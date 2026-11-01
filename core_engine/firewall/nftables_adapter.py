"""
core_engine/firewall/nftables_adapter.py
========================================
Real-Time Intrusion Detection and Autonomous Response System for IP-Camera IoT Networks
Group 03 - University of Sri Jayewardenepura

Nftables Linux Firewall Adapter.
Translates abstract mitigation decisions into concrete nftables kernel set elements
with explicit timeout flags for automatic expiry and zero permanent network disruption.

Supports:
  - Inline bridge mode: 'table bridge ids' (L2 bridging on Linux sensor)
  - Passive router mode: 'table inet ids' (L3 routing on lab router / OpenWrt)
  - Timed elements: 'add element <family> ids <set> { <ip> timeout <duration>m }'
  - Set queries: 'list set <family> ids <set>' with remaining timeout parsing
  - Cross-platform simulation fallback: Full in-memory state tracking when nft binary is absent
  - Allowlist immunity enforcement prior to kernel dispatch
"""

import json
import logging
import os
import platform
import re
import shutil
import subprocess
import time
from typing import Any, Dict, List, Optional, Set, Tuple

from core_engine.firewall.base import (
    BaseFirewallAdapter,
    FirewallError,
    AllowlistImmunityError,
)

logger = logging.getLogger("ids.nftables_adapter")


class NftablesError(FirewallError):
    """Base exception for nftables operations."""
    pass


class AllowlistProtectedError(AllowlistImmunityError, NftablesError):
    """Raised when an attempt is made to block an allowlisted IP."""
    pass


class NftablesAdapter(BaseFirewallAdapter):
    """
    Adapter interfacing with the Linux nftables kernel subsystem using timed sets.
    """

    def __init__(
        self,
        table_family: str = "bridge",
        table_name: str = "ids",
        nft_path: Optional[str] = None,
        use_sudo: bool = True,
        simulate: Optional[bool] = None,
        allowlist: Optional[Set[str]] = None,
        max_rule_minutes: int = 60,
    ):
        """
        Initialize the nftables adapter.

        :param table_family: 'bridge' (sensor bridge forward) or 'inet' (router forward)
        :param table_name: nftables table name (default 'ids')
        :param nft_path: path to nft binary (detected from PATH or /usr/sbin/nft)
        :param use_sudo: whether to prefix commands with sudo (on Linux)
        :param simulate: force simulation mode; if None, autodetects based on OS and binary availability
        :param allowlist: set of IPs permanently immune to blocking
        :param max_rule_minutes: upper bound for rule duration (default 60 mins)
        """
        fam = table_family.lower()
        if fam not in ("bridge", "inet"):
            raise ValueError(f"table_family must be 'bridge' or 'inet', got '{table_family}'")

        mode = "inline" if fam == "bridge" else "passive_router"
        super().__init__(
            name=f"nftables_{fam}",
            mode=mode,
            allowlist=allowlist,
            max_rule_minutes=max_rule_minutes,
        )

        self.table_family = fam
        self.table_name = table_name
        self.use_sudo = use_sudo and (platform.system().lower() != "windows")

        # Detect nft binary
        detected_path = nft_path or shutil.which("nft") or "/usr/sbin/nft"
        self.nft_path = detected_path

        # Determine if simulation mode is active
        if simulate is not None:
            self._is_simulated = bool(simulate)
        else:
            if platform.system().lower() == "windows":
                self._is_simulated = True
            elif not os.path.exists(detected_path) or not os.access(detected_path, os.X_OK):
                self._is_simulated = True
            else:
                self._is_simulated = False

        if self._is_simulated:
            logger.info(
                "NftablesAdapter running in SIMULATION mode (family=%s, table=%s, max_minutes=%d)",
                self.table_family, self.table_name, self.max_rule_minutes
            )
        else:
            logger.info(
                "NftablesAdapter running in KERNEL mode via '%s' (family=%s, table=%s, sudo=%s)",
                self.nft_path, self.table_family, self.table_name, self.use_sudo
            )

        # In-memory storage for simulation mode: { set_name: { ip: rule_dict } }
        self._simulated_sets: Dict[str, Dict[str, Any]] = {
            "block_src": {},
            "block_dst": {},
            "limit_src": {},
        }

    @property
    def is_simulated(self) -> bool:
        return self._is_simulated

    @is_simulated.setter
    def is_simulated(self, value: bool) -> None:
        self._is_simulated = bool(value)

    def _verify_allowlist(self, ip: str) -> None:
        """Backward-compatible allowlist check."""
        try:
            self.verify_allowlist(ip)
        except AllowlistImmunityError as err:
            raise AllowlistProtectedError(str(err)) from err

    def _clamp_duration(self, minutes: int) -> int:
        """Backward-compatible duration clamping."""
        return self.clamp_duration(minutes)

    def _build_command(self, args: List[str]) -> List[str]:
        """Build command list prepending sudo if required."""
        cmd = []
        if self.use_sudo:
            cmd.append("sudo")
        cmd.append(self.nft_path)
        cmd.extend(args)
        return cmd

    def _execute(self, args: List[str]) -> Tuple[int, str, str]:
        """Execute nft command via subprocess."""
        cmd = self._build_command(args)
        cmd_str = " ".join(cmd)
        logger.debug("Executing nftables command: %s", cmd_str)

        try:
            res = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            return res.returncode, res.stdout, res.stderr
        except FileNotFoundError:
            logger.warning("nft binary not found at '%s', switching to simulation", self.nft_path)
            self.is_simulated = True
            return 127, "", "nft binary not found"
        except subprocess.TimeoutExpired:
            logger.error("nft command timed out: %s", cmd_str)
            return 124, "", "Command timed out"
        except Exception as exc:
            logger.error("nft command error: %s (%s)", cmd_str, exc)
            return 1, "", str(exc)

    def block(
        self,
        ip: str,
        direction: str = "src",
        minutes: int = 30,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a timed block rule to nftables set (block_src or block_dst).

        :param ip: IPv4 address to drop
        :param direction: 'src' (default) or 'dst'
        :param minutes: duration in minutes
        :param reason: justification or reason code (e.g. 'AUTO_PORTSCAN_REPEATED')
        :return: rule details dictionary
        """
        ip = ip.strip()
        self._verify_allowlist(ip)
        duration = self._clamp_duration(minutes)

        target_set = "block_dst" if direction == "dst" else "block_src"

        if self.is_simulated:
            now = time.time()
            record = {
                "ip": ip,
                "set": target_set,
                "direction": direction,
                "duration_minutes": duration,
                "added_at": now,
                "expires_at": now + (duration * 60),
                "reason": reason or "BLOCKED",
                "simulated": True,
            }
            self._simulated_sets[target_set][ip] = record
            logger.info("[SIMULATION] Blocked %s in %s for %dm (reason: %s)", ip, target_set, duration, reason)
            return record

        # nft add element <family> <table_name> <set_name> '{ <ip> timeout <duration>m }'
        element_spec = f"{{ {ip} timeout {duration}m }}"
        args = ["add", "element", self.table_family, self.table_name, target_set, element_spec]

        ret, out, err = self._execute(args)
        if ret != 0:
            raise NftablesError(f"Failed to add nftables block element: {err or out} (code {ret})")

        logger.info("Kernel blocked %s in set %s for %dm (reason: %s)", ip, target_set, duration, reason)
        return {
            "ip": ip,
            "set": target_set,
            "direction": direction,
            "duration_minutes": duration,
            "added_at": time.time(),
            "expires_at": time.time() + (duration * 60),
            "reason": reason or "BLOCKED",
            "simulated": False,
        }

    def rate_limit(
        self,
        ip: str,
        minutes: int = 30,
        reason: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Add a timed rate-limit rule to nftables set (limit_src).

        :param ip: IPv4 address to rate-limit
        :param minutes: duration in minutes
        :param reason: justification or reason code (e.g. 'AUTO_DDOS_RATELIMIT')
        :return: rule details dictionary
        """
        ip = ip.strip()
        self._verify_allowlist(ip)
        duration = self._clamp_duration(minutes)
        target_set = "limit_src"

        if self.is_simulated:
            now = time.time()
            record = {
                "ip": ip,
                "set": target_set,
                "direction": "src",
                "duration_minutes": duration,
                "added_at": now,
                "expires_at": now + (duration * 60),
                "reason": reason or "RATE_LIMITED",
                "simulated": True,
            }
            self._simulated_sets[target_set][ip] = record
            logger.info("[SIMULATION] Rate-limited %s in %s for %dm (reason: %s)", ip, target_set, duration, reason)
            return record

        element_spec = f"{{ {ip} timeout {duration}m }}"
        args = ["add", "element", self.table_family, self.table_name, target_set, element_spec]

        ret, out, err = self._execute(args)
        if ret != 0:
            raise NftablesError(f"Failed to add nftables rate_limit element: {err or out} (code {ret})")

        logger.info("Kernel rate-limited %s in set %s for %dm (reason: %s)", ip, target_set, duration, reason)
        return {
            "ip": ip,
            "set": target_set,
            "direction": "src",
            "duration_minutes": duration,
            "added_at": time.time(),
            "expires_at": time.time() + (duration * 60),
            "reason": reason or "RATE_LIMITED",
            "simulated": False,
        }

    def unblock(self, ip: str, direction: str = "src") -> bool:
        """
        Remove an IP element from nftables set (block_src, block_dst, or limit_src).

        :param ip: IPv4 address to remove
        :param direction: 'src', 'dst', or 'all'
        :return: True if an element was removed, False if not found
        """
        ip = ip.strip()
        removed = False

        sets_to_check = []
        if direction == "src":
            sets_to_check = ["block_src"]
        elif direction == "dst":
            sets_to_check = ["block_dst"]
        elif direction == "limit":
            sets_to_check = ["limit_src"]
        elif direction == "all":
            sets_to_check = ["block_src", "block_dst", "limit_src"]
        else:
            sets_to_check = ["block_src"]

        for sname in sets_to_check:
            if self.is_simulated:
                if ip in self._simulated_sets[sname]:
                    del self._simulated_sets[sname][ip]
                    logger.info("[SIMULATION] Unblocked %s from set %s", ip, sname)
                    removed = True
            else:
                # nft delete element <family> <table_name> <set_name> '{ <ip> }'
                element_spec = f"{{ {ip} }}"
                args = ["delete", "element", self.table_family, self.table_name, sname, element_spec]
                ret, out, err = self._execute(args)
                if ret == 0:
                    logger.info("Kernel unblocked %s from set %s", ip, sname)
                    removed = True
                else:
                    # Common case: element not found or expired; not an unrecoverable failure
                    logger.debug("Element %s not in set %s: %s", ip, sname, err or out)

        return removed

    def list_active(self, set_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all currently active rules with calculated remaining seconds.

        :param set_name: filter by set name ('block_src', 'block_dst', 'limit_src') or None for all
        :return: list of active rule dictionaries
        """
        now = time.time()
        active_rules = []

        sets = [set_name] if set_name else ["block_src", "block_dst", "limit_src"]

        if self.is_simulated:
            for sname in sets:
                if sname not in self._simulated_sets:
                    continue
                # Prune expired
                expired_ips = [
                    ip for ip, rec in self._simulated_sets[sname].items()
                    if rec["expires_at"] <= now
                ]
                for exp_ip in expired_ips:
                    del self._simulated_sets[sname][exp_ip]

                for ip, rec in self._simulated_sets[sname].items():
                    rem = max(0, int(rec["expires_at"] - now))
                    active_rules.append({
                        "ip": ip,
                        "set": sname,
                        "direction": rec.get("direction", "src"),
                        "duration_minutes": rec.get("duration_minutes", 30),
                        "remaining_seconds": rem,
                        "remaining_minutes": round(rem / 60.0, 1),
                        "reason": rec.get("reason", "ACTIVE"),
                        "simulated": True,
                    })
            return active_rules

        # Kernel mode: query nft list set for each set
        for sname in sets:
            # Query JSON if possible: nft -j list set <family> <table_name> <set_name>
            args_json = ["-j", "list", "set", self.table_family, self.table_name, sname]
            ret, out, err = self._execute(args_json)
            if ret == 0 and out.strip():
                try:
                    data = json.loads(out)
                    elements = self._parse_nft_json_elements(data, sname)
                    active_rules.extend(elements)
                    continue
                except Exception as exc:
                    logger.debug("Failed parsing JSON output: %s; falling back to text parsing", exc)

            # Fallback to text parsing: nft list set <family> <table_name> <set_name>
            args_txt = ["list", "set", self.table_family, self.table_name, sname]
            ret, out, err = self._execute(args_txt)
            if ret == 0:
                elements = self._parse_nft_text_elements(out, sname)
                active_rules.extend(elements)

        return active_rules

    def _parse_nft_json_elements(self, data: Dict[str, Any], set_name: str) -> List[Dict[str, Any]]:
        """Parse structured elements from 'nft -j list set' JSON output."""
        results = []
        now = time.time()
        for item in data.get("nftables", []):
            if "set" in item and item["set"].get("name") == set_name:
                elem_list = item["set"].get("elem", [])
                for elem in elem_list:
                    if isinstance(elem, dict) and "elem" in elem:
                        val = elem["elem"].get("val")
                        expires = elem["elem"].get("expires", 0)
                        if val:
                            results.append({
                                "ip": str(val),
                                "set": set_name,
                                "direction": "dst" if set_name == "block_dst" else "src",
                                "remaining_seconds": int(expires),
                                "remaining_minutes": round(int(expires) / 60.0, 1),
                                "reason": "KERNEL_SET",
                                "simulated": False,
                            })
                    elif isinstance(elem, str):
                        results.append({
                            "ip": elem,
                            "set": set_name,
                            "direction": "dst" if set_name == "block_dst" else "src",
                            "remaining_seconds": 0,
                            "remaining_minutes": 0,
                            "reason": "KERNEL_SET",
                            "simulated": False,
                        })
        return results

    def _parse_nft_text_elements(self, text: str, set_name: str) -> List[Dict[str, Any]]:
        """Parse text elements and remaining timeouts from 'nft list set' output."""
        results = []
        # Matches patterns like:
        # elements = { 10.10.10.50 expires 28m32s, 10.10.10.51 expires 15s }
        match = re.search(r"elements\s*=\s*\{([^}]*)\}", text, re.DOTALL)
        if not match:
            return results

        elements_body = match.group(1)
        for raw_elem in elements_body.split(","):
            raw_elem = raw_elem.strip()
            if not raw_elem:
                continue

            # Extract IP and optional expires string
            parts = raw_elem.split()
            if not parts:
                continue
            ip = parts[0]
            rem_sec = 0

            # Find 'expires <duration>'
            if "expires" in parts:
                exp_idx = parts.index("expires")
                if exp_idx + 1 < len(parts):
                    exp_str = parts[exp_idx + 1]
                    rem_sec = self._parse_duration_string(exp_str)

            results.append({
                "ip": ip,
                "set": set_name,
                "direction": "dst" if set_name == "block_dst" else "src",
                "remaining_seconds": rem_sec,
                "remaining_minutes": round(rem_sec / 60.0, 1),
                "reason": "KERNEL_SET",
                "simulated": False,
            })
        return results

    @staticmethod
    def _parse_duration_string(dur_str: str) -> int:
        """Parse nftables duration strings like '28m32s', '50s', '1h5m' into seconds."""
        total = 0
        h_match = re.search(r"(\d+)h", dur_str)
        m_match = re.search(r"(\d+)m", dur_str)
        s_match = re.search(r"(\d+)s", dur_str)

        if h_match:
            total += int(h_match.group(1)) * 3600
        if m_match:
            total += int(m_match.group(1)) * 60
        if s_match:
            total += int(s_match.group(1))
        return total

    def check_ruleset(self, file_path: str) -> Tuple[bool, str]:
        """
        Check syntax of a ruleset file with 'nft -c -f <file_path>'.

        :param file_path: path to .nft rule file
        :return: (is_valid, message)
        """
        if not os.path.exists(file_path):
            return False, f"Rule file '{file_path}' does not exist"

        if self.is_simulated:
            # Basic textual syntax validation for simulation
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                if "table" not in content or "chain" not in content:
                    return False, "File missing required 'table' or 'chain' definitions"
                return True, "[SIMULATION] Rule file structure valid"
            except Exception as exc:
                return False, f"Error reading file: {exc}"

        args = ["-c", "-f", file_path]
        ret, out, err = self._execute(args)
        if ret == 0:
            return True, "Syntax check successful"
        return False, err or out

    def load_ruleset(self, file_path: str) -> Tuple[bool, str]:
        """
        Load a ruleset file into the kernel with 'nft -f <file_path>'.

        :param file_path: path to .nft rule file
        :return: (success, message)
        """
        valid, msg = self.check_ruleset(file_path)
        if not valid:
            return False, f"Syntax validation failed: {msg}"

        if self.is_simulated:
            logger.info("[SIMULATION] Loaded ruleset file '%s'", file_path)
            return True, f"[SIMULATION] Ruleset '{file_path}' loaded successfully"

        args = ["-f", file_path]
        ret, out, err = self._execute(args)
        if ret == 0:
            logger.info("Kernel loaded ruleset file '%s'", file_path)
            return True, f"Ruleset '{file_path}' loaded successfully"
        return False, err or out
