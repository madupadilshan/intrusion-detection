"""
core_engine/log_exporter.py - Backward Compatibility Alias for ExportService (Step 28).
"""

from core_engine.export_service import (
    ExportService,
    parse_datetime,
    serialize_csv,
    serialize_json,
    ATTACK_EVENT_FIELDS,
    SYSTEM_LOG_FIELDS,
    RESPONSE_ACTION_FIELDS,
)

__all__ = [
    "ExportService",
    "parse_datetime",
    "serialize_csv",
    "serialize_json",
    "ATTACK_EVENT_FIELDS",
    "SYSTEM_LOG_FIELDS",
    "RESPONSE_ACTION_FIELDS",
]
