"""
Integration tests for Flask + Socket.IO Unified Backend Server.
Group 03 - Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks.
Complies with Group 03 Proposal:
- Section 3.6 (Figure 2: Unified Backend on Port 5000)
- Table 7 (FR-01, FR-03, FR-04: Live Socket.IO Telemetry, FR-05, FR-06, FR-07, FR-08: Log Export)
- Decision D-029 (Consolidated Flask + Socket.IO server, RBAC, authenticated WebSocket streams)
"""

import os
import json
import pytest
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

from core_engine.app import create_app
from core_engine.db_service import DatabaseService
from core_engine.auth import AuthManager

TEST_DB_NAME = "iot_ids_test"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
TEST_JWT_SECRET = "test_super_secret_jwt_key_2026_flask_app_test"


def is_mongodb_available() -> bool:
    try:
        c = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        c.admin.command("ping")
        c.close()
        return True
    except Exception:
        return False


pytestmark = pytest.mark.skipif(
    not is_mongodb_available(),
    reason="Local MongoDB 8.0 server is not reachable on localhost:27017",
)


@pytest.fixture(scope="function")
def test_setup():
    """
    Sets up an isolated DatabaseService, AuthManager, Flask app, and SocketIO instance
    targeting the test database 'iot_ids_test'.
    """
    db = DatabaseService(uri=MONGO_URI, db_name=TEST_DB_NAME)
    db.drop_database_for_testing()
    db.connect()

    auth = AuthManager(db_service=db, secret_key=TEST_JWT_SECRET, token_expiry_hours=8)
    app, socketio = create_app(
        db_service=db,
        auth_manager=auth,
        test_config={"TESTING": True},
    )

    # Seed test users
    admin_pw_hash = AuthManager.hash_password("AdminPass1234!")
    op_pw_hash = AuthManager.hash_password("OperatorPass1234!")
    db.create_user("admin_user", admin_pw_hash, role="admin")
    db.create_user("operator_user", op_pw_hash, role="operator")

    admin_token = auth.create_token(username="admin_user", role="admin")
    operator_token = auth.create_token(username="operator_user", role="operator")

    client = app.test_client()

    yield {
        "db": db,
        "auth": auth,
        "app": app,
        "socketio": socketio,
        "client": client,
        "admin_token": admin_token,
        "operator_token": operator_token,
    }

    db.drop_database_for_testing()
    db.close()


# =============================================================================
# 1. Health & Public Endpoints
# =============================================================================

def test_health_check_endpoint(test_setup):
    """Verify /api/health returns 200 with online subsystem indicators."""
    client = test_setup["client"]
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "healthy"
    assert data["subsystems"]["mongodb"] == "online"
    assert data["subsystems"]["auth_engine"] == "active"


def test_auth_login_success_and_failure(test_setup):
    """Verify POST /api/auth/login validates credentials and issues JWT token."""
    client = test_setup["client"]

    # Success
    resp_ok = client.post("/api/auth/login", json={
        "username": "admin_user",
        "password": "AdminPass1234!",
    })
    assert resp_ok.status_code == 200
    data_ok = resp_ok.get_json()
    assert "token" in data_ok
    assert data_ok["username"] == "admin_user"
    assert data_ok["role"] == "admin"

    # Failure: Wrong password
    resp_bad = client.post("/api/auth/login", json={
        "username": "admin_user",
        "password": "WrongPassword999!",
    })
    assert resp_bad.status_code == 401
    assert resp_bad.get_json()["code"] == "INVALID_CREDENTIALS"

    # Failure: User not found
    resp_nouser = client.post("/api/auth/login", json={
        "username": "nonexistent",
        "password": "AnyPassword123!",
    })
    assert resp_nouser.status_code == 401


def test_auth_me_endpoint(test_setup):
    """Verify GET /api/auth/me returns current token payload."""
    client = test_setup["client"]
    token = test_setup["admin_token"]

    resp = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["username"] == "admin_user"
    assert data["role"] == "admin"


# =============================================================================
# 2. Unauthorized Route Rejection (FR-04 Security)
# =============================================================================

def test_unauthorized_requests_rejected(test_setup):
    """Verify that protected REST endpoints reject requests lacking valid JWT tokens with 401."""
    client = test_setup["client"]
    protected_urls = [
        "/api/summary",
        "/api/events",
        "/api/devices",
        "/api/blocklist",
        "/api/settings",
        "/api/scans",
    ]
    for url in protected_urls:
        resp = client.get(url)
        assert resp.status_code == 401
        data = resp.get_json()
        assert data["error"] == "Unauthorized"


# =============================================================================
# 3. Summary & Dashboard Metrics
# =============================================================================

def test_get_summary_metrics(test_setup):
    """Verify GET /api/summary returns event totals, class breakdown, and device counts."""
    client = test_setup["client"]
    db = test_setup["db"]
    token = test_setup["admin_token"]

    # Seed an event and a device
    db.upsert_device({
        "ip": "192.168.50.100",
        "device_type": "ip_camera",
        "possible_camera": True,
        "vendor": "TP-Link",
    })
    db.record_attack_event({
        "src_ip": "10.0.0.1",
        "dst_ip": "192.168.50.100",
        "predicted_class": "PortScan",
        "confidence": 0.90,
    })

    resp = client.get(
        "/api/summary",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["metrics"]["total_devices"] >= 1
    assert data["metrics"]["camera_devices"] >= 1
    assert data["metrics"]["total_incidents"] >= 1
    assert "PortScan" in data["class_distribution"]


# =============================================================================
# 4. Attack Events & Forensic Evidence
# =============================================================================

def test_attack_events_listing_and_patch(test_setup):
    """Verify querying attack history, reading incident details, and updating status."""
    client = test_setup["client"]
    db = test_setup["db"]
    token = test_setup["admin_token"]
    op_token = test_setup["operator_token"]

    event_id = db.record_attack_event({
        "src_ip": "10.0.0.88",
        "src_port": 50000,
        "dst_ip": "192.168.50.100",
        "dst_port": 554,
        "proto": "tcp",
        "predicted_class": "DDoS_DoS",
        "confidence": 0.95,
        "direction": "inbound",
        "evidence_note": "Volumetric RTSP stream flood",
    })

    # 1. Query events list with filter
    resp = client.get(
        "/api/events?class=DDoS_DoS",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["count"] == 1
    assert data["events"][0]["event_id"] == event_id

    # 2. Get event detail
    resp_detail = client.get(
        f"/api/events/{event_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_detail.status_code == 200
    detail = resp_detail.get_json()["event"]
    assert detail["src_ip"] == "10.0.0.88"
    assert detail["evidence_note"] == "Volumetric RTSP stream flood"

    # 3. Patch event status (Operator forbidden, Admin allowed)
    resp_op = client.patch(
        f"/api/events/{event_id}",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"status": "confirmed", "response_status": "mitigated"},
    )
    assert resp_op.status_code == 403

    resp_admin = client.patch(
        f"/api/events/{event_id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "confirmed", "response_status": "mitigated"},
    )
    assert resp_admin.status_code == 200
    assert resp_admin.get_json()["update"]["status"] == "confirmed"


# =============================================================================
# 5. Devices & Discovery Scans (FR-05, Section 3.7)
# =============================================================================

def test_devices_listing(test_setup):
    """Verify GET /api/devices with camera_only filter."""
    client = test_setup["client"]
    db = test_setup["db"]
    token = test_setup["admin_token"]

    db.upsert_device({"ip": "192.168.50.100", "possible_camera": True, "vendor": "TP-Link"})
    db.upsert_device({"ip": "192.168.50.1", "possible_camera": False, "vendor": "MikroTik"})

    resp_all = client.get("/api/devices", headers={"Authorization": f"Bearer {token}"})
    assert resp_all.status_code == 200
    assert resp_all.get_json()["count"] == 2

    resp_cam = client.get("/api/devices?camera_only=true", headers={"Authorization": f"Bearer {token}"})
    assert resp_cam.status_code == 200
    assert resp_cam.get_json()["count"] == 1
    assert resp_cam.get_json()["devices"][0]["ip"] == "192.168.50.100"


def test_trigger_scan_safety_guardrails(test_setup):
    """
    Verify POST /api/scans enforces approved subnet guardrails (Proposal Section 3.7).
    """
    client = test_setup["client"]
    token = test_setup["admin_token"]
    op_token = test_setup["operator_token"]

    # Non-admin forbidden
    resp_op = client.post(
        "/api/scans",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"subnet": "192.168.50.0/24"},
    )
    assert resp_op.status_code == 403

    # Unapproved subnet rejected with 403
    resp_unapproved = client.post(
        "/api/scans",
        headers={"Authorization": f"Bearer {token}"},
        json={"subnet": "10.99.99.0/24"},
    )
    assert resp_unapproved.status_code == 403
    assert resp_unapproved.get_json()["code"] == "UNAUTHORIZED_SUBNET"

    # Approved subnet accepted with 202
    resp_ok = client.post(
        "/api/scans",
        headers={"Authorization": f"Bearer {token}"},
        json={"subnet": "192.168.50.0/24"},
    )
    assert resp_ok.status_code == 202
    scan_id = resp_ok.get_json()["scan"]["scan_id"]

    # Fetch scan status
    resp_status = client.get(f"/api/scans/{scan_id}", headers={"Authorization": f"Bearer {token}"})
    assert resp_status.status_code == 200
    assert resp_status.get_json()["scan"]["status"] == "running"


# =============================================================================
# 6. Blocklist & Mitigation Rules (FR-06, FR-07)
# =============================================================================

def test_blocklist_enforcement_and_allowlist_protection(test_setup):
    """
    Verify manual block enforcement and allowlist safety protection (Proposal Section 3.7).
    """
    client = test_setup["client"]
    token = test_setup["admin_token"]

    # Allowlisted IP cannot be blocked
    resp_allow = client.post(
        "/api/blocklist",
        headers={"Authorization": f"Bearer {token}"},
        json={"ip": "192.168.50.1", "direction": "source", "reason": "Test block router"},
    )
    assert resp_allow.status_code == 403
    assert resp_allow.get_json()["code"] == "ALLOWLIST_PROTECTED"

    # Normal target IP blocked successfully
    target_ip = "192.168.50.77"
    resp_block = client.post(
        "/api/blocklist",
        headers={"Authorization": f"Bearer {token}"},
        json={"ip": target_ip, "direction": "source", "reason": "Persistent brute force"},
    )
    assert resp_block.status_code == 201
    assert resp_block.get_json()["block"]["ip"] == target_ip

    # Verify present in active blocklist
    resp_list = client.get("/api/blocklist?active_only=true", headers={"Authorization": f"Bearer {token}"})
    assert resp_list.status_code == 200
    ips = [b["ip"] for b in resp_list.get_json()["blocks"]]
    assert target_ip in ips

    # Unblock target IP
    resp_unblock = client.delete(
        f"/api/blocklist/{target_ip}",
        headers={"Authorization": f"Bearer {token}"},
        json={"reason": "Investigated by analyst"},
    )
    assert resp_unblock.status_code == 200
    assert resp_unblock.get_json()["unblocked"]["status"] == "removed"

    # Query full history for this IP
    resp_hist = client.get(f"/api/blocklist?ip={target_ip}", headers={"Authorization": f"Bearer {token}"})
    assert resp_hist.status_code == 200
    history = resp_hist.get_json()["history"]
    assert len(history) >= 1
    assert history[0]["status"] == "removed"


# =============================================================================
# 7. Operational Settings & Allowlist (FR-07)
# =============================================================================

def test_settings_get_put_and_history(test_setup):
    """Verify retrieving, updating, and auditing settings (Proposal FR-07)."""
    client = test_setup["client"]
    token = test_setup["admin_token"]
    op_token = test_setup["operator_token"]

    # 1. Update setting as admin
    resp_put = client.put(
        "/api/settings",
        headers={"Authorization": f"Bearer {token}"},
        json={"key": "min_confidence", "value": 0.89, "reason": "Lab threshold calibration"},
    )
    assert resp_put.status_code == 200

    # 2. Get setting
    resp_get = client.get(
        "/api/settings?key=min_confidence",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_get.status_code == 200
    assert resp_get.get_json()["value"] == 0.89

    # 3. Get setting audit history
    resp_hist = client.get(
        "/api/settings/history?key=min_confidence",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_hist.status_code == 200
    history = resp_hist.get_json()["history"]
    assert len(history) == 1
    assert history[0]["new_value"] == 0.89

    # 4. Operator cannot update setting
    resp_op = client.put(
        "/api/settings",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"key": "min_confidence", "value": 0.50},
    )
    assert resp_op.status_code == 403


# =============================================================================
# 8. Log Export & System Audit (FR-08)
# =============================================================================

def test_logs_export_json_and_csv(test_setup):
    """Verify exporting filtered logs as JSON and CSV per Proposal FR-08."""
    client = test_setup["client"]
    db = test_setup["db"]
    token = test_setup["admin_token"]

    db.record_attack_event({
        "src_ip": "10.0.0.1",
        "dst_ip": "192.168.50.100",
        "predicted_class": "PortScan",
        "confidence": 0.92,
        "evidence_note": "SYN scan test",
    })

    # JSON export
    resp_json = client.get(
        "/api/logs/export?format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_json.status_code == 200
    assert "application/json" in resp_json.content_type
    assert "ids_attack_logs_" in resp_json.headers["Content-Disposition"]
    exported_data = json.loads(resp_json.data)
    assert len(exported_data) >= 1
    assert exported_data[0]["predicted_class"] == "PortScan"

    # CSV export
    resp_csv = client.get(
        "/api/logs/export?format=csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_csv.status_code == 200
    assert "text/csv" in resp_csv.content_type
    csv_text = resp_csv.data.decode("utf-8")
    assert "event_id,timestamp,direction" in csv_text
    assert "PortScan" in csv_text


# =============================================================================
# 9. Real-Time Socket.IO Telemetry (FR-04)
# =============================================================================

def test_socketio_authenticated_connection(test_setup):
    """Verify Socket.IO connection accepts valid JWT and rejects invalid/missing tokens."""
    app = test_setup["app"]
    socketio = test_setup["socketio"]
    token = test_setup["admin_token"]

    # 1. Valid token connects successfully
    client_valid = socketio.test_client(app, auth={"token": token})
    assert client_valid.is_connected()
    received = client_valid.get_received()
    assert len(received) >= 1
    assert received[0]["name"] == "connected"
    assert received[0]["args"][0]["status"] == "authenticated"
    client_valid.disconnect()

    # 2. Invalid token rejected
    client_bad = socketio.test_client(app, auth={"token": "forged_invalid_token_123"})
    assert not client_bad.is_connected()

    # 3. Missing token rejected
    client_missing = socketio.test_client(app)
    assert not client_missing.is_connected()


def test_socketio_event_broadcast_reception(test_setup):
    """Verify connected Socket.IO clients receive real-time updates without refreshing (FR-04)."""
    app = test_setup["app"]
    socketio = test_setup["socketio"]
    client_http = test_setup["client"]
    token = test_setup["admin_token"]

    client_sio = socketio.test_client(app, auth={"token": token})
    assert client_sio.is_connected()
    # Clear initial connect message
    client_sio.get_received()

    # Trigger a block via REST API
    client_http.post(
        "/api/blocklist",
        headers={"Authorization": f"Bearer {token}"},
        json={"ip": "192.168.50.88", "reason": "SocketIO broadcast test"},
    )

    # Check that client_sio received 'blocklist_update'
    received = client_sio.get_received()
    event_names = [r["name"] for r in received]
    assert "blocklist_update" in event_names
    block_evt = next(r for r in received if r["name"] == "blocklist_update")
    assert block_evt["args"][0]["ip"] == "192.168.50.88"

    client_sio.disconnect()



def test_settings_change_is_applied_to_running_policy(test_setup):
    """FR-07: a setting saved from the dashboard changes the running response policy at once,
    a wrong value is refused, and GET /api/settings shows the values in use."""
    client = test_setup["client"]
    token = test_setup["admin_token"]
    engine = test_setup["app"].config["decision_engine"]
    headers = {"Authorization": f"Bearer {token}"}

    resp = client.put("/api/settings", headers=headers,
                      json={"key": "min_repeats", "value": 7, "reason": "lab test"})
    assert resp.status_code == 200
    assert engine.policy.min_repeats == 7

    bad = client.put("/api/settings", headers=headers, json={"key": "min_confidence", "value": 3})
    assert bad.status_code == 400

    current = client.get("/api/settings", headers=headers).get_json()["settings"]
    assert current["min_repeats"] == 7
    assert "allowlist" in current and "auto_response" in current

    hist = client.get("/api/settings/history", headers=headers).get_json()["history"]
    assert any(h["key"] == "min_repeats" and h["new_value"] == 7 for h in hist)


def test_step34_manual_block_unblock_audit(test_setup):
    """
    Step 34: Manual block and unblock from the dashboard call the adapter,
    and are written to the audit log (system_logs) with the admin's name.
    """
    client = test_setup["client"]
    db = test_setup["db"]
    token = test_setup["admin_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Manual block with minutes parameter (frontend format)
    resp = client.post(
        "/api/blocklist",
        headers=headers,
        json={
            "ip": "192.168.50.77",
            "direction": "inbound",
            "minutes": 45,
            "reason": "Test manual operator block",
        },
    )
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["status"] == "success"
    assert data["block"]["ip"] == "192.168.50.77"
    assert data["block"]["actor"] == "admin_user"

    # Verify both 'blocks' and 'rules' in GET /api/blocklist
    get_resp = client.get("/api/blocklist", headers=headers)
    assert get_resp.status_code == 200
    get_data = get_resp.get_json()
    assert "blocks" in get_data
    assert "rules" in get_data
    assert any(b["ip"] == "192.168.50.77" for b in get_data["blocks"])

    # Verify system_logs audit entry
    logs = list(db.system_logs.find({"event": "MANUAL_BLOCK", "actor": "admin_user"}))
    assert len(logs) >= 1
    assert logs[0]["details"]["ip"] == "192.168.50.77"
    assert logs[0]["details"]["duration_minutes"] == 45

    # 2. Manual unblock
    unblock_resp = client.delete(
        "/api/blocklist/192.168.50.77",
        headers=headers,
        json={"reason": "Operator cleared false positive"},
    )
    assert unblock_resp.status_code == 200
    unblock_data = unblock_resp.get_json()
    assert unblock_data["status"] == "success"

    # Verify MANUAL_UNBLOCK system_logs audit entry
    unblock_logs = list(db.system_logs.find({"event": "MANUAL_UNBLOCK", "actor": "admin_user"}))
    assert len(unblock_logs) >= 1
    assert unblock_logs[0]["details"]["ip"] == "192.168.50.77"


def test_step34_firewall_sync_and_worker_endpoints(test_setup):
    """
    Step 34: Test REST API endpoints for firewall synchronization and rule expiry worker.
    """
    client = test_setup["client"]
    token = test_setup["admin_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. GET /api/v1/firewall/sync
    sync_resp = client.get("/api/v1/firewall/sync", headers=headers)
    assert sync_resp.status_code == 200
    sync_data = sync_resp.get_json()
    assert sync_data["status"] == "success"
    assert "in_sync" in sync_data
    assert "firewall_rules" in sync_data
    assert "db_active_blocks" in sync_data

    # 2. POST /api/v1/firewall/sync
    post_sync = client.post("/api/v1/firewall/sync", headers=headers)
    assert post_sync.status_code == 200
    assert post_sync.get_json()["reconciliation"]["status"] == "success"

    # 3. Worker status, start, and stop
    w_status = client.get("/api/v1/firewall/worker/status", headers=headers)
    assert w_status.status_code == 200
    assert "running" in w_status.get_json()["worker"]

    w_start = client.post("/api/v1/firewall/worker/start", headers=headers)
    assert w_start.status_code == 200
    assert w_start.get_json()["success"] is True

    w_stop = client.post("/api/v1/firewall/worker/stop", headers=headers)
    assert w_stop.status_code == 200
    assert w_stop.get_json()["success"] is True
