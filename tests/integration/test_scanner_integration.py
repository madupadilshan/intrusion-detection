"""
tests/integration/test_scanner_integration.py - Integration Tests for Scanner Service (Step 27).
================================================================================================

Tests end-to-end device discovery, multi-evidence camera heuristics, MongoDB persistence,
Socket.IO live event broadcast, and administrator camera confirmation adhering to Group 03 Proposal:
- Section 3.7: Subnet restriction (192.168.50.0/24), camera identification heuristics.
- Section 3.6: Figure 4 ('devices', 'scans', 'system_logs' collections).
- Table 7: Requirement FR-05 (Device Discovery).
"""

import os
import time
import pytest
from datetime import datetime, timezone
from pymongo import MongoClient
from unittest.mock import MagicMock

from core_engine.app import create_app
from core_engine.db_service import DatabaseService
from core_engine.auth import AuthManager
from core_engine.scanner_service import ScannerService, UnauthorizedSubnetError

TEST_DB_NAME = "iot_ids_test"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
TEST_JWT_SECRET = "test_super_secret_jwt_key_2026_scanner_test"


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
    """Sets up an isolated DatabaseService, AuthManager, Flask client targeting iot_ids_test."""
    db = DatabaseService(uri=MONGO_URI, db_name=TEST_DB_NAME)
    db.drop_database_for_testing()
    db.connect()

    auth = AuthManager(db_service=db, secret_key=TEST_JWT_SECRET, token_expiry_hours=8)
    mock_socketio = MagicMock()

    scanner = ScannerService(
        db_service=db,
        socketio=mock_socketio,
        approved_subnets=["192.168.50.0/24"],
        allow_simulation=True,  # these tests use the scanner's invented devices on purpose
        nmap_command=None,
    )
    scanner.is_nmap_available, scanner.nm = False, None  # never scan a real network in tests

    app, socketio = create_app(
        db_service=db,
        auth_manager=auth,
        scanner_service=scanner,
        test_config={"TESTING": True},
    )

    # Seed test users
    admin_hash = AuthManager.hash_password("AdminPass1234!")
    op_hash = AuthManager.hash_password("OperatorPass1234!")
    db.create_user("admin", admin_hash, role="admin")
    db.create_user("operator", op_hash, role="operator")

    admin_token = auth.create_token("admin", role="admin")
    op_token = auth.create_token("operator", role="operator")

    client = app.test_client()

    yield {
        "db": db,
        "auth": auth,
        "scanner": scanner,
        "mock_socketio": mock_socketio,
        "client": client,
        "admin_token": admin_token,
        "operator_token": op_token,
    }

    db.drop_database_for_testing()
    db.close()


# =============================================================================
# 1. Synchronous Network Discovery & Database Persistence
# =============================================================================

def test_scanner_sync_scan_persistence(test_setup):
    """
    Verify scan execution persists scan metadata and discovered devices to MongoDB.
    """
    db = test_setup["db"]
    scanner = test_setup["scanner"]

    result = scanner.scan_network(subnet="192.168.50.0/24", started_by="admin_researcher")

    assert result["status"] == "completed"
    assert result["devices_found"] == 5
    assert result["cameras_found"] == 2
    scan_id = result["scan_id"]

    # Verify scan record in scans collection
    scan_doc = db.scans.find_one({"scan_id": scan_id})
    assert scan_doc is not None
    assert scan_doc["status"] == "completed"
    assert scan_doc["devices_found"] == 5
    assert scan_doc["started_by"] == "admin_researcher"
    assert "192.168.50.60" in scan_doc["discovered_ips"]

    # Verify devices collection has Dahua IP Camera
    camera_doc = db.devices.find_one({"ip": "192.168.50.60"})
    assert camera_doc is not None
    assert camera_doc["possible_camera"] is True
    assert camera_doc["confirmed_camera"] is False
    assert camera_doc["device_type"] == "ip_camera"
    assert "Dahua Technology" in camera_doc["vendor"]
    assert 554 in camera_doc["open_ports"]
    assert 37777 in camera_doc["open_ports"]
    assert len(camera_doc["camera_evidence"]) >= 3
    assert camera_doc["simulated"] is True  # invented device: always marked (D-056)

    # Verify router device has possible_camera = False
    router_doc = db.devices.find_one({"ip": "192.168.50.1"})
    assert router_doc is not None
    assert router_doc["possible_camera"] is False
    assert router_doc["device_type"] == "router"

    # Verify audit logs in system_logs
    logs = list(db.system_logs.find({"actor": "admin_researcher"}).sort("timestamp", 1))
    assert len(logs) >= 2
    events = [l["event"] for l in logs]
    assert "SCAN_STARTED" in events
    assert "SCAN_COMPLETED" in events


# =============================================================================
# 2. Asynchronous Scan Execution
# =============================================================================

def test_scanner_async_scan_execution(test_setup):
    """
    Verify start_scan_async initiates immediately and completes in background.
    """
    db = test_setup["db"]
    scanner = test_setup["scanner"]

    scan_id = scanner.start_scan_async(subnet="192.168.50.0/24", started_by="admin_async")
    assert scan_id is not None

    # Wait for background thread completion (up to 3 seconds)
    completed = False
    for _ in range(30):
        time.sleep(0.1)
        doc = db.scans.find_one({"scan_id": scan_id})
        if doc and doc.get("status") == "completed":
            completed = True
            break

    assert completed is True
    doc = db.scans.find_one({"scan_id": scan_id})
    assert doc["devices_found"] == 5
    assert doc["started_by"] == "admin_async"


# =============================================================================
# 3. Live Socket.IO Broadcast Verification
# =============================================================================

def test_scanner_socketio_telemetry_emission(test_setup):
    """
    Verify scan progress and discovered device events are broadcast via Socket.IO.
    """
    scanner = test_setup["scanner"]
    mock_sio = test_setup["mock_socketio"]

    scanner.scan_network(subnet="192.168.50.0/24", started_by="admin_sio")

    # Verify scan_progress events were emitted
    progress_calls = [
        call for call in mock_sio.emit.call_args_list if call[0][0] == "scan_progress"
    ]
    assert len(progress_calls) >= 3

    # Verify device_update events were emitted for each host
    device_calls = [
        call for call in mock_sio.emit.call_args_list if call[0][0] == "device_update"
    ]
    assert len(device_calls) == 5
    discovered_ips = [call[0][1]["ip"] for call in device_calls]
    assert "192.168.50.60" in discovered_ips
    assert "192.168.50.1" in discovered_ips


# =============================================================================
# 4. Administrator Camera Confirmation API (Proposal Section 3.7)
# =============================================================================

def test_admin_confirm_camera_endpoint(test_setup):
    """
    Verify Proposal Section 3.7:
    'A device is labelled as a possible camera with evidence, and the administrator confirms the role.'
    """
    client = test_setup["client"]
    db = test_setup["db"]
    admin_token = test_setup["admin_token"]
    op_token = test_setup["operator_token"]

    # Seed an unconfirmed device
    db.upsert_device({
        "ip": "192.168.50.60",
        "mac": "3C:EF:8C:11:22:33",
        "vendor": "Dahua Technology",
        "device_type": "ip_camera",
        "possible_camera": True,
        "confirmed_camera": False,
        "camera_evidence": ["RTSP streaming port 554 open"],
    })

    # Non-admin user cannot confirm camera role
    resp_op = client.patch(
        "/api/devices/192.168.50.60/confirm-camera",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"confirmed": True, "notes": "Unauthorized attempt"},
    )
    assert resp_op.status_code == 403

    # Admin confirms camera role
    resp_admin = client.patch(
        "/api/devices/192.168.50.60/confirm-camera",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"confirmed": True, "notes": "Verified Dahua IP dome camera in lab rack"},
    )
    assert resp_admin.status_code == 200
    res_data = resp_admin.get_json()
    assert res_data["status"] == "success"
    assert res_data["device"]["confirmed_camera"] is True
    assert "rack" in res_data["device"]["notes"]

    # Verify database state
    dev = db.devices.find_one({"ip": "192.168.50.60"})
    assert dev["confirmed_camera"] is True

    # Verify audit log in system_logs
    log = db.system_logs.find_one({"event": "DEVICE_CAMERA_CONFIRMED"})
    assert log is not None
    assert log["actor"] == "admin"
    assert log["details"]["ip"] == "192.168.50.60"

    # Revoke confirmation
    resp_revoke = client.patch(
        "/api/devices/192.168.50.60/confirm-camera",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"confirmed": False, "notes": "Reassigned as general sensor"},
    )
    assert resp_revoke.status_code == 200
    assert resp_revoke.get_json()["device"]["confirmed_camera"] is False

    dev_after = db.devices.find_one({"ip": "192.168.50.60"})
    assert dev_after["confirmed_camera"] is False


# =============================================================================
# 5. Unauthorized Subnet Safety Guardrail Rejection
# =============================================================================

def test_unauthorized_subnet_rejection(test_setup):
    """
    Verify scan_network refuses targets outside approved lab subnets
    and does not write records to database.
    """
    scanner = test_setup["scanner"]
    db = test_setup["db"]

    with pytest.raises(UnauthorizedSubnetError):
        scanner.scan_network(subnet="10.10.10.0/24")

    # Ensure no scan was written
    count = db.scans.count_documents({"subnet": "10.10.10.0/24"})
    assert count == 0
