"""
core_engine/firewall/simulation_adapter.py
==========================================
Real-Time Intrusion Detection and Autonomous Response System for IP-Camera IoT Networks
Group 03 - University of Sri Jayewardenepura

Development Simulation Firewall Adapter.
Tracks all mitigation decisions in memory without modifying host OS network interfaces.
Conforms to Golden Rule / Step 33 note: 'Never report simulation results as real blocking.'
Explicitly flags all actions with is_simulated=True and simulated=True.
"""

import logging
import time
from typing import Any, Dict, List, Optional, Set

from core_engine.firewall.base import BaseFirewallAdapter

logger = logging.getLogger("ids.firewall.simulation")


class SimulationAdapter(BaseFirewallAdapter):
    """
    In-memory simulation response adapter for development, unit testing, and Windows environments.
    """

    def __init__(
        self,
        allowlist: Optional[Set[str]] = None,
        max_rule_minutes: int = 60,
    ):
        super().__init__(
            name="simulation",
            mode="simulation",
            allowlist=allowlist,
            max_rule_minutes=max_rule_minutes,
        )
        # In-memory storage: { "key": rule_dict } where key = f"{action_type}:{direction}:{ip}"
        self._rules: Dict[str, Dict[str, Any]] = {}
        logger.info(
            "SimulationAdapter initialized (max_minutes=%d, allowlist_count=%d)",
            self.max_rule_minutes, len(self.allowlist)
        )

    @property
    def is_simulated(self) -> bool:
        """Simulation adapter is always simulated."""
        return True

    def block(
        self,
        ip: str,
        direction: str = "src",
        minutes: int = 30,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simulate blocking an IP for a bounded duration.
        """
        ip = ip.strip()
        self.verify_allowlist(ip)
        duration = self.clamp_duration(minutes)
        now = time.time()

        key = f"block:{direction}:{ip}"
        record = {
            "ip": ip,
            "set": "block_dst" if direction == "dst" else "block_src",
            "direction": direction,
            "action": "block",
            "duration_minutes": duration,
            "added_at": now,
            "expires_at": now + (duration * 60),
            "reason": reason or "SIMULATED_BLOCK",
            "simulated": True,
        }
        self._rules[key] = record
        logger.info(
            "[SIMULATION] Blocked %s (direction=%s, duration=%dm, reason=%s)",
            ip, direction, duration, reason
        )
        return record

    def rate_limit(
        self,
        ip: str,
        minutes: int = 30,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Simulate rate-limiting transit traffic from an IP.
        """
        ip = ip.strip()
        self.verify_allowlist(ip)
        duration = self.clamp_duration(minutes)
        now = time.time()

        key = f"rate_limit:src:{ip}"
        record = {
            "ip": ip,
            "set": "limit_src",
            "direction": "src",
            "action": "rate_limit",
            "duration_minutes": duration,
            "added_at": now,
            "expires_at": now + (duration * 60),
            "reason": reason or "SIMULATED_RATE_LIMIT",
            "simulated": True,
        }
        self._rules[key] = record
        logger.info(
            "[SIMULATION] Rate-limited %s (duration=%dm, reason=%s)",
            ip, duration, reason
        )
        return record

    def unblock(self, ip: str, direction: str = "src") -> bool:
        """
        Simulate removing a rule for an IP.
        """
        ip = ip.strip()
        removed = False

        keys_to_remove = []
        for key, rec in self._rules.items():
            if rec["ip"] == ip:
                if direction == "all" or rec["direction"] == direction or (direction == "limit" and rec["action"] == "rate_limit"):
                    keys_to_remove.append(key)

        for k in keys_to_remove:
            del self._rules[k]
            removed = True

        if removed:
            logger.info("[SIMULATION] Removed mitigation rules for %s (direction=%s)", ip, direction)
        return removed

    def list_active(self, set_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List active simulated rules, auto-pruning expired ones.
        """
        now = time.time()
        active = []

        # Prune expired
        expired_keys = [k for k, r in self._rules.items() if r["expires_at"] <= now]
        for k in expired_keys:
            del self._rules[k]

        for r in self._rules.values():
            if set_name and r.get("set") != set_name:
                continue

            rem_sec = max(0, int(r["expires_at"] - now))
            active.append({
                "ip": r["ip"],
                "set": r.get("set", "block_src"),
                "direction": r.get("direction", "src"),
                "action": r.get("action", "block"),
                "duration_minutes": r.get("duration_minutes", 30),
                "remaining_seconds": rem_sec,
                "remaining_minutes": round(rem_sec / 60.0, 1),
                "reason": r.get("reason", "SIMULATED"),
                "simulated": True,
            })

        return active

    def clear(self) -> None:
        """Clear all simulated rules (utility for testing)."""
        self._rules.clear()

