"""
tests/unit/test_decision_engine.py - Unit Tests for Decision Engine (Step 26).
"""

import pytest
import time
from unittest.mock import MagicMock

from core_engine.detector import DetectionResult
from core_engine.decision_engine import DecisionEngine, DecisionOutcome


@pytest.fixture
def mock_db():
    """Fixture providing a mock DatabaseService."""
    db = MagicMock()
    db.record_attack_event.return_value = "mock_event_id_12345"
    db.record_traffic_summary.return_value = True
    return db


@pytest.fixture
def mock_socketio():
    """Fixture providing a mock Flask-SocketIO server."""
    sio = MagicMock()
    return sio


@pytest.fixture
def decision_engine(mock_db, mock_socketio):
    """Fixture providing a configured DecisionEngine with mocks."""
    custom_thresholds = {
        "Benign": {"policy": "ALLOW_ALWAYS"},
        "DDoS_DoS": {
            "active_response_threshold": 0.70,
            "passive_alert_threshold": 0.50,
            "reason_code": "DOS_HIGH_RATE_PACKET_FLOOD",
        },
        "PortScan": {
            "active_response_threshold": 0.65,
            "passive_alert_threshold": 0.30,
            "reason_code": "SCAN_RAPID_PROBE_SWEEP",
        },
        "CnC": {
            "active_response_threshold": 0.60,
            "passive_alert_threshold": 0.25,
            "reason_code": "CNC_PERSISTENT_BEACON",
        },
        "Malware_Download": {
            "active_response_threshold": 0.85,
            "passive_alert_threshold": 0.50,
            "reason_code": "MALWARE_STAGING_TRANSFER",
        },
    }

    engine = DecisionEngine(
        db_service=mock_db,
        socketio=mock_socketio,
        thresholds_config=custom_thresholds,
    )
    return engine


def test_benign_flow_updates_traffic_summary_only(decision_engine, mock_db, mock_socketio):
    """
    FR-03 & Table 5 Requirement:
    Benign flows must NEVER be inserted into attack_events; they update traffic_summaries only.
    """
    detection = DetectionResult(
        flow_id="benign_01",
        predicted_class="Benign",
        predicted_class_idx=0,
        confidence=0.985,
        probabilities={"Benign": 0.985, "DDoS_DoS": 0.005, "PortScan": 0.005, "CnC": 0.003, "Malware_Download": 0.002},
        raw_flow={
            "id.orig_h": "192.168.50.88",
            "id.orig_p": 49152,
            "id.resp_h": "192.168.50.10",
            "id.resp_p": 80,
            "orig_bytes": 100,
            "resp_bytes": 400,
            "proto": "tcp",
            "service": "http",
            "conn_state": "SF",
            "observed_epoch": time.time(),
        },
    )

    outcome = decision_engine.evaluate_detection(detection)

    assert outcome.action == "BENIGN_SUMMARY"
    assert outcome.predicted_class == "Benign"
    assert outcome.response_status == "none"
    assert outcome.severity == "info"

    # Must NOT record attack event
    mock_db.record_attack_event.assert_not_called()

    # Must update traffic summary with byte counts
    mock_db.record_traffic_summary.assert_called_once()
    call_kwargs = mock_db.record_traffic_summary.call_args[1]
    assert call_kwargs["class_name"] == "Benign"
    assert call_kwargs["count"] == 1
    assert call_kwargs["orig_bytes"] == 100
    assert call_kwargs["resp_bytes"] == 400

    # Must emit traffic_update over Socket.IO
    mock_socketio.emit.assert_called_once()
    call_args = mock_socketio.emit.call_args
    assert call_args[0][0] == "traffic_update"
    assert call_args[0][1]["type"] == "benign_flow"


def test_attack_flow_below_alert_threshold_ignored(decision_engine, mock_db, mock_socketio):
    """Verify attack flow with confidence below passive alert threshold is ignored as noise."""
    detection = DetectionResult(
        flow_id="noise_01",
        predicted_class="PortScan",
        confidence=0.20,  # Below 0.30 alert threshold
        raw_flow={
            "id.orig_h": "10.10.10.99",
            "id.resp_h": "192.168.50.15",
            "observed_epoch": time.time(),
        },
    )

    outcome = decision_engine.evaluate_detection(detection)

    assert outcome.action == "LOW_CONFIDENCE_IGNORE"
    assert outcome.response_status == "none"
    mock_db.record_attack_event.assert_not_called()
    mock_socketio.emit.assert_not_called()


def test_attack_flow_moderate_confidence_alert_only(decision_engine, mock_db, mock_socketio):
    """
    Verify attack flow with confidence between alert and block thresholds
    triggers ALERT_ONLY (no active firewall block candidate).
    """
    detection = DetectionResult(
        flow_id="alert_01",
        predicted_class="PortScan",
        confidence=0.45,  # 0.30 <= 0.45 < 0.65 -> ALERT_ONLY
        probabilities={"PortScan": 0.45, "Benign": 0.35, "DDoS_DoS": 0.10, "CnC": 0.05, "Malware_Download": 0.05},
        model_version="v1.0.0",
        raw_flow={
            "id.orig_h": "10.10.10.99",
            "id.orig_p": 55432,
            "id.resp_h": "192.168.50.15",
            "id.resp_p": 23,
            "proto": "tcp",
            "conn_state": "S0",
            "observed_epoch": time.time(),
        },
        features={"conn_state": "S0", "resp_pkts": 0, "duration": 0.001},
    )

    outcome = decision_engine.evaluate_detection(detection)

    assert outcome.action == "ALERT_ONLY"
    assert outcome.response_status == "none"
    assert outcome.reason_code == "SCAN_RAPID_PROBE_SWEEP"
    assert outcome.event_id == "mock_event_id_12345"

    mock_db.record_attack_event.assert_called_once()
    event_arg = mock_db.record_attack_event.call_args[0][0]
    assert event_arg["predicted_class"] == "PortScan"
    assert event_arg["response_status"] == "none"
    assert event_arg["status"] == "prediction"

    mock_socketio.emit.assert_called_once()
    emit_event, emit_payload = mock_socketio.emit.call_args[0]
    assert emit_event == "new_event"
    assert emit_payload["predicted_class"] == "PortScan"


def test_attack_flow_high_confidence_block_candidate(decision_engine, mock_db, mock_socketio):
    """
    Verify attack flow with confidence >= active response threshold
    becomes ACTIVE_BLOCK_CANDIDATE with response_status='candidate'.
    """
    detection = DetectionResult(
        flow_id="block_candidate_01",
        predicted_class="DDoS_DoS",
        confidence=0.95,  # 0.95 >= 0.70 -> ACTIVE_BLOCK_CANDIDATE
        probabilities={"DDoS_DoS": 0.95, "Benign": 0.02, "PortScan": 0.01, "CnC": 0.01, "Malware_Download": 0.01},
        model_version="v1.0.0",
        raw_flow={
            "id.orig_h": "10.10.10.88",
            "id.orig_p": 44444,
            "id.resp_h": "192.168.50.20",
            "id.resp_p": 80,
            "proto": "tcp",
            "orig_pkts": 500,
            "orig_bytes": 25000,
            "observed_epoch": time.time(),
        },
        features={"orig_pkts": 500, "orig_bytes": 25000, "pkt_ratio": 0.01},
    )

    outcome = decision_engine.evaluate_detection(detection)

    assert outcome.action == "ACTIVE_BLOCK_CANDIDATE"
    assert outcome.response_status == "candidate"
    assert outcome.severity == "critical"
    assert outcome.reason_code == "DOS_HIGH_RATE_PACKET_FLOOD"
    assert outcome.is_allowlisted is False

    mock_db.record_attack_event.assert_called_once()
    event_arg = mock_db.record_attack_event.call_args[0][0]
    assert event_arg["response_status"] == "candidate"


def test_allowlist_protected_ip_never_blocked(decision_engine, mock_db, mock_socketio):
    """
    Proposal Section 3.7 Lab Safety Guardrail:
    Management Allowlist IPs (192.168.50.1, .5, .10, .20) must NEVER be candidates for blocking.
    """
    detection = DetectionResult(
        flow_id="admin_pc_flow",
        predicted_class="DDoS_DoS",
        confidence=0.99,  # Extremely high confidence, but on allowlisted admin PC
        probabilities={"DDoS_DoS": 0.99, "Benign": 0.01},
        raw_flow={
            "id.orig_h": "192.168.50.10",  # Admin workstation in allowlist
            "id.orig_p": 12345,
            "id.resp_h": "192.168.50.20",
            "id.resp_p": 80,
            "proto": "tcp",
            "observed_epoch": time.time(),
        },
    )

    outcome = decision_engine.evaluate_detection(detection)

    # Must be downgraded to ALERT_ONLY with allowlist_protected response status
    assert outcome.is_allowlisted is True
    assert outcome.action == "ALERT_ONLY"
    assert outcome.response_status == "allowlist_protected"
    assert "[ALLOWLIST PROTECTED]" in outcome.evidence_note

    event_arg = mock_db.record_attack_event.call_args[0][0]
    assert event_arg["response_status"] == "allowlist_protected"


def test_end_to_end_latency_tracking(decision_engine):
    """
    Hypothesis H1 Clause 3 Requirement:
    Verify timestamps at all stages are tracked (zeek_ts, adapter_ts, detect_ts, decision_ts, db_ts, emit_ts).
    """
    detection = DetectionResult(
        flow_id="latency_flow",
        predicted_class="CnC",
        confidence=0.85,
        raw_flow={
            "ts": 1700000000.0,
            "id.orig_h": "192.168.50.60",
            "id.resp_h": "203.0.113.5",
            "id.resp_p": 8080,
            "observed_epoch": time.time() - 0.05,  # simulated 50ms ago
        },
        detect_ts=time.time() - 0.02,
    )

    outcome = decision_engine.evaluate_detection(detection)

    ts = outcome.timestamps
    assert "zeek_ts" in ts
    assert "adapter_ts" in ts
    assert "detect_ts" in ts
    assert "decision_ts" in ts
    assert "db_ts" in ts
    assert "emit_ts" in ts

    # Pipeline latency must be positive and reasonable
    assert outcome.pipeline_latency_ms >= 0.0


def test_evidence_note_generation(decision_engine):
    """Verify evidence note generation across all distinct attack classes (FR-02)."""
    classes = ["DDoS_DoS", "PortScan", "CnC", "Malware_Download", "Benign"]

    for cls in classes:
        det = DetectionResult(
            predicted_class=cls,
            confidence=0.92,
            raw_flow={"id.resp_h": "192.168.50.15", "id.resp_p": 80, "service": "http"},
            features={"orig_pkts": 50, "orig_bytes": 2000, "resp_bytes": 10000, "conn_state": "SF"},
        )
        note = decision_engine.generate_evidence_note(det)
        assert isinstance(note, str)
        assert len(note) > 10
        if cls != "Benign":
            assert "92.0%" in note


def test_process_flows_batch(decision_engine, mock_db):
    """Verify processing a heterogeneous batch of flows through the complete engine."""
    mock_detector = MagicMock()
    mock_detector.detect_flows.return_value = [
        DetectionResult(predicted_class="Benign", confidence=0.99, raw_flow={"id.orig_h": "192.168.50.88", "id.resp_h": "192.168.50.10"}),
        DetectionResult(predicted_class="PortScan", confidence=0.60, raw_flow={"id.orig_h": "10.10.10.50", "id.resp_h": "192.168.50.15"}),
        DetectionResult(predicted_class="DDoS_DoS", confidence=0.90, raw_flow={"id.orig_h": "10.10.10.77", "id.resp_h": "192.168.50.20"}),
    ]

    decision_engine.detector = mock_detector
    raw_flows = [{"flow": 1}, {"flow": 2}, {"flow": 3}]

    outcomes = decision_engine.process_flows(raw_flows)

    assert len(outcomes) == 3
    assert outcomes[0].action == "BENIGN_SUMMARY"
    assert outcomes[1].action == "ALERT_ONLY"
    assert outcomes[2].action == "ACTIVE_BLOCK_CANDIDATE"


def _cnc_detection(src, dst):
    return DetectionResult(
        predicted_class="CnC",
        confidence=0.62,
        probabilities={"CnC": 0.62, "Benign": 0.35, "PortScan": 0.02, "DDoS_DoS": 0.005, "Malware_Download": 0.005},
        raw_flow={"id.orig_h": src, "id.orig_p": 40000, "id.resp_h": dst, "id.resp_p": 554,
                  "proto": "tcp", "conn_state": "S0", "orig_pkts": 1, "resp_pkts": 0,
                  "observed_epoch": time.time()},
    )


def test_inbound_cnc_is_relabelled_portscan(decision_engine):
    """Direction-aware rule (Table 5): a CnC prediction on an INBOUND flow (outside -> local) is a
    scan probe, not a C&C beacon, so it is shown as PortScan. The raw model class is kept for audit."""
    import ipaddress
    decision_engine.policy.local_networks = [ipaddress.ip_network("192.168.50.0/24")]

    # inbound: outside attacker -> local camera
    outcome = decision_engine.evaluate_detection(_cnc_detection("10.10.10.50", "192.168.50.30"))
    assert outcome.predicted_class == "PortScan"

    # outbound: local camera -> outside C&C server stays CnC (real C&C unchanged)
    outcome2 = decision_engine.evaluate_detection(_cnc_detection("192.168.50.30", "10.10.10.50"))
    assert outcome2.predicted_class == "CnC"


def _scan_detection(src, dst, confidence, udst=0.0, uport=0.0, nconn=1.0):
    """An inbound low-confidence flow the model calls CnC (relabelled PortScan by direction),
    carrying the 60 s window fan-out features a scan produces."""
    return DetectionResult(
        predicted_class="CnC",
        confidence=confidence,
        probabilities={"CnC": confidence, "Benign": 1 - confidence, "PortScan": 0.0,
                       "DDoS_DoS": 0.0, "Malware_Download": 0.0},
        raw_flow={"id.orig_h": src, "id.orig_p": 40000, "id.resp_h": dst, "id.resp_p": 23,
                  "proto": "tcp", "conn_state": "S0", "orig_pkts": 1, "resp_pkts": 0,
                  "observed_epoch": time.time()},
        features={"conn_state": "S0", "resp_pkts": 0, "duration": 0.001,
                  "src_udst_60s": udst, "src_uport_60s": uport, "src_conn_60s": nconn},
    )


def test_fanout_portscan_blocks_despite_low_confidence(decision_engine, mock_db):
    """Behaviour-based scan block: a low-confidence (0.42) inbound scan that fans out to many
    hosts in 60 s becomes a block candidate even though the model confidence is far below the
    PortScan block threshold. The lab nmap sweep (Challenges 38, 46) is caught this way."""
    import ipaddress
    decision_engine.policy.local_networks = [ipaddress.ip_network("192.168.50.0/24")]

    outcome = decision_engine.evaluate_detection(
        _scan_detection("10.10.10.50", "192.168.50.30", confidence=0.42, udst=40, uport=3, nconn=40)
    )
    assert outcome.predicted_class == "PortScan"
    assert outcome.scan_confirmed is True
    assert outcome.action == "ACTIVE_BLOCK_CANDIDATE"
    assert outcome.response_status == "candidate"
    event_arg = mock_db.record_attack_event.call_args[0][0]
    assert event_arg["scan_confirmed"] is True
    assert "fan-out confirmed" in outcome.evidence_note


def test_low_confidence_portscan_without_fanout_stays_alert(decision_engine):
    """Safety: the same low confidence with NO fan-out (one host, one port) must NOT auto-block;
    it only alerts. This keeps a single stray probe from ever blocking on its own."""
    import ipaddress
    decision_engine.policy.local_networks = [ipaddress.ip_network("192.168.50.0/24")]

    outcome = decision_engine.evaluate_detection(
        _scan_detection("10.10.10.50", "192.168.50.30", confidence=0.42, udst=1, uport=1, nconn=1)
    )
    assert outcome.predicted_class == "PortScan"
    assert outcome.scan_confirmed is False
    assert outcome.action == "ALERT_ONLY"
    assert outcome.response_status == "none"


def test_policy_confidence_check_bypassed_only_for_confirmed_scan(decision_engine):
    """ResponsePolicy Safety Check 2: a confirmed PortScan is exempt from the confidence floor;
    an unconfirmed one at the same confidence is still rejected as low-confidence."""
    from core_engine.response_policy import REASON_SKIP_LOW_CONF
    decision_engine.policy.auto_response = True  # reach Safety Check 2 (master switch is Check 1)
    base = {
        "predicted_class": "PortScan", "confidence": 0.42,
        "src_ip": "10.10.10.50", "dst_ip": "192.168.50.30", "traffic_direction": "inbound",
    }
    rejected = decision_engine.policy.evaluate({**base, "scan_confirmed": False})
    assert rejected.reason_code == REASON_SKIP_LOW_CONF

    passed = decision_engine.policy.evaluate({**base, "scan_confirmed": True})
    assert passed.reason_code != REASON_SKIP_LOW_CONF
