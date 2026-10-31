#!/usr/bin/env python3
"""
core_engine/export_service.py - Forensic Log Export Service (Step 28).
======================================================================

Governing Standards & Requirements:
- Group 03 Research Proposal: Table 7 Requirement FR-08 ("Forensic Log Export");
  Table 7 Requirement FR-07 ("Audit Logging and Invariants");
  Section 3.6 (Figure 4, collections `attack_events`, `system_logs`, `response_actions`).
- Step-by-Step Guide: Step 28 ("Log export").
- Key Principles:
  1. Multi-Attribute Filtering:
     - Date/time range: `start_time` and `end_time` (ISO 8601 UTC).
     - Attack class: `predicted_class` (Benign, DDoS, Okiru, PortScan, CnC).
     - IP filtering: `ip` (either src or dst), `src_ip`, `dst_ip`.
     - Incident status: `status` ('prediction', 'confirmed').
     - Response outcome: `response_status` ('none', 'candidate', 'mitigated', 'allowlist_protected').
     - Severity: `severity` ('critical', 'high', 'medium', 'low').
     - Audit filters: `actor`, `event`, `outcome`.
  2. Standard Export Formats:
     - CSV: RFC 4180 standard formatted string with proper headers, quotes, and UTF-8 encoding.
     - JSON: Structured, human-readable indented JSON array.
  3. Audit Logging (FR-07/FR-08 Invariant):
     - Every export operation is permanently recorded to MongoDB `system_logs` with the actor,
       log type, format, sanitized filters, row count, and UTC timestamp.
"""

from __future__ import annotations

import csv
import io
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

logger = logging.getLogger("core_engine.export_service")

# Canonical CSV field order per Proposal Figure 4 schema
ATTACK_EVENT_FIELDS = [
    "event_id",
    "timestamp",
    "direction",
    "src_ip",
    "src_port",
    "dst_ip",
    "dst_port",
    "proto",
    "service",
    "predicted_class",
    "confidence",
    "severity",
    "status",
    "response_status",
    "is_allowlisted",
    "reason_code",
    "flow_count",
    "evidence_note",
    "model_version",
    "pipeline_latency_ms",
]

SYSTEM_LOG_FIELDS = [
    "log_id",
    "timestamp",
    "actor",
    "event",
    "outcome",
    "details",
]

RESPONSE_ACTION_FIELDS = [
    "action_id",
    "executed_at",
    "action",
    "target_ip",
    "direction",
    "rule",
    "reason_code",
    "actor",
    "status",
    "event_id",
    "details",
]


def parse_datetime(val: Optional[Union[datetime, str]]) -> Optional[datetime]:
    """
    Parse an ISO 8601 string or datetime into a UTC-aware datetime.
    Supports '2026-10-31T20:00:00Z', '2026-10-31T20:00:00+00:00', or date '2026-10-31'.
    """
    if val is None:
        return None
    if isinstance(val, datetime):
        if val.tzinfo is None:
            return val.replace(tzinfo=timezone.utc)
        return val.astimezone(timezone.utc)

    val_str = str(val).strip()
    if not val_str:
        return None

    # Handle standard ISO formats
    try:
        clean_str = val_str.replace("Z", "+00:00")
        dt = datetime.fromisoformat(clean_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except ValueError:
        pass

    # Try common fallback patterns
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(val_str, fmt)
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            continue

    raise ValueError(f"Unable to parse datetime string: '{val_str}'. Use ISO 8601 format.")


def serialize_csv(records: List[Dict[str, Any]], fieldnames: List[str]) -> str:
    """
    Serialize a list of dictionaries into an RFC 4180 compliant CSV string.
    Serializes complex dicts and lists to JSON strings to maintain spreadsheet readability.
    """
    output = io.StringIO()
    writer = csv.DictWriter(
        output,
        fieldnames=fieldnames,
        extrasaction="ignore",
        quoting=csv.QUOTE_MINIMAL,
        lineterminator="\r\n",
    )
    writer.writeheader()

    for rec in records:
        row: Dict[str, Any] = {}
        for field in fieldnames:
            val = rec.get(field, "")
            if isinstance(val, (dict, list)):
                row[field] = json.dumps(val, ensure_ascii=False)
            elif isinstance(val, datetime):
                row[field] = val.isoformat()
            elif val is None:
                row[field] = ""
            else:
                row[field] = val
        writer.writerow(row)

    return output.getvalue()


def serialize_json(records: List[Dict[str, Any]]) -> str:
    """Serialize records into an indented, human-readable JSON string."""

    def json_serializer(obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)

    return json.dumps(records, default=json_serializer, indent=2, ensure_ascii=False)


class ExportService:
    """
    Forensic Log and Audit Trail Export Service (Requirement FR-08).

    Enables authenticated administrators to export attack events, system logs,
    and response actions with multi-dimensional query filtering in CSV and JSON formats.
    """

    def __init__(self, db_service: Optional[Any] = None) -> None:
        self.db = db_service

    def export_attack_events(
        self,
        filters: Optional[Dict[str, Any]] = None,
        export_format: str = "json",
    ) -> Tuple[str, str, int]:
        """
        Export filtered attack events.

        Args:
            filters: Dictionary of query constraints.
            export_format: 'csv' or 'json'.

        Returns:
            Tuple of (serialized_content, mime_type, row_count).
        """
        filters = filters or {}
        limit = min(int(filters.get("limit") or 1000), 10000)

        start_dt = parse_datetime(filters.get("start_time"))
        end_dt = parse_datetime(filters.get("end_time"))
        class_filter = filters.get("class_filter") or filters.get("class") or filters.get("predicted_class")
        status_filter = filters.get("status") or filters.get("status_filter")
        response_status_filter = filters.get("response_status") or filters.get("response_status_filter")
        src_ip = filters.get("src_ip")
        dst_ip = filters.get("dst_ip")
        ip = filters.get("ip")
        severity = filters.get("severity")

        if self.db is not None:
            records = self.db.get_attack_events(
                limit=limit,
                class_filter=class_filter,
                status_filter=status_filter,
                response_status_filter=response_status_filter,
                start_time=start_dt,
                end_time=end_dt,
                src_ip=src_ip,
                dst_ip=dst_ip,
                ip=ip,
                severity=severity,
                format_dates=True,
            )
        else:
            records = []

        export_format = export_format.strip().lower()
        if export_format == "csv":
            content = serialize_csv(records, ATTACK_EVENT_FIELDS)
            mime_type = "text/csv; charset=utf-8"
        else:
            content = serialize_json(records)
            mime_type = "application/json; charset=utf-8"

        return content, mime_type, len(records)

    def export_system_logs(
        self,
        filters: Optional[Dict[str, Any]] = None,
        export_format: str = "json",
    ) -> Tuple[str, str, int]:
        """
        Export filtered system audit logs.

        Args:
            filters: Dictionary of query constraints.
            export_format: 'csv' or 'json'.

        Returns:
            Tuple of (serialized_content, mime_type, row_count).
        """
        filters = filters or {}
        limit = min(int(filters.get("limit") or 1000), 10000)

        start_dt = parse_datetime(filters.get("start_time"))
        end_dt = parse_datetime(filters.get("end_time"))
        actor = filters.get("actor")
        event = filters.get("event") or filters.get("event_type")
        outcome = filters.get("outcome")

        if self.db is not None:
            records = self.db.get_system_logs(
                limit=limit,
                actor=actor,
                event=event,
                outcome=outcome,
                start_time=start_dt,
                end_time=end_dt,
                format_dates=True,
            )
        else:
            records = []

        export_format = export_format.strip().lower()
        if export_format == "csv":
            content = serialize_csv(records, SYSTEM_LOG_FIELDS)
            mime_type = "text/csv; charset=utf-8"
        else:
            content = serialize_json(records)
            mime_type = "application/json; charset=utf-8"

        return content, mime_type, len(records)

    def export_response_actions(
        self,
        filters: Optional[Dict[str, Any]] = None,
        export_format: str = "json",
    ) -> Tuple[str, str, int]:
        """
        Export filtered firewall response mitigation actions.

        Args:
            filters: Dictionary of query constraints.
            export_format: 'csv' or 'json'.

        Returns:
            Tuple of (serialized_content, mime_type, row_count).
        """
        filters = filters or {}
        limit = min(int(filters.get("limit") or 1000), 10000)

        start_dt = parse_datetime(filters.get("start_time"))
        end_dt = parse_datetime(filters.get("end_time"))
        target_ip = filters.get("target_ip") or filters.get("ip")
        event_id = filters.get("event_id")
        status = filters.get("status")
        actor = filters.get("actor")

        if self.db is not None:
            records = self.db.get_response_actions(
                limit=limit,
                target_ip=target_ip,
                event_id=event_id,
                start_time=start_dt,
                end_time=end_dt,
                status=status,
                actor=actor,
                format_dates=True,
            )
        else:
            records = []

        export_format = export_format.strip().lower()
        if export_format == "csv":
            content = serialize_csv(records, RESPONSE_ACTION_FIELDS)
            mime_type = "text/csv; charset=utf-8"
        else:
            content = serialize_json(records)
            mime_type = "application/json; charset=utf-8"

        return content, mime_type, len(records)

    def export_logs(
        self,
        log_type: str = "events",
        filters: Optional[Dict[str, Any]] = None,
        export_format: str = "json",
        actor: str = "admin",
    ) -> Tuple[str, str, str, int]:
        """
        Unified dispatch method for exporting logs with audit trail recording.

        Args:
            log_type: 'events' / 'attack_events', 'system_logs' / 'audit', 'actions' / 'response_actions'.
            filters: Dictionary of query filtering constraints.
            export_format: 'csv' or 'json'.
            actor: Username of requesting administrator.

        Returns:
            Tuple of (content_string, mime_type, filename, row_count).
        """
        filters = filters or {}
        norm_type = log_type.strip().lower()
        norm_format = export_format.strip().lower()

        if norm_format not in ("csv", "json"):
            raise ValueError(f"Unsupported export format '{export_format}'. Supported formats are 'csv' and 'json'.")

        now_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

        if norm_type in ("events", "attack_events", "attacks"):
            content, mime_type, count = self.export_attack_events(filters, norm_format)
            filename = f"ids_attack_logs_{now_str}.{norm_format}"
            resolved_type = "attack_events"
        elif norm_type in ("system_logs", "audit", "system"):
            content, mime_type, count = self.export_system_logs(filters, norm_format)
            filename = f"ids_system_logs_{now_str}.{norm_format}"
            resolved_type = "system_logs"
        elif norm_type in ("actions", "response_actions", "mitigations"):
            content, mime_type, count = self.export_response_actions(filters, norm_format)
            filename = f"ids_response_actions_{now_str}.{norm_format}"
            resolved_type = "response_actions"
        else:
            raise ValueError(
                f"Unknown log export type '{log_type}'. Supported types: 'events', 'system_logs', 'actions'."
            )

        # Audit the export event in system_logs (Requirement FR-07, FR-08)
        if self.db is not None:
            # Sanitize filters for audit logging
            sanitized_filters = {
                k: str(v) if isinstance(v, datetime) else v
                for k, v in filters.items()
                if v is not None and v != ""
            }
            try:
                self.db.log_system_event(
                    actor=actor,
                    event="LOGS_EXPORTED",
                    outcome="success",
                    details={
                        "log_type": resolved_type,
                        "format": norm_format,
                        "row_count": count,
                        "filters": sanitized_filters,
                        "filename": filename,
                    },
                )
            except Exception as e:
                logger.error("Failed to log export audit event: %s", e)

        return content, mime_type, filename, count
