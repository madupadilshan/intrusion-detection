#!/usr/bin/env python3
"""
tests/unit/test_response_policy.py - Unit Tests for Response Policy & Safety Guardrails (Step 31).
=================================================================================================

Governing Requirements & Checkpoints:
- Supervisor Checkpoint C7 & Research Question RQ5.
- Group 03 Proposal Table 5 & Section 3.7.
- Unit Tests verification invariants:
  1. Allowlisted IPs are NEVER blocked.
  2. Single high-confidence events do NOT block (require repeats).
  3. Low-confidence events only alert (never block).
  4. Every rule has an explicit bounded expiry duration.
  5. Direction-aware mitigation logic (C&C drops external destination, PortScan drops external source).
"""

import time
import pytest
from unittest.mock import MagicMock

from core_engine.response_policy import (
    ResponsePolicy,
    PolicyDecision,
    is_private_ip,
    REASON_AUTO_PORTSCAN,
    REASON_AUTO_DDOS_BLOCK,
    REASON_AUTO_CNC_DEST_BLOCK,
    REASON_SKIP_BENIGN,
    REASON_SKIP_ALLOWLIST,
    REASON_SKIP_LOW_CONF,
    REASON_SKIP_NOT_REPEATED,
    REASON_SKIP_AUTO_DISABLED,
    REASON_SKIP_PRIVATE_TARGET,
)
from core_engine.decision_engine import DecisionEngine


@pytest.fixture
def policy():
    """Default response policy configured for lab tests."""
    return ResponsePolicy(
        allowlist=["192.168.50.1", "192.168.50.5", "192.168.50.10", "192.168.50.20"],
        min_repeats=3,
        repeat_window_seconds=60,
        max_rule_minutes=45,
        auto_response=True,
    )


def test_private_ip_detection():
    """Verify standard private and public IP classification."""
    assert is_private_ip("192.168.50.10") is True
    assert is_private_ip("10.0.0.1") is True
    assert is_private_ip("172.16.5.4") is True
    assert is_private_ip("127.0.0.1") is True
    assert is_private_ip("8.8.8.8") is False
    assert is_private_ip("198.51.100.25") is False
    assert is_private_ip("") is False


def test_benign_traffic_never_blocked(policy):
    """Safety Invariant: Benign traffic flows are NEVER blocked under any conditions."""
    event = {
        "predicted_class": "Benign",
        "confidence": 0.99,
        "src_ip": "10.10.10.50",
        "dst_ip": "192.168.50.15",
    }
    decision = policy.evaluate(event)
    assert decision.should_act is False
    assert decision.action_type == "none"
    assert decision.reason_code == REASON_SKIP_BENIGN


def test_allowlisted_ip_never_blocked(policy):
    """
    Safety Invariant 1 (Checkpoint C7 & Proposal Section 3.7):
    Management allowlist IPs (192.168.50.1, .5, .10, .20) must NEVER be blocked.
    """
    admin_pc_ip = "192.168.50.10"
    for _ in range(5):  # Simulate repeated high-confidence events
        event = {
            "predicted_class": "DDoS_DoS",
            "confidence": 0.98,
            "src_ip": admin_pc_ip,
            "dst_ip": "192.168.50.20",
        }
        decision = policy.evaluate(event)
        assert decision.should_act is False
        assert decision.reason_code == REASON_SKIP_ALLOWLIST
        assert admin_pc_ip in decision.evidence_note


def test_one_high_confidence_event_does_not_block(policy):
    """
    Safety Invariant 2 (Checkpoint C7):
    A single high-confidence event must NOT trigger an automated block (needs repeats).
    """
    event = {
        "predicted_class": "PortScan",
        "confidence": 0.95,
        "src_ip": "203.0.113.50",
        "dst_ip": "192.168.50.15",
    }
    decision = policy.evaluate(event)
    assert decision.should_act is False
    assert decision.reason_code == REASON_SKIP_NOT_REPEATED
    assert decision.details["current_repeats"] == 1
    assert decision.details["min_repeats"] == 3


def test_repeated_events_trigger_automated_block(policy):
    """
    Proposal Table 5:
    Port scan from outside blocks scanner after repeated probe sweeps.
    """
    attacker_ip = "203.0.113.88"
    base_time = time.time()

    event = {
        "predicted_class": "PortScan",
        "confidence": 0.90,
        "src_ip": attacker_ip,
        "dst_ip": "192.168.50.15",
        "traffic_direction": "inbound",
    }

    # 1st attempt: alerted, not blocked
    d1 = policy.evaluate(event, current_time=base_time)
    assert d1.should_act is False
    assert d1.reason_code == REASON_SKIP_NOT_REPEATED

    # 2nd attempt: alerted, not blocked
    d2 = policy.evaluate(event, current_time=base_time + 5)
    assert d2.should_act is False
    assert d2.reason_code == REASON_SKIP_NOT_REPEATED

    # 3rd attempt: threshold reached -> automated block approved!
    d3 = policy.evaluate(event, current_time=base_time + 10)
    assert d3.should_act is True
    assert d3.action_type == "block"
    assert d3.target_ip == attacker_ip
    assert d3.direction == "inbound"
    assert d3.reason_code == REASON_AUTO_PORTSCAN
    assert d3.duration_minutes == 30  # Requested 30m, clamped to <= 45m max


def test_repeats_outside_window_are_pruned(policy):
    """
    Sliding Window Verification:
    Events that occur outside repeat_window_seconds (60s) must be pruned.
    """
    attacker_ip = "198.51.100.99"
    t0 = 1000.0

    event = {
        "predicted_class": "DDoS_DoS",
        "confidence": 0.92,
        "src_ip": attacker_ip,
        "dst_ip": "192.168.50.15",
    }

    # Event 1 at t=1000s
    policy.evaluate(event, current_time=t0)
    # Event 2 at t=1020s
    policy.evaluate(event, current_time=t0 + 20)
    # Event 3 at t=1070s (t0 has expired since 1070 - 1000 = 70s > 60s)
    d3 = policy.evaluate(event, current_time=t0 + 70)

    # Active count is now 2 (at 1020 and 1070), which is < 3
    assert d3.should_act is False
    assert d3.reason_code == REASON_SKIP_NOT_REPEATED
    assert d3.details["current_repeats"] == 2


def test_low_confidence_event_only_alerts(policy):
    """
    Safety Invariant 3 (Checkpoint C7):
    A low-confidence event must only alert and never block even with repeats.
    """
    attacker_ip = "203.0.113.66"
    for _ in range(5):
        event = {
            "predicted_class": "PortScan",
            "confidence": 0.40,  # Below PortScan active threshold 0.65
            "src_ip": attacker_ip,
            "dst_ip": "192.168.50.15",
        }
        decision = policy.evaluate(event)
        assert decision.should_act is False
        assert decision.reason_code == REASON_SKIP_LOW_CONF


def test_auto_response_disabled_master_switch(policy):
    """
    Master Switch Invariant:
    When auto_response=False, no automated action is ever taken.
    """
    policy.auto_response = False
    for _ in range(5):
        event = {
            "predicted_class": "DDoS_DoS",
            "confidence": 0.95,
            "src_ip": "203.0.113.77",
            "dst_ip": "192.168.50.15",
        }
        decision = policy.evaluate(event)
        assert decision.should_act is False
        assert decision.reason_code == REASON_SKIP_AUTO_DISABLED


def test_private_target_protection(policy):
    """
    Private Target Protection Invariant:
    Inbound attacks cannot block local camera IP unless device isolation is enabled.
    """
    camera_ip = "192.168.50.15"  # Local camera, not in allowlist
    policy.allow_device_isolation = False

    for _ in range(4):
        event = {
            "predicted_class": "PortScan",
            "confidence": 0.95,
            "src_ip": camera_ip,
            "dst_ip": "192.168.50.80",
        }
        decision = policy.evaluate(event)
        assert decision.should_act is False
        assert decision.reason_code == REASON_SKIP_PRIVATE_TARGET


def test_direction_aware_cnc_mitigation(policy):
    """
    Proposal Table 5:
    C&C from camera to outside blocks the external destination IP.
    """
    camera_ip = "192.168.50.15"
    external_cnc_server = "198.51.100.44"

    event = {
        "predicted_class": "CnC",
        "confidence": 0.85,
        "src_ip": camera_ip,
        "dst_ip": external_cnc_server,
        "traffic_direction": "outbound",
    }

    # Simulate 3 repeated beacons
    t = time.time()
    policy.evaluate(event, current_time=t)
    policy.evaluate(event, current_time=t + 5)
    decision = policy.evaluate(event, current_time=t + 10)

    assert decision.should_act is True
    assert decision.action_type == "block"
    assert decision.target_ip == external_cnc_server
    assert decision.direction == "outbound"
    assert decision.reason_code == REASON_AUTO_CNC_DEST_BLOCK


def test_every_rule_has_bounded_expiry(policy):
    """
    Safety Invariant 4:
    Every rule must have a bounded expiry clamped to max_rule_minutes.
    """
    policy.max_rule_minutes = 25  # Limit duration to 25 mins
    event = {
        "predicted_class": "DDoS_DoS",
        "confidence": 0.95,
        "src_ip": "203.0.113.111",
        "dst_ip": "192.168.50.15",
    }

    # Reach 3 repeats
    t = time.time()
    policy.evaluate(event, current_time=t)
    policy.evaluate(event, current_time=t + 1)
    decision = policy.evaluate(event, current_time=t + 2)

    assert decision.should_act is True
    # Requested 60m DDoS duration clamped to 25m max_rule_minutes
    assert decision.duration_minutes == 25


def test_decision_engine_policy_integration():
    """Verify that DecisionEngine exposes evaluate_response() using its policy."""
    engine = DecisionEngine(
        db_service=MagicMock(),
        socketio=MagicMock(),
    )
    outcome_dict = {
        "predicted_class": "Benign",
        "confidence": 0.99,
        "src_ip": "192.168.50.88",
    }
    decision = engine.evaluate_response(outcome_dict)
    assert isinstance(decision, PolicyDecision)
    assert decision.should_act is False
    assert decision.reason_code == REASON_SKIP_BENIGN
