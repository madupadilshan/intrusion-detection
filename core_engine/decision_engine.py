#!/usr/bin/env python3
"""
core_engine/decision_engine.py - Intrusion Decision and Response Engine (Step 26).
==================================================================================

Governing Standards & Requirements:
- Group 03 Research Proposal: Figures 2 & 3 ("Intrusion Detection Pipeline");
  Sections 3.4, 3.6, 3.7; Requirements Table 7: FR-01, FR-02, FR-03, FR-04, FR-06;
  Table 9 latency target (median decision < 2 s, 95th percentile < 5 s; measured in Step 37).
- Step-by-Step Guide: Step 26 ("Build the detector and decision engine").
- Key Principles:
  1. Benign flows: Aggregate exclusively to `traffic_summaries` (FR-03, Table 5).
     NEVER write benign flows to `attack_events`.
  2. Attack flows below passive alert threshold: Logged/ignored as low-confidence noise.
  3. Attack flows between alert & active thresholds: Recorded as `ALERT_ONLY` with status `prediction`.
  4. Attack flows at or above active response threshold: Passed as `ACTIVE_BLOCK_CANDIDATE`
     subject to allowlist and private network safety checks.
  5. Allowlist immunity: Critical management IPs (router, sensor, admin, NVR) are NEVER block candidates.
  6. Burst coalescing (Tip 3): Coalesces repeated flows within `repeat_window_seconds` (60s).
  7. End-to-end latency tracking: Records `zeek_ts`, `adapter_ts`, `detect_ts`, `decision_ts`,
     `db_ts`, and `emit_ts` so the end-to-end time can be measured (Table 9, Step 37).
"""

from __future__ import annotations

import os

import json
import logging
import time
from datetime import datetime, timezone
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from core_engine.detector import DetectionResult, Detector
from core_engine.response_policy import ResponsePolicy, PolicyDecision
from core_engine.firewall import (
    get_firewall_adapter,
    firewall_config_from_settings,
    BaseFirewallAdapter,
    FirewallError,
)

logger = logging.getLogger("core_engine.decision_engine")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_THRESHOLDS_PATH = PROJECT_ROOT / "reports" / "experiments" / "operational_thresholds.json"
# IDS_SETTINGS_FILE lets a test setup (e.g. lab_virtual/) use its own settings file.
DEFAULT_SETTINGS_PATH = Path(os.getenv("IDS_SETTINGS_FILE") or PROJECT_ROOT / "config" / "settings.yaml")

# Default fallback thresholds if config files cannot be loaded
FALLBACK_THRESHOLDS = {
    "Benign": {"policy": "ALLOW_ALWAYS"},
    "DDoS_DoS": {
        "active_response_threshold": 0.70,
        "passive_alert_threshold": 0.50,
        "action": "drop_source",
        "reason_code": "DOS_HIGH_RATE_PACKET_FLOOD",
    },
    "PortScan": {
        "active_response_threshold": 0.65,
        "passive_alert_threshold": 0.30,
        "action": "drop_source",
        "reason_code": "SCAN_RAPID_PROBE_SWEEP",
    },
    "CnC": {
        "active_response_threshold": 0.60,
        "passive_alert_threshold": 0.25,
        "action": "isolate_target",
        "reason_code": "CNC_PERSISTENT_BEACON",
    },
    "Malware_Download": {
        "active_response_threshold": 0.85,
        "passive_alert_threshold": 0.50,
        "action": "isolate_target",
        "reason_code": "MALWARE_STAGING_TRANSFER",
    },
}

DEFAULT_ALLOWLIST = [
    "192.168.50.1",   # lab router / gateway
    "192.168.50.5",   # IDS sensor
    "192.168.50.10",  # admin workstation
    "192.168.50.20",  # NVR
]


@dataclass
class DecisionOutcome:
    """Standardized decision outcome for an evaluated flow detection."""

    flow_id: Optional[str] = None
    event_id: Optional[str] = None
    action: str = "BENIGN_SUMMARY"  # BENIGN_SUMMARY | LOW_CONFIDENCE_IGNORE | ALERT_ONLY | ACTIVE_BLOCK_CANDIDATE
    predicted_class: str = "Benign"
    confidence: float = 0.0
    severity: str = "info"  # info | low | medium | high | critical
    src_ip: str = ""
    src_port: int = 0
    dst_ip: str = ""
    dst_port: int = 0
    proto: str = "tcp"
    service: str = "-"
    conn_state: str = "-"
    traffic_direction: str = "inbound"
    is_allowlisted: bool = False
    evidence_note: str = ""
    reason_code: str = "NONE"
    # none | allowlist_protected | candidate | blocked | rate_limited | already_blocked | failed
    response_status: str = "none"
    response_reason: str = ""  # policy reason code (AUTO_* when acted, SKIP_* when not)
    status: str = "prediction"
    timestamps: Dict[str, float] = field(default_factory=dict)
    pipeline_latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert decision outcome to serializable dictionary."""
        return asdict(self)


class DecisionEngine:
    """
    Intrusion Decision and Response Engine.

    Evaluates flow predictions against operational thresholds, enforces lab safety
    guardrails, generates evidence notes, records to MongoDB, and emits live Socket.IO events.
    """

    def __init__(
        self,
        db_service: Optional[Any] = None,
        socketio: Optional[Any] = None,
        thresholds_config: Optional[Dict[str, Any]] = None,
        settings_path: Optional[Union[str, Path]] = None,
        detector: Optional[Detector] = None,
        firewall_adapter: Optional[BaseFirewallAdapter] = None,
    ) -> None:
        """
        Initialize the Decision Engine.

        Args:
            db_service: DatabaseService instance. If None, lazy-loads default if needed.
            socketio: Flask-SocketIO server instance for real-time telemetry broadcasts.
            thresholds_config: Operational threshold dictionary. If None, loads from JSON.
            settings_path: Path to settings.yaml. If None, loads from default.
            detector: Pre-initialized Detector instance. If None, lazily initializes.
            firewall_adapter: Firewall response adapter. If None, instantiates via factory.
        """
        self.db = db_service
        self.socketio = socketio
        self.detector = detector

        # Load operational thresholds. The model bundle is the main source, so the
        # model and its thresholds always travel together (proposal 3.3, step 7).
        if thresholds_config is None and detector is not None and getattr(detector, "operational_thresholds", None):
            thresholds_config = detector.operational_thresholds
        self.thresholds: Dict[str, Any] = self._load_thresholds(thresholds_config)

        # Load local settings (allowlist, safety guardrails)
        self.settings: Dict[str, Any] = self._load_settings(settings_path)
        self.allowlist: List[str] = self.settings.get("allowlist", DEFAULT_ALLOWLIST)
        self.repeat_window_seconds: int = int(
            self.settings.get("response", {}).get("repeat_window_seconds", 60)
        )
        self.min_repeats: int = int(self.settings.get("response", {}).get("min_repeats", 3))
        self.max_rule_minutes: int = int(
            self.settings.get("response", {}).get("max_rule_minutes", 30)
        )
        response_cfg = self.settings.get("response", {}) or {}
        # Active (blocking) thresholds per class come from the model bundle /
        # operational_thresholds.json (Step 17). A class with no active threshold
        # is never blocked automatically; it can only raise alerts.
        min_conf_map: Dict[str, float] = {}
        for cls_name, cls_cfg in self.thresholds.items():
            if isinstance(cls_cfg, dict) and cls_cfg.get("active_response_threshold") is not None:
                min_conf_map[cls_name] = float(cls_cfg["active_response_threshold"])
            elif cls_name != "Benign":
                min_conf_map[cls_name] = 1.01  # unreachable: alert only
        self.policy = ResponsePolicy(
            allowlist=self.allowlist,
            min_confidence_map=min_conf_map or None,
            min_repeats=self.min_repeats,
            repeat_window_seconds=self.repeat_window_seconds,
            max_rule_minutes=self.max_rule_minutes,
            # Off unless settings.yaml turns it on (safe default, proposal Table 11).
            auto_response=bool(response_cfg.get("auto_response", False)),
            allow_device_isolation=bool(response_cfg.get("allow_device_isolation", False)),
            local_networks=(self.settings.get("lab", {}) or {}).get("local_networks"),
        )
        # IPs blocked by this engine and when the rule ends, so one attack does not
        # create a new firewall rule for every single flow.
        self._active_blocks: Dict[str, float] = {}
        self._min_confidence_floor: Optional[float] = None
        # settings.yaml response.min_confidence = lowest confidence for any automatic block.
        if response_cfg.get("min_confidence") is not None:
            try:
                self.apply_runtime_settings({"min_confidence": response_cfg["min_confidence"]})
            except ValueError as exc:
                logger.warning("Ignoring invalid response.min_confidence: %s", exc)

        # Initialize firewall response adapter (Step 33)
        self.firewall: BaseFirewallAdapter = firewall_adapter or get_firewall_adapter(
            config=firewall_config_from_settings(self.settings),
            allowlist=set(self.allowlist),
            max_rule_minutes=self.max_rule_minutes,
        )

        logger.info(
            "DecisionEngine initialized. Repeat window: %ds, Allowlist IPs: %d, Firewall: %s (%s)",
            self.repeat_window_seconds,
            len(self.allowlist),
            self.firewall.name,
            "simulated" if self.firewall.is_simulated else "live",
        )

    def evaluate_response(self, outcome_or_event: Any) -> PolicyDecision:
        """
        Evaluate candidate outcome or event against response policy safety guardrails (Step 31).

        Args:
            outcome_or_event: `DecisionOutcome` or event dictionary.

        Returns:
            `PolicyDecision` with action recommendation and reason code.
        """
        return self.policy.evaluate(outcome_or_event)

    def execute_response(
        self,
        decision: PolicyDecision,
        event_id: Optional[str] = None,
        actor: str = "autonomous_policy",
    ) -> Optional[Dict[str, Any]]:
        """
        Execute an approved policy response decision on the firewall adapter and record audit logs (Step 33).

        Args:
            decision: Approved `PolicyDecision` from `evaluate_response()`.
            event_id: Associated attack event ID in MongoDB.
            actor: Operator identity or 'autonomous_policy'.

        Returns:
            Firewall rule dictionary if executed, None if skipped.
        """
        if not decision.should_act or not decision.target_ip:
            if self.db is not None and hasattr(self.db, "log_response_action"):
                try:
                    self.db.log_response_action({
                        "event_id": event_id,
                        "action": decision.action,
                        "target_ip": decision.target_ip or "",
                        "direction": decision.target_direction,
                        "duration_minutes": decision.duration_minutes,
                        "reason": decision.reason,
                        "actor": actor,
                        "status": "skipped",
                        "created_at": datetime.now(timezone.utc),
                        "simulated": getattr(self.firewall, "is_simulated", True),
                    })
                except Exception as exc:
                    logger.debug("Failed to log skipped response action: %s", exc)
            return None

        # Execute mitigation on firewall adapter
        applied_rule = None
        if decision.action == "rate_limit":
            applied_rule = self.firewall.rate_limit(
                ip=decision.target_ip,
                minutes=decision.duration_minutes,
                reason=decision.reason,
            )
        else:
            applied_rule = self.firewall.block(
                ip=decision.target_ip,
                direction=decision.target_direction,
                minutes=decision.duration_minutes,
                reason=decision.reason,
            )

        # Record in MongoDB. The blocklist stores the direction as 'source' / 'destination'
        # (db_service.add_to_blocklist); the firewall uses 'src' / 'dst'.
        if self.db is not None:
            details = decision.details or {}
            if hasattr(self.db, "add_to_blocklist"):
                try:
                    self.db.add_to_blocklist(
                        ip=decision.target_ip,
                        direction="destination" if decision.target_direction == "dst" else "source",
                        reason=decision.reason,
                        duration_minutes=decision.duration_minutes,
                        linked_event_id=event_id,
                        predicted_class=details.get("class"),
                        confidence=details.get("confidence"),
                        actor=actor,
                    )
                except Exception as exc:
                    logger.error("Failed to save the block of %s in the blocklist: %s", decision.target_ip, exc)
            try:
                if hasattr(self.db, "log_response_action"):
                    self.db.log_response_action({
                        "event_id": event_id,
                        "action": decision.action,
                        "target_ip": decision.target_ip,
                        "direction": decision.target_direction,
                        "duration_minutes": decision.duration_minutes,
                        "reason": decision.reason,
                        "actor": actor,
                        "status": "active",
                        "created_at": datetime.now(timezone.utc),
                        "simulated": getattr(self.firewall, "is_simulated", True),
                    })
            except Exception as exc:
                logger.error("Failed to persist response action to DB: %s", exc)

        # Broadcast via Socket.IO
        if self.socketio is not None:
            try:
                self.socketio.emit(
                    "blocklist_update",
                    {
                        "ip": decision.target_ip,
                        "direction": decision.target_direction,
                        "action": decision.action,
                        "duration_minutes": decision.duration_minutes,
                        "reason": decision.reason,
                        "actor": actor,
                        "status": "active",
                        "event_id": event_id,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "simulated": getattr(self.firewall, "is_simulated", True),
                    },
                )
            except Exception as exc:
                logger.error("Failed to emit blocklist_update: %s", exc)

        return applied_rule

    def _load_thresholds(
        self, custom_thresholds: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Load operational thresholds from dict or JSON configuration."""
        if custom_thresholds:
            return custom_thresholds.get("classes", custom_thresholds)

        if DEFAULT_THRESHOLDS_PATH.is_file():
            try:
                with open(DEFAULT_THRESHOLDS_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                return cfg.get("classes", cfg)
            except Exception as e:
                logger.warning("Could not read operational_thresholds.json: %s. Using fallback.", e)

        return FALLBACK_THRESHOLDS

    def _load_settings(
        self, custom_path: Optional[Union[str, Path]] = None
    ) -> Dict[str, Any]:
        """Load runtime settings from YAML configuration."""
        path = Path(custom_path) if custom_path else DEFAULT_SETTINGS_PATH
        if path.is_file():
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning("Could not read settings.yaml from %s: %s", path, e)
        return {"allowlist": DEFAULT_ALLOWLIST}

    def _get_reason_code(self, predicted_class: str) -> str:
        """Map predicted attack class to standardized reason code."""
        class_cfg = self.thresholds.get(predicted_class, {})
        return class_cfg.get("reason_code") or FALLBACK_THRESHOLDS.get(
            predicted_class, {}
        ).get("reason_code", "GENERIC_ANOMALY")

    def generate_evidence_note(self, detection: DetectionResult) -> str:
        """
        Synthesize human-readable technical evidence note (FR-02) from flow metrics.

        Args:
            detection: `DetectionResult` containing predicted class and extracted features.

        Returns:
            Formatted evidence note string.
        """
        feats = detection.features or {}
        raw = detection.raw_flow or {}
        p_class = detection.predicted_class
        conf_pct = detection.confidence * 100

        dst_ip = raw.get("id.resp_h") or raw.get("id_resp_h") or raw.get("dst_ip", "target")
        dst_p = raw.get("id.resp_p") or raw.get("id_resp_p") or raw.get("dst_port", 0)
        orig_pkts = int(feats.get("orig_pkts", raw.get("orig_pkts", 0)))
        orig_bytes = int(feats.get("orig_bytes", raw.get("orig_bytes", 0)))
        resp_bytes = int(feats.get("resp_bytes", raw.get("resp_bytes", 0)))
        resp_pkts = int(feats.get("resp_pkts", raw.get("resp_pkts", 0)))
        conn_state = str(feats.get("conn_state", raw.get("conn_state", "-")))
        duration = float(feats.get("duration", raw.get("duration", 0.0)))
        service = str(feats.get("service", raw.get("service", "-")))
        pkt_ratio = float(feats.get("pkt_ratio", 0.0))

        if p_class == "DDoS_DoS":
            return (
                f"High-rate packet flood: {orig_pkts} packets ({orig_bytes} bytes) directed at "
                f"{dst_ip}:{dst_p} with packet return ratio {pkt_ratio:.2f} (Confidence: {conf_pct:.1f}%)."
            )
        elif p_class == "PortScan":
            return (
                f"Unanswered TCP probe sweep: conn_state={conn_state}, resp_pkts={resp_pkts}, "
                f"duration={duration:.3f}s to {dst_ip}:{dst_p} (Confidence: {conf_pct:.1f}%)."
            )
        elif p_class == "CnC":
            return (
                f"Persistent command-and-control beacon: low-volume telemetry ({orig_pkts} pkts, "
                f"{orig_bytes} bytes) to dynamic service port {dst_ip}:{dst_p} (Confidence: {conf_pct:.1f}%)."
            )
        elif p_class == "Malware_Download":
            return (
                f"Substantial inbound payload download: {resp_bytes} bytes received over "
                f"{service} service in conn_state={conn_state} (Confidence: {conf_pct:.1f}%)."
            )
        else:
            return f"Standard authorized traffic flow to {dst_ip}:{dst_p} ({service})."

    def _classify_severity(self, predicted_class: str, confidence: float) -> str:
        """Assign standardized incident severity."""
        if predicted_class == "Benign":
            return "info"
        if predicted_class in ("DDoS_DoS", "Malware_Download"):
            return "critical" if confidence >= 0.90 else "high"
        if predicted_class == "CnC":
            return "critical" if confidence >= 0.85 else "high"
        if predicted_class == "PortScan":
            return "high" if confidence >= 0.85 else "medium"
        return "low"

    def evaluate_detection(self, detection: DetectionResult) -> DecisionOutcome:
        """
        Evaluate a single detection result against thresholds and safety rules.

        Executes:
        - Benign routing to traffic_summaries (FR-03).
        - Threshold comparison (Alert vs Block).
        - Allowlist immunity verification.
        - Database persistence via `db_service`.
        - Real-time Socket.IO event emission.
        - End-to-end latency tracking.

        Args:
            detection: `DetectionResult` from `Detector`.

        Returns:
            `DecisionOutcome` object detailing the operational decision.
        """
        raw = detection.raw_flow or {}
        decision_ts = time.time()

        # Extract network flow tuple
        src_ip = str(raw.get("id.orig_h") or raw.get("id_orig_h") or raw.get("src_ip", "")).strip()
        dst_ip = str(raw.get("id.resp_h") or raw.get("id_resp_h") or raw.get("dst_ip", "")).strip()

        try:
            src_port = int(raw.get("id.orig_p") or raw.get("id_orig_p") or raw.get("src_port", 0))
        except (ValueError, TypeError):
            src_port = 0

        try:
            dst_port = int(raw.get("id.resp_p") or raw.get("id_resp_p") or raw.get("dst_port", 0))
        except (ValueError, TypeError):
            dst_port = 0

        proto = str(raw.get("proto", "tcp")).lower()
        service = str(raw.get("service", "-")).lower()
        conn_state = str(raw.get("conn_state", "-"))
        direction = str(raw.get("traffic_direction", "inbound"))

        # Timestamps for end-to-end latency measurement (Table 9: median < 2 s, p95 < 5 s)
        zeek_ts = float(raw.get("ts", raw.get("observed_epoch", decision_ts)))
        adapter_ts = float(raw.get("observed_epoch", decision_ts))
        detect_ts = detection.detect_ts

        is_allowlisted = src_ip in self.allowlist
        p_class = detection.predicted_class
        confidence = detection.confidence

        # Case 1: Benign Flow Handling (Proposal FR-03, Table 5)
        if p_class == "Benign":
            evidence_note = self.generate_evidence_note(detection)
            byte_count = int(
                raw.get("orig_bytes", 0) or 0
            ) + int(raw.get("resp_bytes", 0) or 0)

            # Record to MongoDB traffic_summaries only
            db_ts = time.time()
            if self.db is not None:
                try:
                    minute_dt = datetime.fromtimestamp(decision_ts, timezone.utc)
                    orig_b = int(raw.get("orig_bytes", 0) or 0)
                    resp_b = int(raw.get("resp_bytes", 0) or 0)
                    pkts_cnt = int(raw.get("orig_pkts", 0) or 0) + int(raw.get("resp_pkts", 0) or 0)
                    self.db.record_traffic_summary(
                        minute=minute_dt,
                        class_name="Benign",
                        count=1,
                        orig_bytes=orig_b,
                        resp_bytes=resp_b,
                        pkts=pkts_cnt,
                    )
                except Exception as e:
                    logger.error("Failed to record traffic summary in db: %s", e)

            # Socket.IO live push telemetry
            emit_ts = time.time()
            if self.socketio is not None:
                try:
                    self.socketio.emit(
                        "traffic_update",
                        {
                            "type": "benign_flow",
                            "timestamp": db_ts,
                            "flow_count": 1,
                            "byte_count": byte_count,
                            "src_ip": src_ip,
                            "dst_ip": dst_ip,
                        },
                    )
                except Exception as e:
                    logger.error("Failed to emit traffic_update via Socket.IO: %s", e)

            latency_ms = (emit_ts - adapter_ts) * 1000.0

            return DecisionOutcome(
                flow_id=detection.flow_id,
                event_id=None,
                action="BENIGN_SUMMARY",
                predicted_class="Benign",
                confidence=confidence,
                severity="info",
                src_ip=src_ip,
                src_port=src_port,
                dst_ip=dst_ip,
                dst_port=dst_port,
                proto=proto,
                service=service,
                conn_state=conn_state,
                traffic_direction=direction,
                is_allowlisted=is_allowlisted,
                evidence_note=evidence_note,
                reason_code="BENIGN_BASELINE_FLOW",
                response_status="none",
                status="prediction",
                timestamps={
                    "zeek_ts": zeek_ts,
                    "adapter_ts": adapter_ts,
                    "detect_ts": detect_ts,
                    "decision_ts": decision_ts,
                    "db_ts": db_ts,
                    "emit_ts": emit_ts,
                },
                pipeline_latency_ms=round(latency_ms, 2),
            )

        # Case 2: Attack Flow Handling (FR-01, FR-02, FR-06)
        class_thresh = self.thresholds.get(p_class, FALLBACK_THRESHOLDS.get(p_class, {}))
        alert_raw = class_thresh.get("passive_alert_threshold", 0.50)
        block_raw = class_thresh.get("active_response_threshold", 0.70)
        alert_threshold = float(alert_raw) if alert_raw is not None else 0.50
        # None = Step 17 found no safe block threshold: this class only raises alerts.
        block_threshold = float(block_raw) if block_raw is not None else float("inf")
        reason_code = self._get_reason_code(p_class)
        severity = self._classify_severity(p_class, confidence)
        evidence_note = self.generate_evidence_note(detection)

        # Branching based on dual thresholds
        if confidence < alert_threshold:
            # Noise below alert threshold: ignore
            action = "LOW_CONFIDENCE_IGNORE"
            response_status = "none"
            event_id = None
            db_ts = time.time()
            emit_ts = db_ts
        else:
            if is_allowlisted:
                action = "ALERT_ONLY"
                response_status = "allowlist_protected"
                evidence_note = f"[ALLOWLIST PROTECTED] {evidence_note}"
                event_id = None
            elif confidence >= block_threshold:
                action = "ACTIVE_BLOCK_CANDIDATE"
                response_status = "candidate"
                event_id = None
            else:
                action = "ALERT_ONLY"
                response_status = "none"
                event_id = None

        # Persist to database if alert or candidate
        if action in ("ALERT_ONLY", "ACTIVE_BLOCK_CANDIDATE"):
            event_payload = {
                "src_ip": src_ip,
                "src_port": src_port,
                "dst_ip": dst_ip,
                "dst_port": dst_port,
                "proto": proto,
                "service": service,
                "conn_state": conn_state,
                "direction": direction,
                "traffic_direction": direction,
                "predicted_class": p_class,
                "confidence": confidence,
                "probabilities": detection.probabilities,
                "model_version": detection.model_version,
                "evidence_note": evidence_note,
                "reason_code": reason_code,
                "severity": severity,
                "status": "prediction",  # All initial detections start in prediction status
                "response_status": response_status,
                "is_allowlisted": is_allowlisted,
                "flow_features": detection.features,
                "features": detection.features,
                "timestamps": {
                    "zeek_ts": zeek_ts,
                    "adapter_ts": adapter_ts,
                    "detect_ts": detect_ts,
                    "decision_ts": decision_ts,
                },
            }

            db_ts = time.time()
            if self.db is not None:
                try:
                    event_id = self.db.record_attack_event(
                        event_payload,
                        aggregate_window_seconds=self.repeat_window_seconds,
                    )
                    event_payload["event_id"] = str(event_id)
                except Exception as e:
                    logger.error("Failed to record attack event in MongoDB: %s", e)

            # Socket.IO real-time alert push
            emit_ts = time.time()
            if self.socketio is not None:
                try:
                    self.socketio.emit("new_event", event_payload)
                except Exception as e:
                    logger.error("Failed to emit new_event via Socket.IO: %s", e)
        else:
            db_ts = time.time()
            emit_ts = db_ts

        latency_ms = (emit_ts - adapter_ts) * 1000.0

        return DecisionOutcome(
            flow_id=detection.flow_id,
            event_id=str(event_id) if event_id else None,
            action=action,
            predicted_class=p_class,
            confidence=confidence,
            severity=severity,
            src_ip=src_ip,
            src_port=src_port,
            dst_ip=dst_ip,
            dst_port=dst_port,
            proto=proto,
            service=service,
            conn_state=conn_state,
            traffic_direction=direction,
            is_allowlisted=is_allowlisted,
            evidence_note=evidence_note,
            reason_code=reason_code,
            response_status=response_status,
            status="prediction",
            timestamps={
                "zeek_ts": zeek_ts,
                "adapter_ts": adapter_ts,
                "detect_ts": detect_ts,
                "decision_ts": decision_ts,
                "db_ts": db_ts,
                "emit_ts": emit_ts,
            },
            pipeline_latency_ms=round(latency_ms, 2),
        )

    def process_flows(self, flows: List[Dict[str, Any]]) -> List[DecisionOutcome]:
        """
        Execute end-to-end processing of a flow batch through Detector and Decision Engine.

        Args:
            flows: List of Zeek flow connection dictionaries.

        Returns:
            List of `DecisionOutcome` objects.
        """
        if not flows:
            return []

        if self.detector is None:
            self.detector = Detector()

        # 1. Machine Learning Inference
        detections = self.detector.detect_flows(flows)

        # 2. Decision evaluation, then 3. controlled response (proposal 3.4, 3.7)
        outcomes: List[DecisionOutcome] = []
        for det in detections:
            outcome = self.evaluate_detection(det)
            self.respond_to_outcome(outcome)
            outcomes.append(outcome)

        return outcomes

    # Settings the administrator may change from the dashboard (FR-07). Each change is
    # stored with its history by db_service.set_setting() and applied here at once.
    RUNTIME_SETTING_KEYS = ("allowlist", "min_confidence", "min_repeats", "repeat_window_seconds", "max_rule_minutes")

    @staticmethod
    def validate_runtime_setting(key: str, value: Any) -> Any:
        """Check one dashboard setting and return the clean value (ValueError if wrong)."""
        import ipaddress as _ip

        if key == "allowlist":
            if not isinstance(value, (list, tuple)) or not value:
                raise ValueError("allowlist must be a non-empty list of IP addresses")
            clean = []
            for item in value:
                clean.append(str(_ip.ip_address(str(item).strip())))
            return clean
        if key == "min_confidence":
            v = float(value)
            if not 0.0 < v <= 1.0:
                raise ValueError("min_confidence must be between 0 and 1")
            return v
        if key == "min_repeats":
            v = int(value)
            if v < 1:
                raise ValueError("min_repeats must be at least 1")
            return v
        if key == "repeat_window_seconds":
            v = int(value)
            if v < 5:
                raise ValueError("repeat_window_seconds must be at least 5")
            return v
        if key == "max_rule_minutes":
            v = int(value)
            if not 1 <= v <= 1440:
                raise ValueError("max_rule_minutes must be between 1 and 1440")
            return v
        raise ValueError(f"'{key}' is not a runtime setting")

    def apply_runtime_settings(self, values: Dict[str, Any]) -> Dict[str, Any]:
        """Apply checked dashboard settings to the running policy. Returns what was applied."""
        applied: Dict[str, Any] = {}
        for key, raw in (values or {}).items():
            if key not in self.RUNTIME_SETTING_KEYS or raw is None:
                continue
            value = self.validate_runtime_setting(key, raw)
            if key == "allowlist":
                self.allowlist = list(value)
                self.policy.allowlist = set(value)
                if hasattr(self.firewall, "allowlist"):
                    self.firewall.allowlist = set(value)
            elif key == "min_confidence":
                self._min_confidence_floor = value
                # Lowest confidence for ANY automatic block. A per-class threshold
                # from Step 17 that is higher than this still applies.
                for cls_name in list(self.policy.min_confidence_map):
                    base = self._class_active_threshold(cls_name)
                    self.policy.min_confidence_map[cls_name] = max(base, value)
            elif key == "min_repeats":
                self.min_repeats = value
                self.policy.min_repeats = value
            elif key == "repeat_window_seconds":
                self.repeat_window_seconds = value
                self.policy.repeat_window_seconds = value
            elif key == "max_rule_minutes":
                self.max_rule_minutes = value
                self.policy.max_rule_minutes = value
                if hasattr(self.firewall, "max_rule_minutes"):
                    self.firewall.max_rule_minutes = value
            applied[key] = value
        if applied:
            logger.info("Runtime settings applied: %s", applied)
        return applied

    def get_runtime_settings(self) -> Dict[str, Any]:
        """Values the running policy uses now (shown on the dashboard Settings page)."""
        return {
            "allowlist": sorted(self.policy.allowlist),
            "min_confidence": self._min_confidence_floor,
            "min_repeats": self.policy.min_repeats,
            "repeat_window_seconds": self.policy.repeat_window_seconds,
            "max_rule_minutes": self.policy.max_rule_minutes,
            "auto_response": self.policy.auto_response,
            "block_thresholds": {k: (None if v > 1.0 else v) for k, v in self.policy.min_confidence_map.items()},
        }

    def _class_active_threshold(self, cls_name: str) -> float:
        cfg = self.thresholds.get(cls_name, {})
        if isinstance(cfg, dict) and cfg.get("active_response_threshold") is not None:
            return float(cfg["active_response_threshold"])
        return 1.01

    def forget_block(self, ip: str) -> None:
        """Forget an engine block after a manual unblock, so a new attack can be blocked again."""
        self._active_blocks.pop(str(ip).strip(), None)

    def respond_to_outcome(self, outcome: DecisionOutcome) -> Optional[PolicyDecision]:
        """Run the response policy for a block candidate and act if every check passes.

        Only `ACTIVE_BLOCK_CANDIDATE` outcomes go to the policy. The policy applies the
        safety checks (master switch, confidence, allowlist, local-network protection,
        repeats in the time window, maximum rule time). When it approves, the firewall
        adapter applies the rule, the block is saved and the dashboard is told.
        """
        if outcome.action != "ACTIVE_BLOCK_CANDIDATE":
            return None

        decision = self.evaluate_response(outcome)
        outcome.response_reason = decision.reason_code
        if not decision.should_act:
            # Audit: keep the reason why no block was made on the attack event (proposal 3.7)
            if outcome.event_id and self.db is not None and hasattr(self.db, "update_attack_event_status"):
                try:
                    self.db.update_attack_event_status(outcome.event_id, response_reason=decision.reason_code)
                except Exception as exc:
                    logger.debug("Could not store skip reason: %s", exc)
            return decision

        now = time.time()
        expires = self._active_blocks.get(decision.target_ip)
        if expires is not None and expires > now:
            outcome.response_status = "already_blocked"
            return decision

        try:
            rule = self.execute_response(decision, event_id=outcome.event_id)
        except FirewallError as exc:
            logger.error("Firewall refused the block for %s: %s", decision.target_ip, exc)
            outcome.response_status = "failed"
            rule = None
        except Exception as exc:  # never let a firewall problem stop detection
            logger.error("Unexpected error while blocking %s: %s", decision.target_ip, exc)
            outcome.response_status = "failed"
            rule = None

        if outcome.response_status != "failed":
            outcome.response_status = "rate_limited" if decision.action_type == "rate_limit" else "blocked"
            self._active_blocks[decision.target_ip] = now + 60.0 * max(1, decision.duration_minutes)

        if outcome.event_id and self.db is not None and hasattr(self.db, "update_attack_event_status"):
            try:
                self.db.update_attack_event_status(
                    outcome.event_id,
                    response_status=outcome.response_status,
                    response_reason=outcome.response_reason,
                )
            except Exception as exc:
                logger.error("Failed to update event response status: %s", exc)
        if self.socketio is not None and outcome.event_id:
            try:
                self.socketio.emit("event_update", {
                    "event_id": outcome.event_id,
                    "response_status": outcome.response_status,
                    "response_reason": outcome.response_reason,
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                })
            except Exception as exc:
                logger.error("Failed to emit event_update: %s", exc)
        return decision
