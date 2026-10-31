"""
tests/integration/test_detection_pipeline.py - End-to-End Pipeline Integration Tests (Step 26).
"""

import time
import pytest
from unittest.mock import MagicMock

from core_engine.db_service import DatabaseService
from core_engine.detector import Detector
from core_engine.decision_engine import DecisionEngine


@pytest.fixture(scope="module")
def integration_setup():
    """Setup real test database and pipeline components."""
    db = DatabaseService(db_name="iot_ids_test")
    if not db.connect():
        pytest.skip("MongoDB service not available on localhost:27017")

    # Clean test collections
    db.db.attack_events.delete_many({})
    db.db.traffic_summaries.delete_many({})

    mock_sio = MagicMock()
    detector = Detector()
    engine = DecisionEngine(db_service=db, socketio=mock_sio, detector=detector)

    yield {"db": db, "engine": engine, "sio": mock_sio, "detector": detector}

    # Teardown
    db.db.attack_events.delete_many({})
    db.db.traffic_summaries.delete_many({})
    db.close()


def test_end_to_end_benign_camera_stream(integration_setup):
    """
    Test 1: Legitimate IP Camera RTSP flow.
    Verify flow aggregates into traffic_summaries and does NOT touch attack_events.
    """
    db = integration_setup["db"]
    engine = integration_setup["engine"]
    sio = integration_setup["sio"]
    sio.reset_mock()

    camera_flow = {
        "ts": time.time(),
        "uid": "CCamFlowRTSP",
        "proto": "tcp",
        "service": "rtsp",
        "conn_state": "SF",
        "history": "ShADadFf",
        "id.orig_h": "192.168.50.60",  # IP Camera
        "id.orig_p": 554,
        "id.resp_h": "192.168.50.20",  # NVR
        "id.resp_p": 49160,
        "duration": 5.0,
        "orig_bytes": 500000,
        "resp_bytes": 1200,
        "missed_bytes": 0,
        "orig_pkts": 350,
        "orig_ip_bytes": 514000,
        "resp_pkts": 20,
        "resp_ip_bytes": 1600,
        "traffic_direction": "internal",
        "observed_epoch": time.time(),
    }

    outcomes = engine.process_flows([camera_flow])
    assert len(outcomes) == 1
    out = outcomes[0]

    assert out.action == "BENIGN_SUMMARY"
    assert out.predicted_class == "Benign"

    # MongoDB Invariants:
    # 1. attack_events must remain empty
    assert db.db.attack_events.count_documents({"src_ip": "192.168.50.60"}) == 0

    # 2. traffic_summaries must have recorded the summary
    summary = db.db.traffic_summaries.find_one()
    assert summary is not None
    assert summary["flow_count"] >= 1

    # Socket.IO invariant
    assert sio.emit.called
    emit_event, emit_payload = sio.emit.call_args[0]
    assert emit_event == "traffic_update"
    assert emit_payload["type"] == "benign_flow"
    assert emit_payload["flow_count"] == 1
    assert emit_payload["byte_count"] == 501200
    assert emit_payload["src_ip"] == "192.168.50.60"
    assert emit_payload["dst_ip"] == "192.168.50.20"


def test_end_to_end_portscan_detection(integration_setup):
    """
    Test 2: External PortScan probe.
    Verify alert generation, MongoDB event insertion, and Socket.IO new_event emission.
    """
    db = integration_setup["db"]
    engine = integration_setup["engine"]
    sio = integration_setup["sio"]
    sio.reset_mock()

    scan_probe = {
        "ts": time.time(),
        "uid": "CScanProbe01",
        "proto": "tcp",
        "service": "-",
        "conn_state": "S0",
        "history": "S",
        "id.orig_h": "10.10.10.99",
        "id.orig_p": 59123,
        "id.resp_h": "192.168.50.60",
        "id.resp_p": 23,
        "duration": 0.001,
        "orig_bytes": 0,
        "resp_bytes": 0,
        "missed_bytes": 0,
        "orig_pkts": 1,
        "orig_ip_bytes": 40,
        "resp_pkts": 0,
        "resp_ip_bytes": 0,
        "traffic_direction": "inbound",
        "observed_epoch": time.time(),
    }

    outcomes = engine.process_flows([scan_probe])
    assert len(outcomes) == 1
    out = outcomes[0]

    assert out.predicted_class == "PortScan"
    assert out.action in ("ALERT_ONLY", "ACTIVE_BLOCK_CANDIDATE")
    assert out.event_id is not None

    # Check database persistence
    event_doc = db.db.attack_events.find_one({"src_ip": "10.10.10.99"})
    assert event_doc is not None
    assert event_doc["predicted_class"] == "PortScan"
    assert event_doc["status"] == "prediction"
    assert "timestamps" in event_doc
    assert event_doc["timestamps"]["detect_ts"] > 0

    # Socket.IO emission
    sio.emit.assert_called()
    call_args = sio.emit.call_args_list[0][0]
    assert call_args[0] == "new_event"
    assert call_args[1]["src_ip"] == "10.10.10.99"


def test_end_to_end_burst_coalescing(integration_setup):
    """
    Test 3: Burst Coalescing (Proposal Section 3.6 Tip 3).
    Sending repeated flows within repeat_window_seconds increments flow_count on existing document.
    """
    db = integration_setup["db"]
    engine = integration_setup["engine"]

    target_src = "10.10.10.77"
    target_dst = "192.168.50.60"

    # Send 5 repeated attack flows
    for i in range(5):
        burst_flow = {
            "ts": time.time(),
            "uid": f"CBurst_{i}",
            "proto": "tcp",
            "service": "-",
            "conn_state": "S0",
            "history": "S",
            "id.orig_h": target_src,
            "id.orig_p": 40000 + i,
            "id.resp_h": target_dst,
            "id.resp_p": 80,
            "duration": 0.001,
            "orig_bytes": 0,
            "resp_bytes": 0,
            "missed_bytes": 0,
            "orig_pkts": 1,
            "orig_ip_bytes": 40,
            "resp_pkts": 0,
            "resp_ip_bytes": 0,
            "traffic_direction": "inbound",
            "observed_epoch": time.time(),
        }
        engine.process_flows([burst_flow])

    # Count documents in MongoDB
    docs = list(db.db.attack_events.find({"src_ip": target_src, "dst_ip": target_dst}))

    # MUST be coalesced into exactly 1 document
    assert len(docs) == 1
    assert docs[0]["flow_count"] == 5
    assert "last_seen" in docs[0]


def test_end_to_end_allowlist_protection(integration_setup):
    """
    Test 4: Allowlist Immunity Guardrail (Proposal Section 3.7).
    A scan flow originating from the admin workstation is NEVER marked as candidate for blocking.
    """
    db = integration_setup["db"]
    engine = integration_setup["engine"]

    admin_probe = {
        "ts": time.time(),
        "uid": "CAdminProbe01",
        "proto": "tcp",
        "service": "-",
        "conn_state": "S0",
        "history": "S",
        "id.orig_h": "192.168.50.10",  # Management Allowlist IP
        "id.orig_p": 51234,
        "id.resp_h": "192.168.50.60",
        "id.resp_p": 80,
        "duration": 0.001,
        "orig_bytes": 0,
        "resp_bytes": 0,
        "missed_bytes": 0,
        "orig_pkts": 1,
        "orig_ip_bytes": 40,
        "resp_pkts": 0,
        "resp_ip_bytes": 0,
        "traffic_direction": "internal",
        "observed_epoch": time.time(),
    }

    outcomes = engine.process_flows([admin_probe])
    out = outcomes[0]

    assert out.is_allowlisted is True
    assert out.action == "ALERT_ONLY"
    assert out.response_status == "allowlist_protected"

    # Check MongoDB record
    doc = db.db.attack_events.find_one({"src_ip": "192.168.50.10"})
    assert doc is not None
    assert doc["response_status"] == "allowlist_protected"
