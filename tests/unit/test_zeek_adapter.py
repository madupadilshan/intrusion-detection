"""tests/unit/test_zeek_adapter.py - Unit Tests for Zeek Adapter & Telemetry Pipeline.

Governing Standards:
- Proposal: Section 3.5, Figure 3, Table 7 (FR-01)
- Step-by-Step Guide: Step 21 (Build the Zeek adapter)
- Decision Log: D-025

Test Coverage:
1. Direction classification across internal, outbound, inbound, and external CIDR flows.
2. Device inventory tagging for IP cameras, NVRs, and infrastructure.
3. Incomplete flow detection for scan and flood telemetry.
4. Schema normalization and metadata enrichment from JSON records.
5. Micro-batching dynamics (batch_size vs batch_timeout triggers).
6. File offset persistence and crash recovery (Step 38).
7. Cross-platform log rotation and truncation detection.
8. Malformed/corrupted JSON fault tolerance.
9. Feature matrix extraction compatibility with 19 locked features and 0 NaNs.
"""

from __future__ import annotations

import json
from pathlib import Path
import threading
import time
from typing import Any, Dict, List

import numpy as np
import pandas as pd
import pytest

from core_engine.zeek_adapter import (
    AdapterMetrics,
    DeviceTagger,
    DirectionClassifier,
    NetworkDirection,
    StateStore,
    ZeekAdapter,
    ZeekLogFollower,
    is_incomplete_flow,
)
from ml_engine.features import FEATURE_COLUMNS, make_features


@pytest.fixture
def sample_flow_dict() -> Dict[str, Any]:
    """Sample raw Zeek conn.log JSON record."""
    return {
        "ts": 1793465084.308,
        "uid": "CTestFlowUid01",
        "id.orig_h": "192.168.50.101",
        "id.orig_p": 554,
        "id.resp_h": "192.168.50.200",
        "id.resp_p": 51234,
        "proto": "tcp",
        "service": "rtsp",
        "duration": 12.5,
        "orig_bytes": 10240,
        "resp_bytes": 1048576,
        "conn_state": "SF",
        "local_orig": True,
        "local_resp": True,
        "missed_bytes": 0,
        "history": "ShADadFf",
        "orig_pkts": 120,
        "orig_ip_bytes": 15000,
        "resp_pkts": 850,
        "resp_ip_bytes": 1080000,
    }


def test_direction_classifier():
    """Verify flow direction classification against configured subnets."""
    classifier = DirectionClassifier(["192.168.50.0/24", "10.0.0.0/8"])

    # Internal: both endpoints in local subnets
    assert classifier.classify("192.168.50.101", "192.168.50.200") == NetworkDirection.INTERNAL
    assert classifier.classify("192.168.50.10", "10.1.2.3") == NetworkDirection.INTERNAL

    # Outbound: source local, destination public
    assert classifier.classify("192.168.50.101", "8.8.8.8") == NetworkDirection.OUTBOUND
    assert classifier.classify("10.0.1.5", "1.1.1.1") == NetworkDirection.OUTBOUND

    # Inbound: source public, destination local
    assert classifier.classify("45.33.32.156", "192.168.50.101") == NetworkDirection.INBOUND

    # External: both endpoints public
    assert classifier.classify("1.1.1.1", "8.8.8.8") == NetworkDirection.EXTERNAL

    # Edge cases: invalid or missing IPs
    assert classifier.classify("-", "unknown") == NetworkDirection.EXTERNAL
    assert classifier.classify(None, "192.168.50.101") == NetworkDirection.INBOUND
    assert classifier.classify("invalid_ip", None) == NetworkDirection.EXTERNAL


def test_device_tagger():
    """Verify device tagging attribution."""
    tagger = DeviceTagger(
        {
            "192.168.50.101": {
                "device_id": "cam_01",
                "name": "Tapo C200",
                "type": "ip_camera",
            }
        }
    )

    # Source match
    tag_src = tagger.tag("192.168.50.101", "8.8.8.8")
    assert tag_src is not None
    assert tag_src["device_id"] == "cam_01"
    assert tag_src["direction_role"] == "source"
    assert tag_src["type"] == "ip_camera"

    # Destination match
    tag_dst = tagger.tag("8.8.8.8", "192.168.50.101")
    assert tag_dst is not None
    assert tag_dst["direction_role"] == "destination"

    # Unknown IP
    assert tagger.tag("8.8.8.8", "1.1.1.1") is None


def test_is_incomplete_flow():
    """Verify incomplete connection detection for port scans and flood telemetry."""
    # SYN without ACK
    assert is_incomplete_flow({"conn_state": "S0", "resp_pkts": 0}) is True
    # Connection rejected
    assert is_incomplete_flow({"conn_state": "REJ", "resp_pkts": 1}) is True
    # Reset before SYN-ACK
    assert is_incomplete_flow({"conn_state": "RSTOS0", "resp_pkts": 0}) is True
    # Zero responses
    assert is_incomplete_flow({"conn_state": "OTH", "resp_pkts": 0}) is True
    # Zero payload and zero duration
    assert is_incomplete_flow({"conn_state": "OTH", "duration": 0.0, "orig_bytes": 0, "resp_bytes": 0, "resp_pkts": 1}) is True

    # Complete established session
    assert is_incomplete_flow({"conn_state": "SF", "duration": 5.2, "orig_bytes": 500, "resp_bytes": 1500, "resp_pkts": 10}) is False


def test_parse_and_enrich(sample_flow_dict):
    """Verify parsing and telemetry enrichment of raw JSON lines."""
    adapter = ZeekAdapter(
        local_networks=["192.168.50.0/24"],
        batch_size=10,
        enable_state_persistence=False,
    )

    # 1. Normal flat JSON
    line = json.dumps(sample_flow_dict)
    enriched = adapter.parse_and_enrich(line)
    assert enriched is not None
    assert enriched["traffic_direction"] == "internal"
    assert "observed_at" in enriched
    assert enriched["is_incomplete"] is False
    assert enriched["device_tag"] is not None
    assert enriched["device_tag"]["type"] in ("ip_camera", "nvr")

    # 2. Nested JSON structure: {"id": {"orig_h": ...}}
    nested_flow = dict(sample_flow_dict)
    del nested_flow["id.orig_h"]
    del nested_flow["id.orig_p"]
    del nested_flow["id.resp_h"]
    del nested_flow["id.resp_p"]
    nested_flow["id"] = {
        "orig_h": "192.168.50.101",
        "orig_p": 554,
        "resp_h": "8.8.8.8",
        "resp_p": 53,
    }
    enriched_nested = adapter.parse_and_enrich(json.dumps(nested_flow))
    assert enriched_nested is not None
    assert enriched_nested["id.orig_h"] == "192.168.50.101"
    assert enriched_nested["traffic_direction"] == "outbound"

    # 3. Corrupted / malformed JSON
    assert adapter.parse_and_enrich("{bad json line") is None
    assert adapter.parse_and_enrich("") is None
    assert adapter.get_metrics()["flows_corrupted"] == 1


def test_static_read_and_feature_extraction(tmp_path, sample_flow_dict):
    """Verify reading static conn.log files and extracting standard 19 features."""
    log_file = tmp_path / "conn.log"
    # Write 5 test lines
    records = []
    for i in range(5):
        rec = dict(sample_flow_dict)
        rec["uid"] = f"flow_{i}"
        rec["duration"] = 1.0 + i
        records.append(rec)

    with open(log_file, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")

    adapter = ZeekAdapter(conn_log_path=log_file, enable_state_persistence=False)
    flows = adapter.read_file()
    assert len(flows) == 5

    # Feature extraction
    feat_df = adapter.to_feature_dataframe(flows)
    assert isinstance(feat_df, pd.DataFrame)
    assert feat_df.shape == (5, 19)
    assert list(feat_df.columns) == FEATURE_COLUMNS
    assert feat_df.isna().sum().sum() == 0


def test_micro_batching_by_size(tmp_path, sample_flow_dict):
    """Verify micro-batches trigger promptly when batch_size threshold is reached."""
    log_file = tmp_path / "conn.log"
    log_file.touch()

    adapter = ZeekAdapter(
        conn_log_path=log_file,
        batch_size=3,
        batch_timeout=5.0,  # long timeout so size triggers first
        enable_state_persistence=False,
    )

    stop_ev = threading.Event()
    collected_batches: List[List[Dict[str, Any]]] = []

    def consumer():
        for b in adapter.tail_batches(seek_end=False, stop_event=stop_ev):
            collected_batches.append(b)
            if len(collected_batches) >= 2:
                stop_ev.set()
                break

    t = threading.Thread(target=consumer, daemon=True)
    t.start()

    time.sleep(0.05)
    # Write 6 lines in chunks
    with open(log_file, "a", encoding="utf-8") as f:
        for i in range(3):
            rec = dict(sample_flow_dict)
            rec["uid"] = f"batch1_{i}"
            f.write(json.dumps(rec) + "\n")
        f.flush()

    time.sleep(0.1)
    with open(log_file, "a", encoding="utf-8") as f:
        for i in range(3):
            rec = dict(sample_flow_dict)
            rec["uid"] = f"batch2_{i}"
            f.write(json.dumps(rec) + "\n")
        f.flush()

    t.join(timeout=3.0)
    stop_ev.set()

    assert len(collected_batches) == 2
    assert len(collected_batches[0]) == 3
    assert len(collected_batches[1]) == 3


def test_micro_batching_by_timeout(tmp_path, sample_flow_dict):
    """Verify micro-batches trigger on timeout when traffic rate is low."""
    log_file = tmp_path / "conn.log"
    log_file.touch()

    adapter = ZeekAdapter(
        conn_log_path=log_file,
        batch_size=50,  # large size so timeout triggers first
        batch_timeout=0.15,
        enable_state_persistence=False,
    )

    stop_ev = threading.Event()
    collected_batches: List[List[Dict[str, Any]]] = []

    def consumer():
        for b in adapter.tail_batches(seek_end=False, stop_event=stop_ev):
            collected_batches.append(b)
            stop_ev.set()
            break

    t = threading.Thread(target=consumer, daemon=True)
    t.start()

    time.sleep(0.05)
    # Write only 2 lines (less than batch_size of 50)
    with open(log_file, "a", encoding="utf-8") as f:
        for i in range(2):
            f.write(json.dumps(sample_flow_dict) + "\n")
        f.flush()

    t.join(timeout=3.0)
    stop_ev.set()

    assert len(collected_batches) == 1
    assert len(collected_batches[0]) == 2


def test_state_persistence_and_recovery(tmp_path, sample_flow_dict):
    """Verify offset state persistence across adapter stop and restart (Step 38)."""
    log_file = tmp_path / "conn.log"
    state_file = tmp_path / ".zeek_state.json"

    # Step 1: Write 4 records
    with open(log_file, "w", encoding="utf-8") as f:
        for i in range(4):
            rec = dict(sample_flow_dict)
            rec["uid"] = f"initial_{i}"
            f.write(json.dumps(rec) + "\n")

    # Step 2: Read with state persistence
    adapter1 = ZeekAdapter(
        conn_log_path=log_file,
        state_path=state_file,
        batch_size=4,
        enable_state_persistence=True,
    )

    stop_ev1 = threading.Event()
    batches1 = []
    for b in adapter1.tail_batches(seek_end=False, stop_event=stop_ev1):
        batches1.append(b)
        stop_ev1.set()
        break

    assert len(batches1) == 1
    assert len(batches1[0]) == 4
    assert state_file.exists()

    # Step 3: Append 3 more records while adapter is offline
    with open(log_file, "a", encoding="utf-8") as f:
        for i in range(3):
            rec = dict(sample_flow_dict)
            rec["uid"] = f"appended_{i}"
            f.write(json.dumps(rec) + "\n")

    # Step 4: Restart adapter with saved state
    adapter2 = ZeekAdapter(
        conn_log_path=log_file,
        state_path=state_file,
        batch_size=3,
        enable_state_persistence=True,
    )

    stop_ev2 = threading.Event()
    batches2 = []
    for b in adapter2.tail_batches(seek_end=False, stop_event=stop_ev2):
        batches2.append(b)
        stop_ev2.set()
        break

    assert len(batches2) == 1
    assert len(batches2[0]) == 3
    # Check that only new flows were read, zero duplicate initial flows
    assert batches2[0][0]["uid"] == "appended_0"
    assert batches2[0][2]["uid"] == "appended_2"


def test_log_rotation_handling(tmp_path, sample_flow_dict):
    """Verify log rotation and truncation recovery without crashes or data loss."""
    log_file = tmp_path / "conn.log"
    log_file.touch()

    adapter = ZeekAdapter(
        conn_log_path=log_file,
        batch_size=2,
        batch_timeout=0.2,
        enable_state_persistence=False,
    )

    stop_ev = threading.Event()
    collected_flows: List[str] = []

    def consumer():
        for flow in adapter.tail_flows(seek_end=False, stop_event=stop_ev):
            collected_flows.append(flow["uid"])
            if len(collected_flows) >= 4:
                stop_ev.set()
                break

    t = threading.Thread(target=consumer, daemon=True)
    t.start()

    time.sleep(0.05)
    # Write first 2 records
    with open(log_file, "a", encoding="utf-8") as f:
        for i in range(2):
            rec = dict(sample_flow_dict)
            rec["uid"] = f"pre_rotation_{i}"
            f.write(json.dumps(rec) + "\n")
        f.flush()

    time.sleep(0.1)
    # Simulate log rotation / truncation: truncate file to 0 bytes
    with open(log_file, "r+", encoding="utf-8") as f:
        f.truncate(0)
    time.sleep(0.15)  # Allow follower to observe truncated size (0 < current_offset)
    with open(log_file, "a", encoding="utf-8") as f:
        for i in range(2):
            rec = dict(sample_flow_dict)
            rec["uid"] = f"post_rotation_{i}"
            f.write(json.dumps(rec) + "\n")
        f.flush()

    t.join(timeout=4.0)
    stop_ev.set()

    assert len(collected_flows) == 4
    assert collected_flows[:2] == ["pre_rotation_0", "pre_rotation_1"]
    assert collected_flows[2:] == ["post_rotation_0", "post_rotation_1"]
