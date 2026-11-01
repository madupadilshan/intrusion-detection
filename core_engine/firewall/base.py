"""
core_engine/firewall/base.py
============================
Real-Time Intrusion Detection and Autonomous Response System for IP-Camera IoT Networks
Group 03 - University of Sri Jayewardenepura

Abstract Base Class for Firewall Response Adapters.
Defines the unified mitigation interface across deployment topologies:
  - Inline bridge filtering (Linux sensor L2 forward)
  - Passive router mitigation (OpenWrt / Linux L3 router forward via SSH/API)
  - Development simulation (in-memory state tracking)
"""

from abc import ABC, abstractmethod
import logging
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("ids.firewall.base")


class FirewallError(Exception):
    """Base exception for all firewall response adapters."""
    pass


class AllowlistImmunityError(FirewallError):
    """Raised when an attempt is made to block or rate-limit an allowlisted IP."""
    pass


class BaseFirewallAdapter(ABC):
    """
    Common abstract interface for all intrusion response adapters.
    """

    DEFAULT_ALLOWLIST = {
        "192.168.50.1",   # Gateway router
        "192.168.50.5",   # IDS Sensor
        "192.168.50.10",  # Security Admin PC
        "192.168.50.20",  # Network Video Recorder (NVR)
    }

    def __init__(
        self,
        name: str,
        mode: str,
        allowlist: Optional[Set[str]] = None,
        max_rule_minutes: int = 60,
    ):
        """
        Initialize the base firewall adapter.

        :param name: Human-readable adapter name (e.g. 'nftables_bridge', 'openwrt_router', 'simulation')
        :param mode: Deployment mode ('inline', 'passive_router', 'simulation')
        :param allowlist: Set of IP addresses permanently immune to blocking
        :param max_rule_minutes: Maximum duration for any dynamic firewall rule (clamping limit)
        """
        self.name = name
        self.mode = mode
        self.max_rule_minutes = int(max_rule_minutes)
        if allowlist is None:
            self.allowlist = set(self.DEFAULT_ALLOWLIST)
        else:
            self.allowlist = set(allowlist)

    @property
    @abstractmethod
    def is_simulated(self) -> bool:
        """Returns True if the adapter operates in simulation / mock mode."""
        pass

    def verify_allowlist(self, ip: str) -> None:
        """
        Verify that the IP is not allowlist protected.
        Raises AllowlistImmunityError if the IP is protected.
        """
        clean_ip = ip.strip()
        if clean_ip in self.allowlist:
            raise AllowlistImmunityError(
                f"IP address '{clean_ip}' is protected by the management allowlist and cannot be mitigated."
            )

    def clamp_duration(self, minutes: int) -> int:
        """Clamp requested rule duration to the configured maximum."""
        mins = max(1, int(minutes))
        if mins > self.max_rule_minutes:
            logger.warning(
                "[%s] Duration %dm exceeds max %dm; clamping to %dm",
                self.name, mins, self.max_rule_minutes, self.max_rule_minutes
            )
            return self.max_rule_minutes
        return mins

    @abstractmethod
    def block(
        self,
        ip: str,
        direction: str = "src",
        minutes: int = 30,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Block transit traffic from or to the specified IP for a bounded duration.

        :param ip: Target IPv4 address
        :param direction: 'src' (default, block external attacker) or 'dst' (block C&C destination)
        :param minutes: Duration in minutes
        :param reason: Reason code or justification note
        :return: Rule details dictionary
        """
        pass

    @abstractmethod
    def rate_limit(
        self,
        ip: str,
        minutes: int = 30,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rate-limit transit traffic from the specified IP for a bounded duration.

        :param ip: Target IPv4 address
        :param minutes: Duration in minutes
        :param reason: Reason code or justification note
        :return: Rule details dictionary
        """
        pass

    @abstractmethod
    def unblock(self, ip: str, direction: str = "src") -> bool:
        """
        Remove an active mitigation rule for the specified IP.

        :param ip: Target IPv4 address
        :param direction: 'src', 'dst', 'limit', or 'all'
        :return: True if an active rule was removed, False if not found
        """
        pass

    @abstractmethod
    def list_active(self, set_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Retrieve all currently active mitigation rules with calculated remaining durations.

        :param set_name: Optional filter by set name
        :return: List of active rule dictionaries
        """
        pass

