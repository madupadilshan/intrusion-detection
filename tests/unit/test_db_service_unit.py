"""
Unit tests for DatabaseService configuration, validation, and offline logic.
Group 03 - Real-Time Intrusion Detection and Response System for IP-Camera IoT Networks.
"""

import pytest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from core_engine.db_service import (
    DatabaseService,
    DEFAULT_RETENTION_DAYS,
    DEFAULT_MAX_RULE_MINUTES,
    DEFAULT_REPEAT_WINDOW_SECONDS,
    _load_settings,
)


def test_default_retention_and_settings_loading(tmp_path):
    """Verify default retention periods and loading overrides from settings.yaml."""
    yaml_content = """
retention_days:
  attack_events: 120
  traffic_summaries: 45
  system_logs: 180
  response_actions: 90
  scans: 60
response:
  max_rule_minutes: 45
  repeat_window_seconds: 30
"""
    yaml_file = tmp_path / "test_settings.yaml"
    yaml_file.write_text(yaml_content, encoding="utf-8")

    loaded = _load_settings(yaml_file)
    assert loaded["retention_days"]["attack_events"] == 120
    assert loaded["response"]["max_rule_minutes"] == 45

    # Test initialization with custom settings file without auto_connect
    service = DatabaseService(
        uri="mongodb://localhost:27017/",
        db_name="test_dummy_db",
        settings_path=yaml_file,
        auto_connect=False,
    )
    assert service.retention_days["attack_events"] == 120
    assert service.retention_days["traffic_summaries"] == 45
    assert service.max_rule_minutes == 45
    assert service.repeat_window_seconds == 30


def test_default_fallback_when_settings_missing():
    """Verify standard defaults when settings file does not exist."""
    service = DatabaseService(
        uri="mongodb://localhost:27017/",
        db_name="test_dummy_db",
        settings_path=Path("non_existent_settings.yaml"),
        auto_connect=False,
    )
    assert service.retention_days == DEFAULT_RETENTION_DAYS
    assert service.max_rule_minutes == DEFAULT_MAX_RULE_MINUTES
    assert service.repeat_window_seconds == DEFAULT_REPEAT_WINDOW_SECONDS


def test_doc_formatting_and_date_serialization():
    """Verify _format_doc converts ObjectId and formats datetime objects to ISO strings."""
    doc = {
        "_id": "6723b7891234567890abcdef",
        "timestamp": datetime(2026, 10, 31, 12, 0, 0, tzinfo=timezone.utc),
        "ip": "192.168.50.100",
        "nested": [
            {"updated_at": datetime(2026, 10, 31, 12, 5, 0, tzinfo=timezone.utc)},
            "plain_text",
        ],
    }

    formatted = DatabaseService._format_doc(doc, format_dates=True)
    assert isinstance(formatted["_id"], str)
    assert formatted["timestamp"] == "2026-10-31T12:00:00+00:00"
    assert formatted["nested"][0]["updated_at"] == "2026-10-31T12:05:00+00:00"
    assert formatted["nested"][1] == "plain_text"

    unformatted_dates = DatabaseService._format_doc(doc, format_dates=False)
    assert isinstance(unformatted_dates["timestamp"], datetime)


def test_input_validations_offline():
    """Verify offline input validations without active database connection."""
    service = DatabaseService(auto_connect=False)

    # Disconnected service calls return empty/None gracefully
    assert service.upsert_device({"ip": "192.168.50.1"}) is False
    assert service.get_devices() == []
    assert service.record_attack_event({"src_ip": "1.1.1.1", "dst_ip": "2.2.2.2", "predicted_class": "CnC", "confidence": 0.9}) is None
    assert service.add_to_blocklist("1.1.1.1", "source", "test") is None
    assert service.log_response_action({"target_ip": "1.1.1.1", "action": "block"}) is None
    assert service.log_system_event("admin", "TEST", "SUCCESS") is None
    assert service.create_user("admin", "hash") is None
    assert service.record_traffic_summary(datetime.now(timezone.utc)) is False
    assert service.get_setting("non_existent", default=42) == 42
    assert service.record_scan_start("192.168.50.0/24") is None


def test_drop_database_refuses_non_test_db():
    """Verify drop_database_for_testing protects production databases."""
    service = DatabaseService(db_name="iot_ids_production_db", auto_connect=False)
    # Even if connected, refusal logic triggers if 'test' not in db_name
    service.client = MagicMock()
    assert service.drop_database_for_testing() is False
    service.client.drop_database.assert_not_called()
