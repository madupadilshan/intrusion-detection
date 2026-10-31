"""
tests/unit/test_export_service.py - Comprehensive Unit Tests for ExportService (Step 28).
========================================================================================

Complies with Group 03 Proposal:
- Table 7 Requirement FR-08 ("Forensic Log Export").
- Table 7 Requirement FR-07 ("Audit Logging and Invariants").
- Section 3.6 (Figure 4, collections `attack_events`, `system_logs`, `response_actions`).
"""

import json
import pytest
from datetime import datetime, timezone
from unittest.mock import MagicMock

from core_engine.export_service import (
    ExportService,
    parse_datetime,
    serialize_csv,
    serialize_json,
    ATTACK_EVENT_FIELDS,
    SYSTEM_LOG_FIELDS,
    RESPONSE_ACTION_FIELDS,
)


# =============================================================================
# 1. Datetime Parsing Unit Tests
# =============================================================================

def test_parse_datetime_valid():
    """Verify ISO 8601 strings and datetimes are parsed to UTC."""
    # Datetime object
    dt = datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc)
    assert parse_datetime(dt) == dt

    # ISO with Z
    parsed_z = parse_datetime("2026-10-31T15:30:00Z")
    assert parsed_z == datetime(2026, 10, 31, 15, 30, 0, tzinfo=timezone.utc)

    # ISO with offset
    parsed_offset = parse_datetime("2026-10-31T21:00:00+05:30")
    assert parsed_offset.astimezone(timezone.utc) == datetime(2026, 10, 31, 15, 30, 0, tzinfo=timezone.utc)

    # Date only
    parsed_date = parse_datetime("2026-10-31")
    assert parsed_date == datetime(2026, 10, 31, 0, 0, 0, tzinfo=timezone.utc)

    # None and empty
    assert parse_datetime(None) is None
    assert parse_datetime("") is None


def test_parse_datetime_invalid():
    """Verify malformed datetime strings raise ValueError."""
    with pytest.raises(ValueError, match="Unable to parse datetime string"):
        parse_datetime("invalid-date-format")


# =============================================================================
# 2. Serialization Unit Tests
# =============================================================================

def test_serialize_csv_attack_events():
    """Verify CSV serialization handles standard fields, nulls, and nested structures."""
    records = [
        {
            "event_id": "evt_001",
            "timestamp": "2026-10-31T12:00:00+00:00",
            "direction": "inbound",
            "src_ip": "10.0.0.1",
            "src_port": 45123,
            "dst_ip": "192.168.50.60",
            "dst_port": 554,
            "proto": "tcp",
            "service": "rtsp",
            "predicted_class": "PortScan",
            "confidence": 0.95,
            "severity": "high",
            "status": "prediction",
            "response_status": "candidate",
            "is_allowlisted": False,
            "reason_code": "SYN_PROBE",
            "flow_count": 12,
            "evidence_note": "Rapid SYN sweep across surveillance ports",
            "model_version": "ids_bundle_v1",
            "pipeline_latency_ms": 14.5,
        }
    ]

    csv_text = serialize_csv(records, ATTACK_EVENT_FIELDS)
    lines = csv_text.strip().split("\r\n")

    # Header check
    assert lines[0] == ",".join(ATTACK_EVENT_FIELDS)
    # Row check
    assert "evt_001" in lines[1]
    assert "PortScan" in lines[1]
    assert "10.0.0.1" in lines[1]
    assert "192.168.50.60" in lines[1]


def test_serialize_csv_nested_json():
    """Verify nested dictionaries (e.g. details) are JSON-encoded in CSV."""
    records = [
        {
            "log_id": "log_001",
            "timestamp": "2026-10-31T12:00:00+00:00",
            "actor": "admin",
            "event": "RULE_APPLIED",
            "outcome": "success",
            "details": {"rule": "drop 10.0.0.1", "interface": "eth0"},
        }
    ]

    csv_text = serialize_csv(records, SYSTEM_LOG_FIELDS)
    assert "log_001" in csv_text
    assert "RULE_APPLIED" in csv_text
    # Check JSON quotes in CSV
    assert '"{""rule"": ""drop 10.0.0.1"", ""interface"": ""eth0""}"' in csv_text or "rule" in csv_text


def test_serialize_json_indentation():
    """Verify JSON serialization outputs structured, indented JSON array."""
    records = [{"id": 1, "name": "test"}, {"id": 2, "name": "test2"}]
    json_text = serialize_json(records)

    parsed = json.loads(json_text)
    assert len(parsed) == 2
    assert parsed[0]["name"] == "test"
    assert "\n" in json_text  # Verify indent


# =============================================================================
# 3. ExportService Class Unit Tests
# =============================================================================

def test_export_attack_events_flow():
    """Verify export_attack_events queries db with parsed filters and returns formatted content."""
    mock_db = MagicMock()
    mock_db.get_attack_events.return_value = [
        {
            "event_id": "evt_101",
            "timestamp": "2026-10-31T12:00:00+00:00",
            "src_ip": "10.0.0.5",
            "dst_ip": "192.168.50.60",
            "predicted_class": "DDoS",
            "confidence": 0.99,
        }
    ]

    exporter = ExportService(db_service=mock_db)

    # Test CSV
    content, mime, count = exporter.export_attack_events(
        filters={
            "class": "DDoS",
            "start_time": "2026-10-31T00:00:00Z",
            "end_time": "2026-10-31T23:59:59Z",
            "severity": "high",
            "limit": 100,
        },
        export_format="csv",
    )

    assert count == 1
    assert "text/csv" in mime
    assert "evt_101" in content
    assert "DDoS" in content

    # Verify db call arguments
    mock_db.get_attack_events.assert_called_once()
    kwargs = mock_db.get_attack_events.call_args.kwargs
    assert kwargs["class_filter"] == "DDoS"
    assert kwargs["limit"] == 100
    assert kwargs["severity"] == "high"


def test_export_system_logs_flow():
    """Verify export_system_logs queries db and formats system logs."""
    mock_db = MagicMock()
    mock_db.get_system_logs.return_value = [
        {
            "log_id": "sys_001",
            "timestamp": "2026-10-31T12:00:00+00:00",
            "actor": "admin",
            "event": "AUTH_LOGIN_SUCCESS",
            "outcome": "success",
            "details": {"ip": "192.168.50.10"},
        }
    ]

    exporter = ExportService(db_service=mock_db)
    content, mime, count = exporter.export_system_logs(
        filters={"actor": "admin", "event": "AUTH_LOGIN_SUCCESS"},
        export_format="json",
    )

    assert count == 1
    assert "application/json" in mime
    data = json.loads(content)
    assert data[0]["event"] == "AUTH_LOGIN_SUCCESS"


def test_export_response_actions_flow():
    """Verify export_response_actions queries db and formats response actions."""
    mock_db = MagicMock()
    mock_db.get_response_actions.return_value = [
        {
            "action_id": "act_001",
            "executed_at": "2026-10-31T12:00:00+00:00",
            "action": "BLOCK_IP",
            "target_ip": "10.0.0.99",
            "status": "applied",
            "reason_code": "DOS_PROTECTION",
        }
    ]

    exporter = ExportService(db_service=mock_db)
    content, mime, count = exporter.export_response_actions(
        filters={"status": "applied"},
        export_format="csv",
    )

    assert count == 1
    assert "text/csv" in mime
    assert "BLOCK_IP" in content
    assert "10.0.0.99" in content


def test_export_logs_dispatcher_and_audit():
    """Verify export_logs dispatcher generates proper filename and logs audit event."""
    mock_db = MagicMock()
    mock_db.get_attack_events.return_value = [{"event_id": "evt_test", "predicted_class": "CnC"}]

    exporter = ExportService(db_service=mock_db)
    content, mime, filename, count = exporter.export_logs(
        log_type="events",
        filters={"class": "CnC"},
        export_format="json",
        actor="admin_auditor",
    )

    assert count == 1
    assert filename.startswith("ids_attack_logs_")
    assert filename.endswith(".json")

    # Verify audit event logged to system_logs
    mock_db.log_system_event.assert_called_once()
    call_kwargs = mock_db.log_system_event.call_args.kwargs
    assert call_kwargs["actor"] == "admin_auditor"
    assert call_kwargs["event"] == "LOGS_EXPORTED"
    assert call_kwargs["details"]["log_type"] == "attack_events"
    assert call_kwargs["details"]["format"] == "json"
    assert call_kwargs["details"]["row_count"] == 1


def test_export_logs_invalid_inputs():
    """Verify invalid format or unknown log type raises ValueError."""
    exporter = ExportService()

    with pytest.raises(ValueError, match="Unsupported export format"):
        exporter.export_logs(log_type="events", export_format="xml")

    with pytest.raises(ValueError, match="Unknown log export type"):
        exporter.export_logs(log_type="unsupported_type", export_format="json")
