"""tests/unit/test_auto_response.py - The controlled automatic response (proposal 2.5, 3.4, 3.7; Table 5).

Checks that a block candidate goes through the response policy and reaches the firewall
only when every safety rule passes, and that the lab's "outside" network can be blocked
while local camera-network devices stay protected.
"""

from pathlib import Path

import pytest
import yaml

from core_engine.decision_engine import DecisionEngine, DecisionOutcome
from core_engine.firewall import SimulationAdapter, firewall_config_from_settings
from core_engine.response_policy import REASON_SKIP_PRIVATE_TARGET, ResponsePolicy

THRESHOLDS = {
    "classes": {
        "Benign": {"active_response_threshold": None, "passive_alert_threshold": None},
        "PortScan": {"active_response_threshold": 0.80, "passive_alert_threshold": 0.50, "reason_code": "SCAN_RAPID_PROBE_SWEEP"},
        "DDoS_DoS": {"active_response_threshold": 0.80, "passive_alert_threshold": 0.50, "reason_code": "DOS_HIGH_RATE_PACKET_FLOOD"},
        "CnC": {"active_response_threshold": None, "passive_alert_threshold": 0.50, "reason_code": "CNC_PERSISTENT_BEACON"},
        "Malware_Download": {"active_response_threshold": 0.90, "passive_alert_threshold": 0.50, "reason_code": "MALWARE_STAGING_TRANSFER"},
    }
}


def _engine(tmp_path: Path, auto_response: bool = True) -> DecisionEngine:
    settings = {
        "lab": {"local_networks": ["192.168.50.0/24"]},
        "allowlist": ["192.168.50.1", "192.168.50.5", "192.168.50.10", "192.168.50.20"],
        "response": {"adapter": "simulation", "auto_response": auto_response, "min_repeats": 3,
                     "repeat_window_seconds": 60, "max_rule_minutes": 30},
    }
    path = tmp_path / "settings.yaml"
    path.write_text(yaml.safe_dump(settings), encoding="utf-8")
    fw = SimulationAdapter(allowlist=set(settings["allowlist"]), max_rule_minutes=30)
    return DecisionEngine(db_service=None, socketio=None, thresholds_config=THRESHOLDS,
                          settings_path=path, firewall_adapter=fw)


def _candidate(src="10.10.10.50", dst="192.168.50.30", cls="PortScan", conf=0.95) -> DecisionOutcome:
    return DecisionOutcome(action="ACTIVE_BLOCK_CANDIDATE", predicted_class=cls, confidence=conf,
                           src_ip=src, dst_ip=dst, traffic_direction="inbound", response_status="candidate")


def test_auto_response_off_by_default_means_no_block(tmp_path):
    eng = _engine(tmp_path, auto_response=False)
    for _ in range(5):
        out = _candidate()
        eng.respond_to_outcome(out)
    assert out.response_status == "candidate"
    assert out.response_reason == "SKIP_AUTO_RESPONSE_DISABLED"
    assert eng.firewall.list_active() == []


def test_outside_scanner_blocked_only_after_repeats(tmp_path):
    eng = _engine(tmp_path)
    first, second, third = _candidate(), _candidate(), _candidate()
    eng.respond_to_outcome(first)
    eng.respond_to_outcome(second)
    assert first.response_reason == "SKIP_NOT_REPEATED" and second.response_status == "candidate"
    eng.respond_to_outcome(third)
    assert third.response_status == "blocked"
    active = eng.firewall.list_active()
    assert any(r.get("ip") == "10.10.10.50" for r in active)


def test_same_ip_is_not_blocked_again_while_rule_is_active(tmp_path):
    eng = _engine(tmp_path)
    outs = [_candidate() for _ in range(5)]
    for o in outs:
        eng.respond_to_outcome(o)
    assert outs[2].response_status == "blocked"
    assert outs[3].response_status == "already_blocked"
    eng.forget_block("10.10.10.50")  # manual unblock from the dashboard
    again = _candidate()
    eng.respond_to_outcome(again)
    assert again.response_status == "blocked"


def test_alert_only_class_is_never_blocked(tmp_path):
    eng = _engine(tmp_path)
    for _ in range(5):
        out = _candidate(src="192.168.50.30", dst="10.10.10.50", cls="CnC", conf=0.99)
        eng.respond_to_outcome(out)
    assert out.response_status == "candidate"
    assert out.response_reason == "SKIP_LOW_CONFIDENCE"


def test_allowlisted_admin_is_never_blocked(tmp_path):
    eng = _engine(tmp_path)
    for _ in range(5):
        out = _candidate(src="192.168.50.10")
        eng.respond_to_outcome(out)
    assert out.response_status == "candidate"
    assert out.response_reason == "SKIP_ALLOWLIST"


def test_local_networks_decide_what_is_protected():
    # Without local_networks every private address counts as local (old behaviour)
    p_old = ResponsePolicy(auto_response=True, min_repeats=1)
    d_old = p_old.evaluate({"predicted_class": "PortScan", "confidence": 0.99, "src_ip": "10.10.10.50",
                            "dst_ip": "192.168.50.30"})
    assert d_old.reason_code == REASON_SKIP_PRIVATE_TARGET
    # With the lab's local network, the 10.10.10.0/24 "outside" attacker can be blocked
    p_lab = ResponsePolicy(auto_response=True, min_repeats=1, local_networks=["192.168.50.0/24"])
    d_lab = p_lab.evaluate({"predicted_class": "PortScan", "confidence": 0.99, "src_ip": "10.10.10.50",
                            "dst_ip": "192.168.50.30"})
    assert d_lab.should_act is True and d_lab.target_ip == "10.10.10.50"
    # A local camera is still protected
    d_cam = p_lab.evaluate({"predicted_class": "PortScan", "confidence": 0.99, "src_ip": "192.168.50.30",
                            "dst_ip": "192.168.50.40"})
    assert d_cam.reason_code == REASON_SKIP_PRIVATE_TARGET
    # C&C from a local camera to the outside blocks the outside destination (Table 5)
    d_cnc = p_lab.evaluate({"predicted_class": "CnC", "confidence": 0.99, "src_ip": "192.168.50.30",
                            "dst_ip": "10.10.10.50"})
    assert d_cnc.should_act is True and d_cnc.target_ip == "10.10.10.50" and d_cnc.direction == "outbound"
    # An incoming flow from outside predicted as C&C (first flood or scan flows, issue 43) never
    # blocks the outside source; its destination is a local device, so it is alert only.
    for _ in range(3):
        d_in = p_lab.evaluate({"predicted_class": "CnC", "confidence": 0.99, "src_ip": "10.10.10.50",
                               "dst_ip": "192.168.50.30"})
    assert d_in.should_act is False and d_in.reason_code == REASON_SKIP_PRIVATE_TARGET
    assert d_in.target_ip == "192.168.50.30"


def test_policy_auto_response_default_is_off():
    assert ResponsePolicy().auto_response is False


def test_runtime_settings_are_checked_and_applied(tmp_path):
    eng = _engine(tmp_path)
    applied = eng.apply_runtime_settings({"min_repeats": 5, "min_confidence": 0.9,
                                          "allowlist": ["192.168.50.1", "10.10.10.50"]})
    assert applied["min_repeats"] == 5 and eng.policy.min_repeats == 5
    assert eng.policy.min_confidence_map["PortScan"] == pytest.approx(0.9)       # floor raised 0.80 -> 0.90
    assert eng.policy.min_confidence_map["Malware_Download"] == pytest.approx(0.9)
    assert "10.10.10.50" in eng.policy.allowlist
    with pytest.raises(ValueError):
        DecisionEngine.validate_runtime_setting("min_confidence", 1.5)
    with pytest.raises(ValueError):
        DecisionEngine.validate_runtime_setting("allowlist", ["not-an-ip"])
    with pytest.raises(ValueError):
        DecisionEngine.validate_runtime_setting("min_repeats", 0)


def test_firewall_config_uses_response_adapter():
    cfg = firewall_config_from_settings({"response": {"adapter": "router"}, "firewall": {"type": "nftables"}})
    assert cfg["type"] == "router" and cfg["table_family"] == "inet"
    cfg2 = firewall_config_from_settings({"response": {"adapter": "nftables"}})
    assert cfg2["type"] == "nftables" and cfg2["table_family"] == "bridge"
    cfg3 = firewall_config_from_settings({})
    assert cfg3["type"] == "auto"
