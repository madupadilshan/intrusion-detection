"""
core_engine/firewall/__init__.py
================================
Real-Time Intrusion Detection and Autonomous Response System for IP-Camera IoT Networks
Group 03 - University of Sri Jayewardenepura

Firewall Adapter Package and Factory.
Exports unified response adapters and a factory function to instantiate the
appropriate adapter based on deployment topology and environment configuration.
"""

import logging
import os
import platform
import shutil
from typing import Any, Dict, Optional, Set

from core_engine.firewall.base import (
    BaseFirewallAdapter,
    FirewallError,
    AllowlistImmunityError,
)
from core_engine.firewall.nftables_adapter import (
    NftablesAdapter,
    NftablesError,
    AllowlistProtectedError,
)
from core_engine.firewall.router_adapter import RouterAdapter
from core_engine.firewall.simulation_adapter import SimulationAdapter

logger = logging.getLogger("ids.firewall")

__all__ = [
    "BaseFirewallAdapter",
    "FirewallError",
    "AllowlistImmunityError",
    "NftablesAdapter",
    "NftablesError",
    "AllowlistProtectedError",
    "RouterAdapter",
    "SimulationAdapter",
    "get_firewall_adapter",
    "firewall_config_from_settings",
]


def firewall_config_from_settings(settings: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Build the adapter configuration from settings.yaml in ONE place.

    - The adapter type comes from `response.adapter` (router | nftables | simulation).
      `firewall.type` is only a fallback; if both are set and differ, a warning is
      logged and `response.adapter` is used.
    - The nftables table family defaults to `inet` for the router (passive mode) and
      `bridge` for the sensor itself (inline mode), unless `firewall.table_family` is set.
    - Router host, port, user and key may be in the `firewall` section; otherwise the
      RouterAdapter reads them from the environment (.env).
    """
    settings = settings or {}
    fw = dict(settings.get("firewall") or {})
    response_adapter = (settings.get("response") or {}).get("adapter")
    fw_type = fw.get("type")
    if response_adapter and fw_type and str(response_adapter).lower() != str(fw_type).lower():
        logger.warning(
            "settings.yaml: response.adapter=%s and firewall.type=%s differ; using response.adapter.",
            response_adapter, fw_type,
        )
    chosen = str(response_adapter or fw_type or "auto").lower()
    fw["type"] = chosen
    if "table_family" not in fw:
        fw["table_family"] = "inet" if chosen == "router" else "bridge"
    return fw


def get_firewall_adapter(
    config: Optional[Dict[str, Any]] = None,
    allowlist: Optional[Set[str]] = None,
    max_rule_minutes: int = 60,
) -> BaseFirewallAdapter:
    """
    Factory function instantiating the appropriate firewall adapter.

    :param config: Configuration dictionary (can contain 'type', 'table_family', 'table_name', 'host', etc.)
    :param allowlist: Protected IP addresses
    :param max_rule_minutes: Maximum mitigation duration
    :return: Concrete BaseFirewallAdapter instance
    """
    cfg = config or {}
    adapter_type = cfg.get("type") or cfg.get("adapter") or os.getenv("FIREWALL_TYPE", "auto")
    adapter_type = str(adapter_type).lower()

    table_family = cfg.get("table_family", "bridge")
    table_name = cfg.get("table_name", "ids")
    use_sudo = cfg.get("use_sudo", True)

    if adapter_type == "nftables":
        return NftablesAdapter(
            table_family=table_family,
            table_name=table_name,
            nft_path=cfg.get("nft_path"),
            use_sudo=use_sudo,
            simulate=cfg.get("simulate"),
            allowlist=allowlist,
            max_rule_minutes=max_rule_minutes,
        )

    if adapter_type == "router":
        # None lets RouterAdapter read ROUTER_HOST / ROUTER_PORT / ROUTER_USER /
        # ROUTER_KEY_FILE (or the ROUTER_SSH_* names) from the environment.
        return RouterAdapter(
            router_host=cfg.get("router_host") or cfg.get("host"),
            router_port=int(cfg["router_port"]) if cfg.get("router_port") else None,
            router_user=cfg.get("router_user"),
            router_key_file=cfg.get("router_key_file"),
            table_family=cfg.get("table_family", "inet"),
            table_name=table_name,
            allowlist=allowlist,
            max_rule_minutes=max_rule_minutes,
            simulate=cfg.get("simulate"),
        )

    if adapter_type == "simulation":
        return SimulationAdapter(
            allowlist=allowlist,
            max_rule_minutes=max_rule_minutes,
        )

    # 'auto' detection
    if platform.system().lower() == "linux" and shutil.which("nft"):
        logger.info("Auto-detected Linux environment with nft binary -> instantiating NftablesAdapter")
        return NftablesAdapter(
            table_family=table_family,
            table_name=table_name,
            use_sudo=use_sudo,
            allowlist=allowlist,
            max_rule_minutes=max_rule_minutes,
        )

    logger.info("Auto-selected SimulationAdapter for development / non-root environment")
    return SimulationAdapter(
        allowlist=allowlist,
        max_rule_minutes=max_rule_minutes,
    )

