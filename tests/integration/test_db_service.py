"""
Integration tests for DatabaseService using local MongoDB 8.0 instance.
Group 03 - Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks.
Complies with Group 03 Proposal:
- Section 3.6 (Figure 4: 6 Core Collections: devices, attack_events, response_actions, blocklist, system_logs, users)
- Table 7 (FR-01, FR-03, FR-04, FR-05, FR-06, FR-07, FR-08)
- Decision D-011 (TTL Retention Indexes: 90 days attacks/logs/actions, 30 days summaries/scans)
- Decision D-027 (MongoDB 9-collection schema, full block history audit trail, dynamic settings)
"""

import os
import pytest
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

from core_engine.db_service import DatabaseService, DEFAULT_RETENTION_DAYS

TEST_DB_NAME = "iot_ids_test"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")


def is_mongodb_available() -> bool:
    """Check if MongoDB server is responsive on localhost."""
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        client.admin.command("ping")
        client.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not is_mongodb_available(),
    reason="Local MongoDB 8.0 server is not reachable on localhost:27017",
)


@pytest.fixture(scope="function")
def db_service():
    """
    Fixture providing an isolated DatabaseService instance targeting 'iot_ids_test'.
    Cleans up all test collections before and after each test function.
    """
    service = DatabaseService(uri=MONGO_URI, db_name=TEST_DB_NAME)
    assert service.is_connected(), "Failed to connect to test database"
    service.drop_database_for_testing()
    # Re-connect to ensure fresh collections and indexes
    service.connect()
    yield service
    service.drop_database_for_testing()
    service.close()


# =============================================================================
# 1. Schema & Indexes Verification (Proposal Section 3.6 & Decision D-011)
# =============================================================================

def test_database_initialization_and_indexes(db_service):
    """Verify that all 9 collections and required TTL / query indexes are created."""
    assert db_service.is_connected()
    expected_collections = {
        "devices",
        "attack_events",
        "response_actions",
        "blocklist",
        "system_logs",
        "users",
        "traffic_summaries",
        "settings",
        "scans",
    }
    # Insert a dummy record in collections or trigger index creation
    existing_collections = set(db_service.db.list_collection_names())
    for col_name in expected_collections:
        assert getattr(db_service, col_name) is not None

    # Verify TTL indexes exist on specified retention fields
    attack_idx = db_service.attack_events.index_information()
    assert "timestamp_ttl" in attack_idx
    assert attack_idx["timestamp_ttl"]["expireAfterSeconds"] == 90 * 86400

    resp_idx = db_service.response_actions.index_information()
    assert "executed_at_ttl" in resp_idx
    assert resp_idx["executed_at_ttl"]["expireAfterSeconds"] == 90 * 86400

    sys_idx = db_service.system_logs.index_information()
    assert "timestamp_ttl" in sys_idx
    assert sys_idx["timestamp_ttl"]["expireAfterSeconds"] == 90 * 86400

    traffic_idx = db_service.traffic_summaries.index_information()
    assert "minute_ttl" in traffic_idx
    assert traffic_idx["minute_ttl"]["expireAfterSeconds"] == 30 * 86400

    scan_idx = db_service.scans.index_information()
    assert "start_time_ttl" in scan_idx
    assert scan_idx["start_time_ttl"]["expireAfterSeconds"] == 30 * 86400

    # Verify Blocklist index is non-unique compound (ip, status)
    block_idx = db_service.blocklist.index_information()
    compound_found = False
    for name, info in block_idx.items():
        keys = info.get("key", [])
        if keys == [("ip", 1), ("status", 1)]:
            compound_found = True
            assert not info.get("unique", False), "Blocklist compound index must NOT be unique"
    assert compound_found, "Compound (ip, status) index missing from blocklist"


def test_obsolete_unique_blocklist_index_migration(db_service):
    """
    Verify Deficiency Fix #1: If a legacy unique index on blocklist.ip exists,
    _ensure_indexes drops it and replaces it with the non-unique compound index.
    """
    # Simulate legacy state: create unique index on 'ip'
    try:
        db_service.blocklist.drop_indexes()
        db_service.blocklist.create_index([("ip", 1)], name="ip_1", unique=True)
    except Exception:
        pass

    # Run index assurance
    db_service._ensure_indexes()
    info = db_service.blocklist.index_information()
    if "ip_1" in info:
        assert not info["ip_1"].get("unique", False)


# =============================================================================
# 2. Device Operations (Figure 4, FR-05)
# =============================================================================

def test_device_upsert_and_retrieval(db_service):
    """Test inserting and updating discovered devices, including camera identification."""
    dev_camera = {
        "ip": "192.168.50.100",
        "mac": "00:1A:2B:3C:4D:5E",
        "vendor": "TP-Link",
        "device_type": "ip_camera",
        "possible_camera": True,
        "camera_evidence": ["RTSP port 554 open", "ONVIF port 80 open", "OUI TP-Link"],
        "open_ports": [80, 554, 8080],
        "possible_services": ["http", "rtsp", "onvif"],
        "hostname": "camera-lab-01",
    }
    dev_router = {
        "ip": "192.168.50.1",
        "mac": "00:50:56:C0:00:01",
        "vendor": "MikroTik",
        "device_type": "router",
        "possible_camera": False,
        "open_ports": [22, 80, 443],
        "possible_services": ["ssh", "http", "https"],
        "hostname": "gateway",
    }

    assert db_service.upsert_device(dev_camera)
    assert db_service.upsert_device(dev_router)

    # Fetch camera by IP
    cam = db_service.get_device_by_ip("192.168.50.100")
    assert cam is not None
    assert cam["vendor"] == "TP-Link"
    assert cam["possible_camera"] is True
    assert 554 in cam["open_ports"]

    # Filter cameras only
    cameras = db_service.get_devices(camera_only=True)
    assert len(cameras) == 1
    assert cameras[0]["ip"] == "192.168.50.100"

    # All devices
    all_devs = db_service.get_devices(camera_only=False)
    assert len(all_devs) == 2

    # Update status
    assert db_service.update_device_status("192.168.50.100", "offline")
    updated = db_service.get_device_by_ip("192.168.50.100")
    assert updated["status"] == "offline"

    # Validation: empty IP must raise ValueError
    with pytest.raises(ValueError):
        db_service.upsert_device({"mac": "AA:BB:CC"})


# =============================================================================
# 3. Attack Events & Burst Aggregation (Figure 4, FR-01, FR-03, FR-06)
# =============================================================================

def test_attack_event_validation_and_benign_rejection(db_service):
    """
    Verify schema validation:
    - Missing fields rejected with ValueError.
    - Benign flows rejected from attack_events (Deficiency #8 & FR-03).
    """
    # Missing src_ip
    with pytest.raises(ValueError, match="src_ip"):
        db_service.record_attack_event({
            "dst_ip": "192.168.50.100",
            "predicted_class": "DDoS_DoS",
            "confidence": 0.95,
        })

    # Missing confidence
    with pytest.raises(ValueError, match="confidence"):
        db_service.record_attack_event({
            "src_ip": "192.168.50.45",
            "dst_ip": "192.168.50.100",
            "predicted_class": "DDoS_DoS",
        })

    # Confidence out of range
    with pytest.raises(ValueError, match="range"):
        db_service.record_attack_event({
            "src_ip": "192.168.50.45",
            "dst_ip": "192.168.50.100",
            "predicted_class": "DDoS_DoS",
            "confidence": 1.5,
        })

    # Benign flows rejected per Proposal FR-03 & Table 5
    with pytest.raises(ValueError, match="record_traffic_summary"):
        db_service.record_attack_event({
            "src_ip": "192.168.50.100",
            "dst_ip": "192.168.50.20",
            "predicted_class": "Benign",
            "confidence": 0.99,
        })


def test_attack_event_insertion_and_burst_aggregation(db_service):
    """
    Test recording attack events and coalescing repeated flows within
    the aggregation time window (Proposal Section 3.6 Tip 3).
    """
    event_data = {
        "direction": "inbound",
        "src_ip": "10.0.0.99",
        "src_port": 45123,
        "dst_ip": "192.168.50.100",
        "dst_port": 554,
        "proto": "tcp",
        "service": "rtsp",
        "predicted_class": "DDoS_DoS",
        "confidence": 0.92,
        "model_version": "ids_bundle_v1",
        "flow_features": {"duration": 0.05, "orig_bytes": 1024, "resp_bytes": 0},
        "evidence_note": "SYN flood burst against RTSP video stream",
    }

    # First event: creates new incident
    id1 = db_service.record_attack_event(event_data, aggregate_window_seconds=60)
    assert id1 is not None

    # Second repeated flow within window: coalesced into id1
    event_data_repeat = dict(event_data)
    event_data_repeat["confidence"] = 0.96
    id2 = db_service.record_attack_event(event_data_repeat, aggregate_window_seconds=60)
    assert id2 == id1, "Repeated flow inside window must coalesce into original event_id"

    # Verify flow count incremented to 2
    events = db_service.get_attack_events(limit=10)
    assert len(events) == 1
    assert events[0]["flow_count"] == 2
    assert events[0]["confidence"] == 0.96  # Highest confidence preserved

    # Update event status
    assert db_service.update_attack_event_status(id1, status="confirmed", response_status="mitigated")
    updated = db_service.get_attack_events(status_filter="confirmed")
    assert len(updated) == 1
    assert updated[0]["response_status"] == "mitigated"

    # Aggregated stats
    stats = db_service.get_attack_stats()
    assert stats["total_flows"] == 2
    assert stats["total_incidents"] == 1
    assert stats["classes"]["DDoS_DoS"] == 2


# =============================================================================
# 4. Blocklist Full Audit History (Proposal FR-06, FR-07)
# =============================================================================

def test_blocklist_preserves_full_history(db_service):
    """
    Verify Deficiency Fix #1: Adding a block for an IP multiple times
    creates separate audit records rather than overwriting the prior record.
    """
    target_ip = "192.168.50.88"

    # First block: Day 1
    b1_id = db_service.add_to_blocklist(
        ip=target_ip,
        direction="source",
        reason="PortScan detected",
        duration_minutes=30,
        predicted_class="PortScan",
        confidence=0.88,
        actor="system_auto",
    )
    assert b1_id is not None
    assert db_service.is_ip_blocked(target_ip)

    # Admin unblocks
    unblocked_count = db_service.remove_from_blocklist(
        ip=target_ip,
        reason="Investigation concluded - false trigger test",
        actor="admin_alice",
    )
    assert unblocked_count == 1
    assert not db_service.is_ip_blocked(target_ip)

    # Second block: Day 2 (Same IP blocked again for DDoS)
    b2_id = db_service.add_to_blocklist(
        ip=target_ip,
        direction="source",
        reason="DDoS attack detected",
        duration_minutes=60,
        predicted_class="DDoS_DoS",
        confidence=0.97,
        actor="system_auto",
    )
    assert b2_id is not None
    assert b2_id != b1_id
    assert db_service.is_ip_blocked(target_ip)

    # Check complete audit history: BOTH documents exist!
    history = db_service.get_block_history_for_ip(target_ip)
    assert len(history) == 2, "Full block history must contain both records"

    # Verify latest record is active and older record is marked removed
    assert history[0]["block_id"] == b2_id
    assert history[0]["status"] == "active"
    assert history[1]["block_id"] == b1_id
    assert history[1]["status"] == "removed"
    assert history[1]["unblock_actor"] == "admin_alice"


def test_blocklist_automatic_expiration(db_service):
    """Verify that blocks past their expiry time are detected and transitioned to 'expired'."""
    test_ip = "192.168.50.99"
    # Insert block that expired 5 minutes ago
    block_id = db_service.add_to_blocklist(
        ip=test_ip,
        direction="source",
        reason="Test expired block",
        duration_minutes=-5,  # negative duration expires immediately
    )
    assert block_id is not None

    # is_ip_blocked should detect expiration and return False
    assert not db_service.is_ip_blocked(test_ip)

    # Verify document status updated to 'expired'
    history = db_service.get_block_history_for_ip(test_ip)
    assert len(history) == 1
    assert history[0]["status"] == "expired"


# =============================================================================
# 5. Response Actions (Figure 4, FR-06, FR-07)
# =============================================================================

def test_response_action_logging(db_service):
    """Test recording mitigation actions with actor, reason code, and action type."""
    act_data = {
        "event_id": "evt-12345",
        "action": "isolate",
        "target_ip": "192.168.50.100",
        "direction": "both",
        "rule": "nft add element inet filter isolated_hosts { 192.168.50.100 }",
        "reason_code": "COMPROMISED_CAMERA_MIRAI",
        "actor": "system_auto",
        "status": "applied",
        "details": {"oui": "TP-Link", "traffic_rate_pps": 1200},
    }

    action_id = db_service.log_response_action(act_data)
    assert action_id is not None

    actions = db_service.get_response_actions(target_ip="192.168.50.100")
    assert len(actions) == 1
    assert actions[0]["action"] == "isolate"
    assert actions[0]["reason_code"] == "COMPROMISED_CAMERA_MIRAI"

    # Validation: invalid action type
    invalid_act = dict(act_data)
    invalid_act["action"] = "shutdown_power"
    with pytest.raises(ValueError, match="Invalid action"):
        db_service.log_response_action(invalid_act)


# =============================================================================
# 6. System Logs (Figure 4, FR-07, FR-08)
# =============================================================================

def test_system_audit_logging(db_service):
    """Test recording and querying system operational and administrative events."""
    log_id = db_service.log_system_event(
        actor="admin_bob",
        event="CONFIG_UPDATE",
        outcome="SUCCESS",
        details={"setting": "min_confidence", "old": 0.85, "new": 0.88},
    )
    assert log_id is not None

    logs = db_service.get_system_logs(actor="admin_bob")
    assert len(logs) == 1
    assert logs[0]["event"] == "CONFIG_UPDATE"
    assert logs[0]["details"]["new"] == 0.88


# =============================================================================
# 7. Users Management (Figure 4, FR-04, Section 3.6)
# =============================================================================

def test_user_creation_and_auth_tracking(db_service):
    """Test admin user storage and login timestamp updating."""
    # Dummy bcrypt hash
    fake_hash = "$2b$12$e8rGjX7kK91qB5h0vM4gXe4/8yC2lB7z9d0k2m1.0"
    user_id = db_service.create_user("admin", fake_hash, role="admin")
    assert user_id is not None

    user = db_service.get_user_by_username("admin")
    assert user is not None
    assert user["role"] == "admin"
    assert user["last_login"] is None

    # Update login
    assert db_service.update_last_login("admin")
    user_updated = db_service.get_user_by_username("admin")
    assert user_updated["last_login"] is not None

    # Listing users hides password hash
    users_list = db_service.list_users()
    assert len(users_list) == 1
    assert "password_hash" not in users_list[0]


# =============================================================================
# 8. Traffic Summaries (FR-03, Table 5, Section 3.6)
# =============================================================================

def test_traffic_summaries_minute_aggregation(db_service):
    """Test 1-minute aggregation for benign flows per Proposal FR-03."""
    now = datetime.now(timezone.utc)

    # Record 3 flow bursts in the same minute
    assert db_service.record_traffic_summary(now, "Benign", count=10, orig_bytes=5000, resp_bytes=20000, pkts=40)
    assert db_service.record_traffic_summary(now, "Benign", count=15, orig_bytes=7500, resp_bytes=30000, pkts=60)

    summaries = db_service.get_traffic_summaries(class_name="Benign")
    assert len(summaries) == 1
    assert summaries[0]["flow_count"] == 25
    assert summaries[0]["total_orig_bytes"] == 12500
    assert summaries[0]["total_resp_bytes"] == 50000
    assert summaries[0]["total_pkts"] == 100


# =============================================================================
# 9. Settings with Change History (FR-07)
# =============================================================================

def test_settings_audit_history(db_service):
    """Test setting parameters and maintaining complete change history."""
    assert db_service.set_setting("allowlist", ["192.168.50.1", "192.168.50.10"], updated_by="admin", reason="Initial setup")
    val1 = db_service.get_setting("allowlist")
    assert len(val1) == 2

    # Update setting
    assert db_service.set_setting(
        "allowlist",
        ["192.168.50.1", "192.168.50.10", "192.168.50.20"],
        updated_by="admin_alice",
        reason="Added NVR IP",
    )
    val2 = db_service.get_setting("allowlist")
    assert len(val2) == 3

    # Check history
    history = db_service.get_setting_history("allowlist")
    assert len(history) == 2
    assert history[0]["old_value"] is None
    assert history[1]["old_value"] == ["192.168.50.1", "192.168.50.10"]
    assert history[1]["new_value"] == ["192.168.50.1", "192.168.50.10", "192.168.50.20"]
    assert history[1]["updated_by"] == "admin_alice"


# =============================================================================
# 10. Scans Management (FR-05, Section 3.7)
# =============================================================================

def test_scans_tracking(db_service):
    """Test recording discovery scan start and completion."""
    scan_id = db_service.record_scan_start("192.168.50.0/24", started_by="admin")
    assert scan_id is not None

    assert db_service.record_scan_complete(
        scan_id=scan_id,
        status="completed",
        devices_found=4,
        discovered_ips=["192.168.50.1", "192.168.50.10", "192.168.50.20", "192.168.50.100"],
        summary={"scan_duration_sec": 14.2, "nmap_args": "-sS -T4 -O"},
    )

    scans = db_service.get_recent_scans()
    assert len(scans) == 1
    assert scans[0]["status"] == "completed"
    assert scans[0]["devices_found"] == 4
    assert len(scans[0]["discovered_ips"]) == 4

