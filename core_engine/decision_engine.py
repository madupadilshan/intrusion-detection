#!/usr/bin/env python3
"""
core_engine/decision_engine.py - Intrusion Decision and Response Engine (Step 26).
==================================================================================

Governing Standards & Requirements:
- Group 03 Research Proposal: Figures 2 & 3 ("Intrusion Detection Pipeline");
  Sections 3.4, 3.6, 3.7; Requirements Table 7: FR-01, FR-02, FR-03, FR-04, FR-06;
  Hypothesis H1 Clause 3 (Sub-Second Latency Tracking).
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
     `db_ts`, and `emit_ts` to verify sub-second response times.
"""

from __future__ import annotations

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
from core_engine.firewall import get_firewall_adapter, BaseFirewallAdapter

logger = logging.getLogger("core_engine.decision_engine")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_THRESHOLDS_PATH = PROJECT_ROOT / "reports" / "experiments" / "operational_thresholds.json"
DEFAULT_SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.yaml"

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
    response_status: str = "none"  # none | allowlist_protected | candidate | pending
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

        # Load operational thresholds
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
        self.policy = ResponsePolicy(
            allowlist=self.allowlist,
            min_repeats=self.min_repeats,
            repeat_window_seconds=self.repeat_window_seconds,
            max_rule_minutes=self.max_rule_minutes,
            auto_response=bool(self.settings.get("response", {}).get("auto_response", True)),
        )

        # Initialize firewall response adapter (Step 33)
        self.firewall: BaseFirewallAdapter = firewall_adapter or get_firewall_adapter(
            config=self.settings.get("firewall", {}),
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

        # Record in MongoDB
        if self.db is not None:
            try:
                if hasattr(self.db, "add_to_blocklist"):
                    self.db.add_to_blocklist(
                        ip=decision.target_ip,
                        direction=decision.target_direction,
                        reason=decision.reason,
                        duration_minutes=decision.duration_minutes,
                        actor=actor,
                        event_id=event_id,
                    )
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

        # Timestamps for sub-second latency verification (Hypothesis H1 Clause 3)
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
        alert_threshold = float(class_thresh.get("passive_alert_threshold", 0.50))
        block_threshold = float(class_thresh.get("active_response_threshold", 0.70))
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

        # 2. Decision evaluation
        outcomes: List[DecisionOutcome] = []
        for det in detections:
            outcome = self.evaluate_detection(det)
            outcomes.append(outcome)

        return outcomes
