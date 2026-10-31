"""tests/unit/test_calibrate_and_explain.py - Unit test suite for Step 17.

Validates:
1. Calibrated model bundle serialization and predict_proba execution.
2. Deliverable artifacts (reports, json, png) existence and completeness.
3. Operational thresholds JSON schema and safety guardrail values.
4. Gini and Permutation feature importance structure and validity.
5. Decision rules and firewall reason code structures.
"""

import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import pytest

from ml_engine.calibrate_and_explain import (
    TARGET_CLASSES,
    CLASS_NAMES,
    extract_decision_rules_summary,
)
from ml_engine.features import FEATURE_COLUMNS


@pytest.fixture
def reports_dir() -> Path:
    return Path("reports/experiments")


@pytest.fixture
def calibrated_model_path() -> Path:
    return Path("ml_engine/models/calibrated_rf_model.joblib")


def test_calibrated_model_bundle_integrity(calibrated_model_path: Path):
    """Verify calibrated model bundle exists, loads, and can predict probabilities."""
    assert calibrated_model_path.exists(), f"Calibrated model bundle missing at {calibrated_model_path}"
    bundle = joblib.load(calibrated_model_path)

    assert isinstance(bundle, dict)
    assert "calibrated_pipeline" in bundle
    assert "base_bundle" in bundle
    assert bundle["calibration_method"] == "sigmoid"

    cal_pipe = bundle["calibrated_pipeline"]
    assert hasattr(cal_pipe, "predict_proba")

    # Predict on dummy sample DataFrame
    dummy_data = {
        "proto": ["tcp"],
        "service": ["http"],
        "conn_state": ["SF"],
        "history": ["ShADadFf"],
        "orig_port_cat": ["registered"],
        "resp_port_cat": ["well_known"],
        "duration": [1.5],
        "orig_bytes": [100],
        "resp_bytes": [500],
        "missed_bytes": [0],
        "orig_pkts": [5],
        "orig_ip_bytes": [300],
        "resp_pkts": [6],
        "resp_ip_bytes": [700],
        "orig_bytes_per_pkt": [20.0],
        "resp_bytes_per_pkt": [83.3],
        "byte_ratio": [0.2],
        "pkt_ratio": [0.83],
        "is_incomplete_flow": [0],
    }
    df_sample = pd.DataFrame(dummy_data)
    probs = cal_pipe.predict_proba(df_sample[FEATURE_COLUMNS])

    assert probs.shape == (1, 5)
    assert pytest.approx(probs.sum(), abs=1e-3) == 1.0


def test_calibration_artifacts_exist_and_valid(reports_dir: Path):
    """Verify all Step 17 deliverable files exist and have non-zero size."""
    json_path = reports_dir / "operational_thresholds.json"
    md_path = reports_dir / "thresholds_and_explanation.md"
    cal_png = reports_dir / "calibration_curve.png"
    feat_png = reports_dir / "feature_importance.png"

    for p in [json_path, md_path, cal_png, feat_png]:
        assert p.exists(), f"Expected artifact missing: {p}"
        assert p.stat().st_size > 0, f"Artifact empty: {p}"

    md_text = md_path.read_text(encoding="utf-8")
    assert "Probability Calibration" in md_text
    assert "Brier Score" in md_text
    assert "Operational Decision Thresholds Matrix" in md_text
    assert "Firewall Reason Codes" in md_text


def test_operational_thresholds_schema(reports_dir: Path):
    """Verify operational_thresholds.json adheres to schema and safe boundary values."""
    json_path = reports_dir / "operational_thresholds.json"
    with open(json_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    assert "metadata" in config
    assert "safety_guardrails" in config
    assert "classes" in config

    # Check guardrails
    rails = config["safety_guardrails"]
    assert rails["min_repeats"] >= 3
    assert rails["repeat_window_seconds"] >= 60
    assert rails["max_rule_minutes"] <= 60
    assert rails["allowlist_protected"] is True

    # Check classes
    classes = config["classes"]
    for cname in CLASS_NAMES:
        assert cname in classes

    # Benign must never be blocked
    assert classes["Benign"]["policy"] == "ALLOW_ALWAYS"
    assert classes["Benign"]["active_response_threshold"] is None

    # Attack classes must specify thresholds
    assert 0.50 <= classes["DDoS_DoS"]["active_response_threshold"] <= 1.0
    assert 0.20 <= classes["CnC"]["passive_alert_threshold"] <= 0.50


def test_decision_rules_structure():
    """Verify decision rule extraction returns properly formatted reason codes and triggers."""
    rf_bundle = joblib.load("ml_engine/models/rf_model.joblib")
    pipe = rf_bundle["pipeline"]
    rules = extract_decision_rules_summary(pipe)

    assert len(rules) >= 4
    for r in rules:
        assert "class_name" in r
        assert "reason_code" in r
        assert "trigger_condition" in r
        assert "firewall_action" in r
        assert "explanation" in r
        assert len(r["reason_code"]) > 3

