"""
tests/integration/test_export_integration.py - Integration Tests for Log Export Service (Step 28).
==================================================================================================

Validates end-to-end log export functionality over HTTP REST endpoints, MongoDB persistence,
multi-attribute query filtering, and audit trail invariants adhering to Group 03 Proposal:
- Table 7 Requirement FR-08 ("Forensic Log Export").
- Table 7 Requirement FR-07 ("Audit Logging and Invariants").
- Section 3.6 (Figure 4: `attack_events`, `system_logs`, `response_actions`).
"""

import os
import json
import pytest
from datetime import datetime, timezone, timedelta
from pymongo import MongoClient

from core_engine.app import create_app
from core_engine.db_service import DatabaseService
from core_engine.auth import AuthManager
from core_engine.export_service import ExportService

TEST_DB_NAME = "iot_ids_test"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
TEST_JWT_SECRET = "test_super_secret_jwt_key_2026_export_test"


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
    """Sets up an isolated DatabaseService, AuthManager, and Flask client targeting iot_ids_test."""
    db = DatabaseService(uri=MONGO_URI, db_name=TEST_DB_NAME)
    db.drop_database_for_testing()
    db.connect()

    auth = AuthManager(db_service=db, secret_key=TEST_JWT_SECRET, token_expiry_hours=8)
    exporter = ExportService(db_service=db)

    app, socketio = create_app(
        db_service=db,
        auth_manager=auth,
        export_service=exporter,
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

    # Seed sample attack events
    now = datetime.now(timezone.utc)
    db.record_attack_event({
        "event_id": "evt_ddos_01",
        "timestamp": now - timedelta(hours=2),
        "src_ip": "10.0.0.50",
        "dst_ip": "192.168.50.60",
        "predicted_class": "DDoS",
        "confidence": 0.98,
        "severity": "critical",
        "status": "confirmed",
        "response_status": "mitigated",
        "evidence_note": "HTTP flood targeting camera web server",
    })

    db.record_attack_event({
        "event_id": "evt_scan_01",
        "timestamp": now - timedelta(hours=1),
        "src_ip": "10.0.0.99",
        "dst_ip": "192.168.50.60",
        "predicted_class": "PortScan",
        "confidence": 0.94,
        "severity": "high",
        "status": "prediction",
        "response_status": "candidate",
        "evidence_note": "SYN probe on port 554",
    })

    # Seed sample response action
    db.log_response_action({
        "action_id": "act_001",
        "action": "block",
        "target_ip": "10.0.0.50",
        "direction": "source",
        "rule": "drop 10.0.0.50",
        "reason_code": "DOS_MITIGATION",
        "actor": "admin",
        "status": "applied",
        "executed_at": now - timedelta(hours=2),
        "details": {"duration_seconds": 3600},
    })

    # Seed sample system log
    db.log_system_event(
        actor="admin",
        event="SCAN_STARTED",
        outcome="success",
        details={"subnet": "192.168.50.0/24"},
    )

    yield {
        "db": db,
        "auth": auth,
        "exporter": exporter,
        "client": client,
        "admin_token": admin_token,
        "operator_token": op_token,
        "now": now,
    }

    db.drop_database_for_testing()
    db.close()


# =============================================================================
# 1. RBAC and Endpoint Validation
# =============================================================================

def test_export_rbac_enforcement(test_setup):
    """Verify non-admin users cannot access log exports."""
    client = test_setup["client"]
    op_token = test_setup["operator_token"]

    resp = client.get(
        "/api/logs/export",
        headers={"Authorization": f"Bearer {op_token}"},
    )
    assert resp.status_code == 403


def test_export_invalid_inputs(test_setup):
    """Verify invalid format or log type returns 400 Bad Request."""
    client = test_setup["client"]
    admin_token = test_setup["admin_token"]

    # Invalid format
    resp_fmt = client.get(
        "/api/logs/export?format=xml",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_fmt.status_code == 400

    # Invalid type
    resp_type = client.get(
        "/api/logs/export?type=invalid_type",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert resp_type.status_code == 400


# =============================================================================
# 2. Attack Events Export with Multi-Attribute Filtering
# =============================================================================

def test_export_attack_events_json_and_csv(test_setup):
    """Verify attack events export in JSON and CSV with filtering."""
    client = test_setup["client"]
    db = test_setup["db"]
    token = test_setup["admin_token"]

    # 1. JSON Export filtered by class = DDoS
    resp_json = client.get(
        "/api/logs/export?type=events&format=json&class=DDoS",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_json.status_code == 200
    assert "application/json" in resp_json.content_type
    assert "ids_attack_logs_" in resp_json.headers["Content-Disposition"]

    data = json.loads(resp_json.data)
    assert len(data) == 1
    assert data[0]["predicted_class"] == "DDoS"
    assert data[0]["src_ip"] == "10.0.0.50"

    # 2. CSV Export filtered by IP
    resp_csv = client.get(
        "/api/logs/export?type=events&format=csv&ip=10.0.0.99",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_csv.status_code == 200
    assert "text/csv" in resp_csv.content_type
    csv_str = resp_csv.data.decode("utf-8")
    assert "event_id,timestamp,direction" in csv_str
    assert "10.0.0.99" in csv_str
    assert "PortScan" in csv_str
    assert "10.0.0.50" not in csv_str

    # 3. Verify audit log entry in system_logs (Requirement FR-08)
    audit_logs = list(db.system_logs.find({"event": "LOGS_EXPORTED"}))
    assert len(audit_logs) >= 2
    last_audit = audit_logs[-1]
    assert last_audit["actor"] == "admin"
    assert last_audit["details"]["log_type"] == "attack_events"
    assert last_audit["details"]["row_count"] == 1


# =============================================================================
# 3. System Logs and Response Actions Export
# =============================================================================

def test_export_system_logs_and_actions(test_setup):
    """Verify system logs and response actions export cleanly."""
    client = test_setup["client"]
    token = test_setup["admin_token"]

    # System Logs CSV
    resp_sys = client.get(
        "/api/logs/export?type=system_logs&format=csv",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_sys.status_code == 200
    assert "ids_system_logs_" in resp_sys.headers["Content-Disposition"]
    sys_csv = resp_sys.data.decode("utf-8")
    assert "log_id,timestamp,actor,event,outcome,details" in sys_csv

    # Response Actions JSON
    resp_act = client.get(
        "/api/logs/export?type=actions&format=json",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp_act.status_code == 200
    assert "ids_response_actions_" in resp_act.headers["Content-Disposition"]
    act_data = json.loads(resp_act.data)
    assert len(act_data) == 1
    assert act_data[0]["action"] == "block"
    assert act_data[0]["target_ip"] == "10.0.0.50"
