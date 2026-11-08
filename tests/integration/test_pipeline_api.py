"""
tests/integration/test_pipeline_api.py - Integration tests for Live Streaming Pipeline Endpoints.
=================================================================================================
"""

import pytest
from core_engine.app import create_app
from core_engine.db_service import DatabaseService
from core_engine.auth import AuthManager
from core_engine.firewall.simulation_adapter import SimulationAdapter
from core_engine.runner import LivePipelineRunner
from unittest.mock import MagicMock


@pytest.fixture
def app_client():
    db = DatabaseService(db_name="iot_ids_test")
    auth = AuthManager(db_service=db)
    firewall = SimulationAdapter()

    mock_runner = MagicMock()
    mock_runner.get_status.return_value = {
        "status": "running",
        "is_running": True,
        "error_message": None,
        "conn_log_path": "sensor/logs/conn.log",
        "metrics": {"batches_processed": 5, "flows_processed": 50, "attacks_detected": 2},
    }
    mock_runner.start.return_value = True
    mock_runner.stop.return_value = True

    app, socketio = create_app(
        db_service=db,
        auth_manager=auth,
        firewall_adapter=firewall,
        pipeline_runner=mock_runner,
        test_config={"TESTING": True},
    )

    client = app.test_client()
    token = auth.create_token(username="admin", role="admin")

    return client, token, mock_runner


def test_pipeline_status_endpoint(app_client):
    client, token, mock_runner = app_client
    resp = client.get(
        "/api/v1/pipeline/status",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["status"] == "running"
    assert data["is_running"] is True
    assert data["metrics"]["batches_processed"] == 5


def test_pipeline_start_endpoint(app_client):
    client, token, mock_runner = app_client
    resp = client.post(
        "/api/v1/pipeline/start",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    mock_runner.start.assert_called_once()


def test_pipeline_stop_endpoint(app_client):
    client, token, mock_runner = app_client
    resp = client.post(
        "/api/v1/pipeline/stop",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    mock_runner.stop.assert_called_once()
