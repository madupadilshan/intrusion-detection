"""
core_engine/firewall/router_adapter.py
======================================
Real-Time Intrusion Detection and Autonomous Response System for IP-Camera IoT Networks
Group 03 - University of Sri Jayewardenepura

Router Firewall Response Adapter for Passive / SPAN Deployment Mode.
Sends remote mitigation commands to the lab router (OpenWrt or Linux router)
via SSH or remote execution.
Proposal Sections 1.2, 2.5, 3.7; Figure 5; Table 7 (FR-06); Step 33.
"""

import json
import logging
import os
import subprocess
import time
from typing import Any, Dict, List, Optional, Set

from core_engine.firewall.base import BaseFirewallAdapter, FirewallError

logger = logging.getLogger("ids.firewall.router")


class RouterAdapter(BaseFirewallAdapter):
    """
    Firewall adapter dispatching mitigation commands to the upstream router in passive SPAN mode.
    """

    def __init__(
        self,
        router_host: Optional[str] = None,
        router_port: Optional[int] = None,
        router_user: Optional[str] = None,
        router_key_file: Optional[str] = None,
        table_family: str = "inet",
        table_name: str = "ids",
        allowlist: Optional[Set[str]] = None,
        max_rule_minutes: int = 60,
        simulate: Optional[bool] = None,
        known_hosts_file: Optional[str] = None,
    ):
        """
        Initialize the router adapter.

        :param router_host: IP or hostname of the lab router (OpenWrt / Linux)
        :param router_port: SSH port (default 22)
        :param router_user: SSH user (default 'root')
        :param router_key_file: Path to SSH private key file
        :param table_family: nftables family on the router (default 'inet')
        :param table_name: table name on the router (default 'ids')
        :param allowlist: Protected IP set
        :param max_rule_minutes: Clamping limit for rules
        :param simulate: Force simulation mode; defaults to True if host not reachable or None
        :param known_hosts_file: Optional known_hosts file for the router's host key (e.g. the
            lab_virtual/ test lab), so the user's own ~/.ssh/known_hosts is not used or changed
        """
        super().__init__(
            name="router_ssh",
            mode="passive_router",
            allowlist=allowlist,
            max_rule_minutes=max_rule_minutes,
        )
        self.router_host = router_host or os.getenv("ROUTER_HOST") or os.getenv("ROUTER_SSH_HOST")
        self.router_port = int(router_port or os.getenv("ROUTER_PORT") or os.getenv("ROUTER_SSH_PORT", 22))
        self.router_user = router_user or os.getenv("ROUTER_USER") or os.getenv("ROUTER_SSH_USER") or "root"
        self.router_key_file = router_key_file or os.getenv("ROUTER_KEY_FILE") or os.getenv("ROUTER_SSH_KEY_PATH")
        self.known_hosts_file = known_hosts_file or os.getenv("ROUTER_KNOWN_HOSTS")
        self.table_family = table_family
        self.table_name = table_name

        if simulate is not None:
            self._is_simulated = bool(simulate)
        elif not self.router_host or self.router_host in ("127.0.0.1", "localhost", "simulation", ""):
            self._is_simulated = True
        else:
            self._is_simulated = False

        self._simulated_rules: Dict[str, Dict[str, Any]] = {}

        if self._is_simulated:
            logger.info(
                "RouterAdapter running in SIMULATION mode (host=%s, family=%s, table=%s)",
                self.router_host, self.table_family, self.table_name
            )
        else:
            logger.info(
                "RouterAdapter running in REMOTE SSH mode target=%s@%s:%d (family=%s, table=%s)",
                self.router_user, self.router_host, self.router_port, self.table_family, self.table_name
            )

    @property
    def is_simulated(self) -> bool:
        return self._is_simulated

    @is_simulated.setter
    def is_simulated(self, value: bool) -> None:
        self._is_simulated = bool(value)

    def _execute_remote(self, remote_cmd: str) -> subprocess.CompletedProcess:
        """Execute a command on the remote router via SSH."""
        cmd = ["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", "-p", str(self.router_port)]
        if self.router_key_file and os.path.exists(self.router_key_file):
            cmd.extend(["-i", self.router_key_file, "-o", "IdentitiesOnly=yes"])
        if self.known_hosts_file:
            # quoted: the path may contain spaces (e.g. "D:\intrusion detection\...")
            cmd.extend(["-o", f'UserKnownHostsFile="{self.known_hosts_file}"', "-o", "StrictHostKeyChecking=yes"])
        cmd.append(f"{self.router_user}@{self.router_host}")
        cmd.append(remote_cmd)

        logger.debug("Executing remote router command: %s", " ".join(cmd))
        return subprocess.run(cmd, capture_output=True, text=True, check=False, timeout=10)

    def block(
        self,
        ip: str,
        direction: str = "src",
        minutes: int = 30,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Block IP on the remote router forward chain.
        """
        ip = ip.strip()
        self.verify_allowlist(ip)
        duration = self.clamp_duration(minutes)
        now = time.time()
        target_set = "block_dst" if direction == "dst" else "block_src"

        if self._is_simulated:
            record = {
                "ip": ip,
                "set": target_set,
                "direction": direction,
                "action": "block",
                "duration_minutes": duration,
                "added_at": now,
                "expires_at": now + (duration * 60),
                "reason": reason or "ROUTER_BLOCK",
                "simulated": True,
            }
            self._simulated_rules[f"block:{direction}:{ip}"] = record
            logger.info(
                "[SIMULATION ROUTER] Blocked %s (%s) for %dm (reason: %s)",
                ip, direction, duration, reason
            )
            return record

        remote_cmd = f"nft add element {self.table_family} {self.table_name} {target_set} '{{ {ip} timeout {duration}m }}'"
        try:
            res = self._execute_remote(remote_cmd)
            if res.returncode != 0:
                raise FirewallError(f"Remote router command failed: {res.stderr or res.stdout} (code {res.returncode})")
        except Exception as exc:
            logger.error("Failed to execute remote router block on %s: %s", self.router_host, exc)
            raise FirewallError(f"Router communication error: {exc}") from exc

        return {
            "ip": ip,
            "set": target_set,
            "direction": direction,
            "action": "block",
            "duration_minutes": duration,
            "added_at": now,
            "expires_at": now + (duration * 60),
            "reason": reason or "ROUTER_BLOCK",
            "simulated": False,
        }

    def rate_limit(
        self,
        ip: str,
        minutes: int = 30,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Rate-limit IP on the remote router.
        """
        ip = ip.strip()
        self.verify_allowlist(ip)
        duration = self.clamp_duration(minutes)
        now = time.time()
        target_set = "limit_src"

        if self._is_simulated:
            record = {
                "ip": ip,
                "set": target_set,
                "direction": "src",
                "action": "rate_limit",
                "duration_minutes": duration,
                "added_at": now,
                "expires_at": now + (duration * 60),
                "reason": reason or "ROUTER_RATE_LIMIT",
                "simulated": True,
            }
            self._simulated_rules[f"rate_limit:src:{ip}"] = record
            logger.info("[SIMULATION ROUTER] Rate-limited %s for %dm (reason: %s)", ip, duration, reason)
            return record

        remote_cmd = f"nft add element {self.table_family} {self.table_name} {target_set} '{{ {ip} timeout {duration}m }}'"
        try:
            res = self._execute_remote(remote_cmd)
            if res.returncode != 0:
                raise FirewallError(f"Remote router command failed: {res.stderr or res.stdout} (code {res.returncode})")
        except Exception as exc:
            logger.error("Failed to execute remote router rate_limit on %s: %s", self.router_host, exc)
            raise FirewallError(f"Router communication error: {exc}") from exc

        return {
            "ip": ip,
            "set": target_set,
            "direction": "src",
            "action": "rate_limit",
            "duration_minutes": duration,
            "added_at": now,
            "expires_at": now + (duration * 60),
            "reason": reason or "ROUTER_RATE_LIMIT",
            "simulated": False,
        }

    def unblock(self, ip: str, direction: str = "src") -> bool:
        """
        Unblock IP on the remote router.
        """
        ip = ip.strip()
        removed = False

        if self._is_simulated:
            keys_to_remove = []
            for k, rec in self._simulated_rules.items():
                if rec["ip"] == ip:
                    if direction == "all" or rec["direction"] == direction or (direction == "limit" and rec["action"] == "rate_limit"):
                        keys_to_remove.append(k)
            for k in keys_to_remove:
                del self._simulated_rules[k]
                removed = True
            return removed

        target_sets = []
        if direction == "src":
            target_sets = ["block_src"]
        elif direction == "dst":
            target_sets = ["block_dst"]
        elif direction == "limit":
            target_sets = ["limit_src"]
        elif direction == "all":
            target_sets = ["block_src", "block_dst", "limit_src"]
        else:
            target_sets = ["block_src"]

        for sname in target_sets:
            remote_cmd = f"nft delete element {self.table_family} {self.table_name} {sname} '{{ {ip} }}'"
            try:
                res = self._execute_remote(remote_cmd)
                if res.returncode == 0:
                    removed = True
            except Exception as exc:
                logger.debug("Failed remote unblock: %s", exc)

        return removed

    def list_active(self, set_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List active rules on the router.
        """
        now = time.time()
        active = []

        if self._is_simulated:
            # Prune expired
            expired_keys = [k for k, r in self._simulated_rules.items() if r["expires_at"] <= now]
            for k in expired_keys:
                del self._simulated_rules[k]

            for r in self._simulated_rules.values():
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
                    "reason": r.get("reason", "ROUTER_RULE"),
                    "simulated": True,
                })
            return active

        # In real SSH mode, read the router's sets (nft JSON). Until 11 Nov 2026 the answer was not
        # read and this always returned [], so startup recovery could not see the router's rules
        # (orphan and allowlist clean-up never happened) (D-056).
        remote_cmd = f"nft -j list table {self.table_family} {self.table_name}"
        try:
            res = self._execute_remote(remote_cmd)
            if res.returncode == 0 and (res.stdout or "").strip():
                active = self.parse_nft_table(json.loads(res.stdout), set_name)
            else:
                logger.warning("Router rule list failed on %s: %s", self.router_host, (res.stderr or res.stdout or "").strip())
        except Exception as exc:
            logger.warning("Remote list table failed: %s", exc)

        return active

    @staticmethod
    def parse_nft_table(data: Dict[str, Any], set_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Rules from `nft -j list table ...`: one entry per element of block_src, block_dst, limit_src."""
        rules: List[Dict[str, Any]] = []
        for item in data.get("nftables", []):
            s = item.get("set")
            if not s or s.get("name") not in ("block_src", "block_dst", "limit_src"):
                continue
            if set_name and s.get("name") != set_name:
                continue
            for elem in s.get("elem", []) or []:
                if isinstance(elem, dict) and "elem" in elem:
                    ip, expires = elem["elem"].get("val"), int(elem["elem"].get("expires", 0) or 0)
                else:
                    ip, expires = elem, 0
                if not ip:
                    continue
                rules.append({
                    "ip": str(ip),
                    "set": s["name"],
                    "direction": "dst" if s["name"] == "block_dst" else "src",
                    "action": "rate_limit" if s["name"] == "limit_src" else "block",
                    "remaining_seconds": expires,
                    "remaining_minutes": round(expires / 60.0, 1),
                    "reason": "ROUTER_SET",
                    "simulated": False,
                })
        return rules

