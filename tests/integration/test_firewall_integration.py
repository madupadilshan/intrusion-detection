"""
tests/integration/test_firewall_integration.py
==============================================
Real-Time Intrusion Detection and Autonomous Response System for IP-Camera IoT Networks
Group 03 - University of Sri Jayewardenepura

Integration tests for Flask REST endpoints with firewall response adapter (Step 33).
"""

import pytest
from unittest.mock import MagicMock

from core_engine.app import create_app
from core_engine.firewall.simulation_adapter import SimulationAdapter
from core_engine.auth import AuthManager


@pytest.fixture
def mock_db():
    """Mock DatabaseService for Flask integration testing."""
    db = MagicMock()
    db.is_connected.return_value = True
    db.get_blocked_ips.return_value = [
        {"ip": "203.0.113.15", "direction": "src", "status": "active", "reason": "Test block"}
    ]
    db.get_block_history_for_ip.return_value = []
    db.add_to_blocklist.return_value = "mock_block_id_999"
    db.remove_from_blocklist.return_value = 1
    db.log_response_action.return_value = True
    db.log_system_event.return_value = True
    return db


@pytest.fixture
def test_sim_firewall():
    """Configured SimulationAdapter for test isolation."""
    return SimulationAdapter()


@pytest.fixture
def app_client(mock_db, test_sim_firewall):
    """Flask test client with authenticated admin token and mock services."""
    auth_mgr = AuthManager(db_service=mock_db, secret_key="test_integration_secret_jwt_key_32bytes_long!")
    admin_token = auth_mgr.create_token(username="admin_soc", role="admin")

    app, socketio = create_app(
        db_service=mock_db,
        auth_manager=auth_mgr,
        firewall_adapter=test_sim_firewall,
        test_config={"TESTING": True},
    )

    client = app.test_client()
    return client, admin_token, test_sim_firewall, mock_db


def test_api_list_blocklist_includes_adapter_metadata(app_client):
    """Verify GET /api/blocklist returns active blocks and adapter metadata."""
    client, token, fw, db = app_client

    res = client.get(
        "/api/blocklist",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["adapter_mode"] == "simulation"
    assert data["is_simulated"] is True
    assert len(data["blocks"]) == 1


def test_api_add_block_invokes_firewall_adapter(app_client):
    """Verify POST /api/blocklist enforces block on firewall adapter and MongoDB."""
    client, token, fw, db = app_client
    target_ip = "198.51.100.77"

    res = client.post(
        "/api/blocklist",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ip": target_ip,
            "direction": "src",
            "duration_minutes": 30,
            "reason": "ADMIN_INTEGRATION_TEST",
        },
    )

    assert res.status_code == 201
    data = res.get_json()
    assert data["status"] == "success"
    assert data["block"]["ip"] == target_ip
    assert data["block"]["status"] == "active"

    # Verified stored in firewall adapter
    active_rules = fw.list_active()
    assert len(active_rules) == 1
    assert active_rules[0]["ip"] == target_ip

    # Verified persisted in DB
    db.add_to_blocklist.assert_called_once()
    db.log_response_action.assert_called_once()


def test_api_remove_block_invokes_firewall_adapter(app_client):
    """Verify DELETE /api/blocklist/<ip> removes block from firewall adapter and updates MongoDB."""
    client, token, fw, db = app_client
    target_ip = "198.51.100.88"

    # Pre-populate in firewall adapter
    fw.block(target_ip, direction="src", minutes=30)
    assert len(fw.list_active()) == 1

    res = client.delete(
        f"/api/blocklist/{target_ip}",
        headers={"Authorization": f"Bearer {token}"},
        json={"reason": "Operator cleared false positive"},
    )

    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "success"
    assert data["unblocked"]["ip"] == target_ip

    # Verified removed from firewall adapter
    assert len(fw.list_active()) == 0

    # Verified updated in DB
    db.remove_from_blocklist.assert_called_once()
    db.log_response_action.assert_called_once()


def test_api_block_rejects_allowlisted_ip(app_client):
    """Verify POST /api/blocklist rejects allowlisted management IP with HTTP 403."""
    client, token, fw, db = app_client
    protected_ip = "192.168.50.1"

    res = client.post(
        "/api/blocklist",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "ip": protected_ip,
            "direction": "src",
            "reason": "Attacking attempt on router",
        },
    )

    assert res.status_code == 403
    data = res.get_json()
    assert data["code"] == "ALLOWLIST_PROTECTED"
    assert len(fw.list_active()) == 0
