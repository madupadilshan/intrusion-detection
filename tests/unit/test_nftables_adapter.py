"""
tests/unit/test_nftables_adapter.py
===================================
Real-Time Intrusion Detection and Autonomous Response System for IP-Camera IoT Networks
Group 03 - University of Sri Jayewardenepura

Unit tests for nftables firewall adapter and ruleset specifications (Step 32).
"""

import json
import os
import time
from unittest.mock import MagicMock, patch
import pytest

from core_engine.firewall.nftables_adapter import (
    NftablesAdapter,
    NftablesError,
    AllowlistProtectedError,
)


@pytest.fixture
def adapter():
    """Create a simulated NftablesAdapter with default settings."""
    return NftablesAdapter(
        table_family="bridge",
        table_name="ids",
        simulate=True,
        max_rule_minutes=60,
    )


def test_nft_rule_files_exist_and_structure():
    """Verify that sensor/ids_inline.nft and sensor/ids_router.nft exist and conform to spec."""
    inline_path = os.path.join("sensor", "ids_inline.nft")
    router_path = os.path.join("sensor", "ids_router.nft")

    assert os.path.exists(inline_path), "sensor/ids_inline.nft must exist"
    assert os.path.exists(router_path), "sensor/ids_router.nft must exist"

    with open(inline_path, "r", encoding="utf-8") as f:
        inline_content = f.read()

    # Must be bridge family
    assert "table bridge ids" in inline_content
    # Must have sets with timeout flags
    assert "set allow" in inline_content
    assert "set block_src" in inline_content
    assert "set block_dst" in inline_content
    assert "set limit_src" in inline_content
    assert "flags timeout" in inline_content
    # Forward chain
    assert "chain forward" in inline_content
    assert "hook forward priority 0" in inline_content
    # Allowlist must check SOURCE only (D-036 / Guide Step 32)
    assert "ip saddr @allow accept" in inline_content
    assert "ip daddr @allow accept" not in inline_content, "Allowlist must not accept destination"

    with open(router_path, "r", encoding="utf-8") as f:
        router_content = f.read()

    # Must be inet family
    assert "table inet ids" in router_content
    assert "set allow" in router_content
    assert "set block_src" in router_content
    assert "set block_dst" in router_content
    assert "flags timeout" in router_content
    assert "ip saddr @allow accept" in router_content
    assert "ip daddr @allow accept" not in router_content


def test_adapter_initialization_invalid_family():
    """Verify ValueError is raised if invalid table family is provided."""
    with pytest.raises(ValueError, match="table_family must be 'bridge' or 'inet'"):
        NftablesAdapter(table_family="invalid_family")


def test_allowlist_immunity_enforced(adapter):
    """Verify management allowlist IPs raise AllowlistProtectedError."""
    # Gateway
    with pytest.raises(AllowlistProtectedError):
        adapter.block("192.168.50.1", direction="src")

    # Sensor
    with pytest.raises(AllowlistProtectedError):
        adapter.block("192.168.50.5", direction="src")

    # Admin PC
    with pytest.raises(AllowlistProtectedError):
        adapter.block("192.168.50.10", direction="src")

    # NVR
    with pytest.raises(AllowlistProtectedError):
        adapter.block("192.168.50.20", direction="dst")

    # Rate limiting allowlist IP is also blocked
    with pytest.raises(AllowlistProtectedError):
        adapter.rate_limit("192.168.50.1")


def test_clamp_duration(adapter):
    """Verify duration is clamped to max_rule_minutes."""
    rec = adapter.block("203.0.113.50", direction="src", minutes=120)
    assert rec["duration_minutes"] == 60  # Clamped to 60


def test_block_and_unblock_source(adapter):
    """Verify blocking and unblocking source IP."""
    target_ip = "198.51.100.99"
    rec = adapter.block(target_ip, direction="src", minutes=30, reason="AUTO_PORTSCAN_REPEATED")

    assert rec["ip"] == target_ip
    assert rec["set"] == "block_src"
    assert rec["direction"] == "src"
    assert rec["duration_minutes"] == 30
    assert rec["reason"] == "AUTO_PORTSCAN_REPEATED"
    assert rec["simulated"] is True

    # Check active rules
    active = adapter.list_active("block_src")
    assert len(active) == 1
    assert active[0]["ip"] == target_ip
    assert active[0]["remaining_minutes"] > 29.0

    # Unblock
    removed = adapter.unblock(target_ip, direction="src")
    assert removed is True
    assert len(adapter.list_active("block_src")) == 0


def test_block_destination_cnc(adapter):
    """Verify blocking destination IP (C&C)."""
    cnc_ip = "198.51.100.200"
    rec = adapter.block(cnc_ip, direction="dst", minutes=45, reason="AUTO_CNC_DEST_BLOCK")

    assert rec["ip"] == cnc_ip
    assert rec["set"] == "block_dst"
    assert rec["direction"] == "dst"
    assert rec["duration_minutes"] == 45

    active = adapter.list_active("block_dst")
    assert len(active) == 1
    assert active[0]["ip"] == cnc_ip
    assert active[0]["direction"] == "dst"

    adapter.unblock(cnc_ip, direction="dst")
    assert len(adapter.list_active("block_dst")) == 0


def test_rate_limit(adapter):
    """Verify rate-limiting source IP."""
    flood_ip = "203.0.113.77"
    rec = adapter.rate_limit(flood_ip, minutes=15, reason="AUTO_DDOS_RATELIMIT")

    assert rec["ip"] == flood_ip
    assert rec["set"] == "limit_src"
    assert rec["duration_minutes"] == 15

    active = adapter.list_active("limit_src")
    assert len(active) == 1
    assert active[0]["ip"] == flood_ip

    adapter.unblock(flood_ip, direction="limit")
    assert len(adapter.list_active("limit_src")) == 0


def test_simulated_expiration():
    """Verify expired rules are pruned on list_active()."""
    adapter = NftablesAdapter(simulate=True)
    target = "203.0.113.88"

    # Block with duration of 0.01 seconds
    adapter.block(target, direction="src", minutes=1)
    # Manually backdate the expiration
    adapter._simulated_sets["block_src"][target]["expires_at"] = time.time() - 5

    active = adapter.list_active("block_src")
    assert len(active) == 0
    assert target not in adapter._simulated_sets["block_src"]


def test_check_and_load_ruleset(adapter):
    """Verify ruleset validation and loading."""
    inline_path = os.path.join("sensor", "ids_inline.nft")
    valid, msg = adapter.check_ruleset(inline_path)
    assert valid is True
    assert "valid" in msg.lower() or "successful" in msg.lower()

    loaded, l_msg = adapter.load_ruleset(inline_path)
    assert loaded is True

    # Non-existent file
    v_fake, m_fake = adapter.check_ruleset("sensor/nonexistent.nft")
    assert v_fake is False


def test_kernel_mode_command_generation():
    """Verify exact CLI commands generated when executing in kernel mode."""
    with patch("platform.system", return_value="Linux"):
        adapter = NftablesAdapter(
            table_family="bridge",
            table_name="ids",
            nft_path="/usr/sbin/nft",
            use_sudo=True,
            simulate=False,
            max_rule_minutes=60,
        )

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

            # 1. Block command
            adapter.block("203.0.113.50", direction="src", minutes=30)
            mock_run.assert_called_with(
                ["sudo", "/usr/sbin/nft", "add", "element", "bridge", "ids", "block_src", "{ 203.0.113.50 timeout 30m }"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )

            # 2. Unblock command
            adapter.unblock("203.0.113.50", direction="src")
            mock_run.assert_called_with(
                ["sudo", "/usr/sbin/nft", "delete", "element", "bridge", "ids", "block_src", "{ 203.0.113.50 }"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )

            # 3. Rate limit command
            adapter.rate_limit("203.0.113.50", minutes=15)
            mock_run.assert_called_with(
                ["sudo", "/usr/sbin/nft", "add", "element", "bridge", "ids", "limit_src", "{ 203.0.113.50 timeout 15m }"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )


def test_kernel_mode_list_active_parsing():
    """Verify parsing of text and JSON output from nft list set."""
    with patch("platform.system", return_value="Linux"):
        adapter = NftablesAdapter(
            table_family="bridge",
            table_name="ids",
            nft_path="/usr/sbin/nft",
            use_sudo=False,
            simulate=False,
        )

        # Mock text output
        text_output = """
        table bridge ids {
            set block_src {
                type ipv4_addr
                flags timeout
                elements = { 198.51.100.22 expires 25m30s, 198.51.100.23 expires 45s }
            }
        }
        """

        with patch("subprocess.run") as mock_run:
            # First json fails, text succeeds
            mock_run.side_effect = [
                MagicMock(returncode=1, stdout="", stderr="no json"),
                MagicMock(returncode=0, stdout=text_output, stderr=""),
            ]

            active = adapter.list_active("block_src")
            assert len(active) == 2
            assert active[0]["ip"] == "198.51.100.22"
            assert active[0]["remaining_seconds"] == (25 * 60) + 30
            assert active[1]["ip"] == "198.51.100.23"
            assert active[1]["remaining_seconds"] == 45


def test_duration_string_parsing():
    """Test helper _parse_duration_string."""
    assert NftablesAdapter._parse_duration_string("30m") == 1800
    assert NftablesAdapter._parse_duration_string("45s") == 45
    assert NftablesAdapter._parse_duration_string("1h20m10s") == 3600 + 1200 + 10
    assert NftablesAdapter._parse_duration_string("10m5s") == 605
