"""
tests/unit/test_firewall_adapters.py
====================================
Real-Time Intrusion Detection and Autonomous Response System for IP-Camera IoT Networks
Group 03 - University of Sri Jayewardenepura

Unit tests for firewall response adapters suite and factory (Step 33).
"""

import time
from unittest.mock import MagicMock, patch
import pytest

from core_engine.firewall import (
    BaseFirewallAdapter,
    FirewallError,
    AllowlistImmunityError,
    NftablesAdapter,
    RouterAdapter,
    SimulationAdapter,
    get_firewall_adapter,
)
from core_engine.response_policy import PolicyDecision
from core_engine.decision_engine import DecisionEngine


def test_simulation_adapter_block_and_unblock():
    """Verify in-memory simulation adapter blocking, duration clamping, and unblocking."""
    adapter = SimulationAdapter(max_rule_minutes=60)
    assert adapter.is_simulated is True
    assert adapter.name == "simulation"
    assert adapter.mode == "simulation"

    # Block source
    target_ip = "198.51.100.44"
    res = adapter.block(target_ip, direction="src", minutes=30, reason="TEST_BLOCK")
    assert res["ip"] == target_ip
    assert res["direction"] == "src"
    assert res["action"] == "block"
    assert res["duration_minutes"] == 30
    assert res["simulated"] is True

    # Active list
    active = adapter.list_active()
    assert len(active) == 1
    assert active[0]["ip"] == target_ip
    assert active[0]["remaining_minutes"] > 29.0

    # Unblock
    removed = adapter.unblock(target_ip, direction="src")
    assert removed is True
    assert len(adapter.list_active()) == 0


def test_simulation_adapter_rate_limit():
    """Verify simulation adapter rate-limiting and clearing."""
    adapter = SimulationAdapter()
    target_ip = "203.0.113.88"
    res = adapter.rate_limit(target_ip, minutes=20, reason="TEST_RATE_LIMIT")
    assert res["ip"] == target_ip
    assert res["action"] == "rate_limit"
    assert res["set"] == "limit_src"

    active = adapter.list_active("limit_src")
    assert len(active) == 1
    assert active[0]["ip"] == target_ip

    adapter.clear()
    assert len(adapter.list_active()) == 0


def test_simulation_adapter_allowlist_protected():
    """Verify simulation adapter rejects blocking protected management IPs."""
    adapter = SimulationAdapter()
    for ip in ["192.168.50.1", "192.168.50.5", "192.168.50.10", "192.168.50.20"]:
        with pytest.raises(AllowlistImmunityError):
            adapter.block(ip)
        with pytest.raises(AllowlistImmunityError):
            adapter.rate_limit(ip)


def test_router_adapter_simulation_fallback():
    """Verify RouterAdapter operates in simulation mode when host is absent or set to simulation."""
    adapter = RouterAdapter(router_host="simulation", max_rule_minutes=45)
    assert adapter.is_simulated is True
    assert adapter.name == "router_ssh"
    assert adapter.mode == "passive_router"

    # Block destination (e.g. C&C)
    cnc_ip = "198.51.100.99"
    res = adapter.block(cnc_ip, direction="dst", minutes=90, reason="AUTO_CNC_DEST_BLOCK")
    assert res["ip"] == cnc_ip
    assert res["direction"] == "dst"
    assert res["duration_minutes"] == 45  # Clamped to 45 mins
    assert res["simulated"] is True

    active = adapter.list_active()
    assert len(active) == 1
    assert active[0]["ip"] == cnc_ip

    removed = adapter.unblock(cnc_ip, direction="dst")
    assert removed is True
    assert len(adapter.list_active()) == 0


def test_router_adapter_ssh_command_generation():
    """Verify RouterAdapter generates correct SSH commands in live mode."""
    adapter = RouterAdapter(
        router_host="192.168.50.1",
        router_port=2222,
        router_user="ids_admin",
        router_key_file="/path/to/key",
        simulate=False,
    )
    assert adapter.is_simulated is False

    with patch("subprocess.run") as mock_run:
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        # Block
        adapter.block("203.0.113.10", direction="src", minutes=30)
        expected_cmd = [
            "ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5",
            "-p", "2222", "-i", "/path/to/key",
            "ids_admin@192.168.50.1",
            "nft add element inet ids block_src '{ 203.0.113.10 timeout 30m }'"
        ]
        # Verify SSH was executed with remote nft command
        assert mock_run.called
        call_args = mock_run.call_args[0][0]
        assert "nft add element inet ids block_src '{ 203.0.113.10 timeout 30m }'" in call_args


def test_get_firewall_adapter_factory():
    """Verify get_firewall_adapter factory instantiation across types."""
    # Simulation
    fw_sim = get_firewall_adapter({"type": "simulation"})
    assert isinstance(fw_sim, SimulationAdapter)

    # Nftables
    fw_nft = get_firewall_adapter({"type": "nftables", "table_family": "bridge", "simulate": True})
    assert isinstance(fw_nft, NftablesAdapter)
    assert fw_nft.table_family == "bridge"

    # Router
    fw_rtr = get_firewall_adapter({"type": "router", "host": "192.168.50.1", "simulate": True})
    assert isinstance(fw_rtr, RouterAdapter)


def test_decision_engine_execute_response_integration():
    """Verify DecisionEngine.execute_response executes response on firewall, DB, and Socket.IO."""
    mock_db = MagicMock()
    mock_sio = MagicMock()
    sim_fw = SimulationAdapter()

    engine = DecisionEngine(
        db_service=mock_db,
        socketio=mock_sio,
        firewall_adapter=sim_fw,
    )

    decision = PolicyDecision(
        should_act=True,
        action_type="block",
        target_ip="203.0.113.66",
        direction="inbound",
        duration_minutes=30,
        reason_code="AUTO_PORTSCAN_REPEATED",
    )

    rule = engine.execute_response(decision, event_id="event_777", actor="autonomous_policy")

    assert rule is not None
    assert rule["ip"] == "203.0.113.66"
    assert rule["duration_minutes"] == 30

    # Verified stored in simulation adapter
    assert len(sim_fw.list_active()) == 1

    # Verified added to DB blocklist and response action logged
    mock_db.add_to_blocklist.assert_called_once()
    assert mock_db.add_to_blocklist.call_args[1]["ip"] == "203.0.113.66"
    mock_db.log_response_action.assert_called_once()
    assert mock_db.log_response_action.call_args[0][0]["action"] == "block"

    # Verified emitted via Socket.IO
    mock_sio.emit.assert_called_once()
    emit_event, emit_payload = mock_sio.emit.call_args[0]
    assert emit_event == "blocklist_update"
    assert emit_payload["ip"] == "203.0.113.66"


def test_decision_engine_execute_response_skipped():
    """Verify DecisionEngine.execute_response logs skipped action when should_act is False."""
    mock_db = MagicMock()
    sim_fw = SimulationAdapter()

    engine = DecisionEngine(
        db_service=mock_db,
        firewall_adapter=sim_fw,
    )

    decision = PolicyDecision(
        should_act=False,
        action_type="none",
        target_ip="192.168.50.1",
        direction="inbound",
        duration_minutes=0,
        reason_code="SKIP_ALLOWLIST",
    )

    rule = engine.execute_response(decision, event_id="event_888")
    assert rule is None
    assert len(sim_fw.list_active()) == 0

    # Logged skipped action
    mock_db.log_response_action.assert_called_once()
    action_arg = mock_db.log_response_action.call_args[0][0]
    assert action_arg["status"] == "skipped"
    assert action_arg["reason"] == "SKIP_ALLOWLIST"
