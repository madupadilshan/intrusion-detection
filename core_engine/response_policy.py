#!/usr/bin/env python3
"""
core_engine/response_policy.py - Response Policy and Safety Guardrail Engine (Step 31).
======================================================================================

Governing Standards & Requirements:
- Group 03 Proposal: Section 2.5, Section 3.4, Section 3.7; Table 5 ("Response Policy");
  Table 7: Requirements FR-06, FR-07; Research Question RQ5; Supervisor Checkpoint C7.
- Step-by-Step Guide: Step 31 ("Write the response policy").

Key Capabilities:
1. Direction-aware mitigation logic:
   - Benign: never block.
   - Port scan: block external scanner source IP only after repeated probe sweeps.
   - DDoS: rate-limit or block external flood source IP after threshold exceedance
     (rate-limit when the class is in `rate_limit_classes`, decision D-055).
   - C&C: block external destination server IP or isolate device.
   - Malware / download: quarantine or block based on direction and confidence.
   - Low confidence: alert only.
2. Seven non-bypassable safety checks:
   - Checkpoint 1: Master switch `auto_response` must be True.
   - Checkpoint 2: Calibrated confidence >= minimum threshold.
   - Checkpoint 3: Management allowlist immunity (target never on allowlist).
   - Checkpoint 4: Private network target protection (internal cameras protected).
   - Checkpoint 5: Sliding-window repeat coalescing (`min_repeats` within `repeat_window_seconds`).
   - Checkpoint 6: Clamped, bounded rule expiry (`max_rule_minutes`).
   - Checkpoint 7: Explicit reason codes (`AUTO_*` or `SKIP_*`) and audit payload generation.
"""

from __future__ import annotations

import ipaddress
import logging
import time
from collections import defaultdict, deque
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("core_engine.response_policy")

# Canonical default allowlist (Proposal Section 3.7)
DEFAULT_ALLOWLIST = [
    "192.168.50.1",   # Lab gateway / router
    "192.168.50.5",   # IDS sensor
    "192.168.50.10",  # Admin workstation
    "192.168.50.20",  # NVR
]

# Canonical Reason Codes
REASON_AUTO_PORTSCAN = "AUTO_PORTSCAN_REPEATED"
REASON_AUTO_DDOS_BLOCK = "AUTO_DDOS_BLOCK"
REASON_AUTO_DDOS_RATELIMIT = "AUTO_DDOS_RATELIMIT"
REASON_AUTO_CNC_DEST_BLOCK = "AUTO_CNC_DEST_BLOCK"
REASON_AUTO_MALWARE_BLOCK = "AUTO_MALWARE_BLOCK"
REASON_MANUAL_BLOCK = "MANUAL_BLOCK"
REASON_MANUAL_UNBLOCK = "MANUAL_UNBLOCK"
REASON_RULE_EXPIRED = "RULE_EXPIRED"

# Skip Reason Codes (Safety Guardrail Invariants)
REASON_SKIP_BENIGN = "SKIP_BENIGN"
REASON_SKIP_AUTO_DISABLED = "SKIP_AUTO_RESPONSE_DISABLED"
REASON_SKIP_LOW_CONF = "SKIP_LOW_CONFIDENCE"
REASON_SKIP_ALLOWLIST = "SKIP_ALLOWLIST"
REASON_SKIP_PRIVATE_TARGET = "SKIP_PRIVATE_TARGET"
REASON_SKIP_NOT_REPEATED = "SKIP_NOT_REPEATED"


PRIVATE_NETWORKS = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
]


def is_private_ip(ip_str: str) -> bool:
    """
    Check if an IPv4/IPv6 string belongs to RFC 1918 or loopback private subnets.

    Args:
        ip_str: IP address string.

    Returns:
        True if RFC 1918 private or loopback, False otherwise.
    """
    if not ip_str:
        return False
    try:
        ip_obj = ipaddress.ip_address(ip_str.strip())
        return any(ip_obj in net for net in PRIVATE_NETWORKS)
    except ValueError:
        return False


@dataclass
class PolicyDecision:
    """Standardized mitigation decision evaluated against safety guardrails."""

    should_act: bool = False
    action_type: str = "none"  # block | rate_limit | isolate | none
    target_ip: str = ""
    direction: str = "inbound"  # inbound | outbound
    duration_minutes: int = 0
    reason_code: str = REASON_SKIP_BENIGN
    evidence_note: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def action(self) -> str:
        return self.action_type

    @property
    def reason(self) -> str:
        return self.reason_code

    @property
    def target_direction(self) -> str:
        return "dst" if self.direction in ("outbound", "dst") else "src"

    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary."""
        return asdict(self)


class ResponsePolicy:
    """
    Direction-aware response policy and safety guardrail engine.
    
    Evaluates detection events and determines whether automated firewall mitigations
    can be safely dispatched without risking denial of authorized service.
    """

    def __init__(
        self,
        allowlist: Optional[List[str]] = None,
        min_confidence_map: Optional[Dict[str, float]] = None,
        min_repeats: int = 3,
        repeat_window_seconds: int = 60,
        max_rule_minutes: int = 60,
        auto_response: bool = False,
        allow_device_isolation: bool = False,
        local_networks: Optional[List[str]] = None,
        rate_limit_classes: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize the response policy engine.

        Args:
            allowlist: List of IP addresses permanently immune to blocking.
            min_confidence_map: Class-specific operational confidence thresholds.
            min_repeats: Required number of repeat occurrences to trigger action.
            repeat_window_seconds: Sliding window duration in seconds.
            max_rule_minutes: Maximum rule duration in minutes before expiry.
            auto_response: Master switch enabling or disabling automated actions.
                Off by default; it is turned on only for planned lab tests.
            allow_device_isolation: Whether isolating a local device is permitted.
            local_networks: The protected local (camera) networks, from settings
                `lab.local_networks`. An address in these networks is a local device.
                If not given, all RFC 1918 private ranges are treated as local.
                (In our lab the "outside" attack network 10.10.10.0/24 is private but
                NOT local, so `lab.local_networks` must be passed in real use.)
            rate_limit_classes: Classes whose automatic action is a rate-limit of the
                outside source instead of a block (D-055: DDoS_DoS when Step 17 found no
                block threshold). The same safety checks apply.
        """
        self.allowlist: set[str] = set(
            ip.strip() for ip in (allowlist if allowlist is not None else DEFAULT_ALLOWLIST)
        )
        self.local_networks = []
        for cidr in local_networks or []:
            try:
                self.local_networks.append(ipaddress.ip_network(str(cidr).strip(), strict=False))
            except ValueError:
                logger.warning("Ignoring invalid local network in settings: %s", cidr)
        self.min_confidence_map: Dict[str, float] = min_confidence_map or {
            "DDoS_DoS": 0.70,
            "PortScan": 0.65,
            "CnC": 0.60,
            "Malware_Download": 0.85,
        }
        self.min_repeats: int = max(1, min_repeats)
        self.repeat_window_seconds: int = max(5, repeat_window_seconds)
        self.max_rule_minutes: int = max(1, max_rule_minutes)
        self.auto_response: bool = auto_response
        self.allow_device_isolation: bool = allow_device_isolation
        self.rate_limit_classes: set[str] = set(rate_limit_classes or [])

        # State tracking: (target_ip, class_name) -> deque of timestamps
        self._history: Dict[Tuple[str, str], deque] = defaultdict(deque)

        logger.info(
            "ResponsePolicy initialized. Auto-response=%s, Min repeats=%d, Window=%ds, Allowlist=%d",
            self.auto_response,
            self.min_repeats,
            self.repeat_window_seconds,
            len(self.allowlist),
        )

    def is_local(self, ip_str: str) -> bool:
        """True if the address is a local (protected) device.

        Uses `lab.local_networks` when it was given; otherwise any RFC 1918 address.
        """
        if not self.local_networks:
            return is_private_ip(ip_str)
        try:
            ip_obj = ipaddress.ip_address(str(ip_str).strip())
        except ValueError:
            return False
        return any(ip_obj in net for net in self.local_networks)

    def reset_history(self) -> None:
        """Clear the sliding-window repeat event history."""
        self._history.clear()

    def check_repeats(
        self, target_ip: str, class_name: str, current_time: Optional[float] = None
    ) -> Tuple[bool, int]:
        """
        Check if an event meets the minimum repetition count within the sliding window.

        Args:
            target_ip: IP address being evaluated.
            class_name: Attack classification name.
            current_time: Epoch timestamp (defaults to current time).

        Returns:
            Tuple of (is_repeated_enough: bool, current_repeat_count: int).
        """
        now = time.time() if current_time is None else float(current_time)
        key = (target_ip.strip(), class_name.strip())
        q = self._history[key]

        # Record this occurrence
        q.append(now)

        # Prune occurrences outside the time window
        cutoff = now - self.repeat_window_seconds
        while q and q[0] < cutoff:
            q.popleft()

        count = len(q)
        return (count >= self.min_repeats, count)

    def get_repeat_count(
        self, target_ip: str, class_name: str, current_time: Optional[float] = None
    ) -> int:
        """Get the current count of events within the active sliding window."""
        now = time.time() if current_time is None else float(current_time)
        key = (target_ip.strip(), class_name.strip())
        q = self._history.get(key)
        if not q:
            return 0

        cutoff = now - self.repeat_window_seconds
        valid = [t for t in q if t >= cutoff]
        return len(valid)

    def evaluate(
        self,
        event: Union[Dict[str, Any], Any],
        current_time: Optional[float] = None,
    ) -> PolicyDecision:
        """
        Evaluate an event against direction-aware rules and the 7 safety checkpoints.

        Args:
            event: Event dict or object with `predicted_class`, `confidence`, `src_ip`,
                   `dst_ip`, `traffic_direction`, `proto`, etc.
            current_time: Optional current epoch timestamp.

        Returns:
            `PolicyDecision` containing action recommendation, target, duration, and reason code.
        """
        now = time.time() if current_time is None else float(current_time)

        # Extract event attributes safely
        if hasattr(event, "to_dict"):
            data = event.to_dict()
        elif isinstance(event, dict):
            data = event
        else:
            data = getattr(event, "__dict__", {})

        p_class = str(data.get("predicted_class", "Benign")).strip()
        confidence = float(data.get("confidence", 0.0))
        src_ip = str(data.get("src_ip", "")).strip()
        dst_ip = str(data.get("dst_ip", "")).strip()
        direction = str(data.get("traffic_direction", data.get("direction", "inbound"))).lower()
        evidence_note = str(data.get("evidence_note", ""))

        # ---------------------------------------------------------
        # Case 1: Benign flows are NEVER blocked (Table 5 invariant)
        # ---------------------------------------------------------
        if p_class == "Benign":
            return PolicyDecision(
                should_act=False,
                action_type="none",
                target_ip="",
                direction="inbound",
                duration_minutes=0,
                reason_code=REASON_SKIP_BENIGN,
                evidence_note="Benign traffic flow; blocking prohibited by response policy.",
                details={"predicted_class": p_class, "confidence": confidence},
            )

        # Determine target IP and action type based on class & traffic direction (Table 5)
        action_type = "block"
        target_ip = ""
        action_direction = "inbound"
        default_reason = REASON_AUTO_PORTSCAN
        requested_duration = 60

        if p_class == "PortScan":
            target_ip = src_ip
            action_direction = "inbound"
            default_reason = REASON_AUTO_PORTSCAN
            requested_duration = 30
        elif p_class == "DDoS_DoS":
            target_ip = src_ip
            action_direction = "inbound"
            default_reason = REASON_AUTO_DDOS_BLOCK
            requested_duration = 60
            if p_class in self.rate_limit_classes:
                # D-055 / Table 5: "Rate-limit or block the outside source if the policy allows it"
                action_type = "rate_limit"
                default_reason = REASON_AUTO_DDOS_RATELIMIT
        elif p_class == "CnC":
            # Table 5: a local device talking to the outside -> block the outside destination.
            # The target is always the destination, as in the Step 17 replay that chose the CnC
            # threshold (ml_engine/response_replay.py TARGET_FIELD). An incoming flow from outside
            # that looks like C&C (for example the first flows of a flood or a scan, issue 43) has
            # a local destination, so the local-network check below stops the block: alert only.
            target_ip = dst_ip
            action_direction = "outbound"
            default_reason = REASON_AUTO_CNC_DEST_BLOCK
            requested_duration = 60
        elif p_class == "Malware_Download":
            # Table 5: block the outside host, chosen by the traffic direction
            target_ip = src_ip if not self.is_local(src_ip) else dst_ip
            action_direction = "inbound" if target_ip == src_ip else "outbound"
            default_reason = REASON_AUTO_MALWARE_BLOCK
            requested_duration = 60
        else:
            target_ip = src_ip
            default_reason = f"AUTO_{p_class.upper()}_BLOCK"

        # ---------------------------------------------------------
        # Safety Check 1: Master auto-response switch enabled?
        # ---------------------------------------------------------
        if not self.auto_response:
            return PolicyDecision(
                should_act=False,
                action_type="none",
                target_ip=target_ip,
                direction=action_direction,
                duration_minutes=0,
                reason_code=REASON_SKIP_AUTO_DISABLED,
                evidence_note="Autonomous mitigation skipped: master response switch is disabled.",
                details={"auto_response": False, "target_ip": target_ip},
            )

        # ---------------------------------------------------------
        # Safety Check 2: Minimum calibrated confidence met?
        # A behaviour-confirmed port scan (fan-out across many hosts/ports, set by the decision
        # engine) is reconnaissance regardless of the per-flow model confidence, so it is exempt
        # from this one check. Every other safety check below still applies to it.
        # ---------------------------------------------------------
        scan_confirmed = bool(data.get("scan_confirmed", False))
        min_conf = self.min_confidence_map.get(p_class, 0.70)
        if confidence < min_conf and not (p_class == "PortScan" and scan_confirmed):
            return PolicyDecision(
                should_act=False,
                action_type="none",
                target_ip=target_ip,
                direction=action_direction,
                duration_minutes=0,
                reason_code=REASON_SKIP_LOW_CONF,
                evidence_note=(
                    f"Confidence {confidence:.2f} is below operational threshold {min_conf:.2f}; "
                    "alerting only."
                ),
                details={"confidence": confidence, "threshold": min_conf, "class": p_class},
            )

        # ---------------------------------------------------------
        # Safety Check 3: Management allowlist immunity verification
        # ---------------------------------------------------------
        if target_ip in self.allowlist or src_ip in self.allowlist:
            immune_ip = target_ip if target_ip in self.allowlist else src_ip
            return PolicyDecision(
                should_act=False,
                action_type="none",
                target_ip=immune_ip,
                direction=action_direction,
                duration_minutes=0,
                reason_code=REASON_SKIP_ALLOWLIST,
                evidence_note=(
                    f"Target IP {immune_ip} is protected by the management allowlist. "
                    "Blocking prohibited."
                ),
                details={"allowlisted_ip": immune_ip, "class": p_class},
            )

        # ---------------------------------------------------------
        # Safety Check 4: Local network target protection (proposal 3.7:
        # "checks on private networks"). A local camera-network device is never
        # blocked automatically unless device isolation is allowed in settings.
        # ---------------------------------------------------------
        if self.is_local(target_ip) and not self.allow_device_isolation:
            return PolicyDecision(
                should_act=False,
                action_type="none",
                target_ip=target_ip,
                direction=action_direction,
                duration_minutes=0,
                reason_code=REASON_SKIP_PRIVATE_TARGET,
                evidence_note=(
                    f"Target IP {target_ip} is an internal private device. Drop aborted "
                    "to preserve surveillance streaming to NVR."
                ),
                details={"private_ip": target_ip, "allow_isolation": self.allow_device_isolation},
            )

        # ---------------------------------------------------------
        # Safety Check 5: Sliding-window repeat coalescing
        # ---------------------------------------------------------
        is_repeated, count = self.check_repeats(target_ip, p_class, now)
        if not is_repeated:
            return PolicyDecision(
                should_act=False,
                action_type="none",
                target_ip=target_ip,
                direction=action_direction,
                duration_minutes=0,
                reason_code=REASON_SKIP_NOT_REPEATED,
                evidence_note=(
                    f"Repeat count ({count}/{self.min_repeats}) in {self.repeat_window_seconds}s "
                    "window is below minimum repetition threshold; candidate alerted."
                ),
                details={
                    "current_repeats": count,
                    "min_repeats": self.min_repeats,
                    "window_seconds": self.repeat_window_seconds,
                    "target_ip": target_ip,
                },
            )

        # ---------------------------------------------------------
        # Safety Check 6: Bounded rule expiry duration
        # ---------------------------------------------------------
        duration_minutes = min(self.max_rule_minutes, requested_duration)

        # ---------------------------------------------------------
        # Checkpoint 7: All 7 checks PASSED -> Action Approved!
        # ---------------------------------------------------------
        return PolicyDecision(
            should_act=True,
            action_type=action_type,
            target_ip=target_ip,
            direction=action_direction,
            duration_minutes=duration_minutes,
            reason_code=default_reason,
            evidence_note=evidence_note or f"Autonomous mitigation triggered for {p_class}.",
            details={
                "class": p_class,
                "confidence": confidence,
                "repeat_count": count,
                "duration_minutes": duration_minutes,
                "evaluated_at": now,
            },
        )
