"""tests/unit/test_model_bundle.py - Unit test suite for Step 18 production bundle and model card.

Validates:
1. Production bundle existence, integrity, and key structures.
2. Model pipelines and calibrated inference functionality on feature frames.
3. Operational thresholds and safety guardrails configuration completeness.
4. Model card document presence and mandatory sections adherence.
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import pytest

from ml_engine.features import FEATURE_COLUMNS, make_features


BUNDLE_PATH = Path("ml_engine/models/ids_bundle_v1.joblib")
MODEL_CARD_PATH = Path("reports/experiments/model_card.md")


@pytest.fixture(scope="module")
def model_bundle():
    """Load production model bundle once for module tests."""
    assert BUNDLE_PATH.exists(), f"Bundle file missing at {BUNDLE_PATH}"
    bundle = joblib.load(BUNDLE_PATH)
    assert isinstance(bundle, dict), "Loaded bundle must be a dictionary"
    return bundle


def test_bundle_structure_and_keys(model_bundle):
    """Verify all mandatory keys are present in the unified bundle."""
    expected_keys = [
        "pipeline",
        "calibrated_model",
        "feature_columns",
        "categorical_features",
        "numerical_features",
        "classes",
        "class_names",
        "class_to_name",
        "operational_thresholds",
        "safety_guardrails",
        "decision_rules",
        "metadata",
    ]
    for key in expected_keys:
        assert key in model_bundle, f"Missing required key '{key}' in production bundle"


def test_bundle_metadata(model_bundle):
    """Verify metadata contains versioning, training metrics, and provenance."""
    meta = model_bundle["metadata"]
    assert "bundle_version" in meta
    assert meta["bundle_version"] == "v1.0.0"
    assert "training_samples_count" in meta
    assert meta["training_samples_count"] == 1384070
    assert "level_2_heldout_scenario" in meta
    assert meta["level_2_heldout_scenario"] == "CTU-IoT-Malware-Capture-34-1"
    assert "inference_latency_us_flow" in meta
    assert meta["inference_latency_us_flow"] < 100.0  # Well below 1s latency requirement


def test_bundle_operational_rules_and_guardrails(model_bundle):
    """Verify operational thresholds, safety guardrails, and decision rules."""
    thresholds = model_bundle["operational_thresholds"]
    for cname in ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]:
        assert cname in thresholds, f"Missing class '{cname}' in operational thresholds"

    guardrails = model_bundle["safety_guardrails"]
    assert "min_repeats" in guardrails
    assert guardrails["min_repeats"] >= 2
    assert "repeat_window_seconds" in guardrails
    assert "allowlist_protected" in guardrails
    assert guardrails["allowlist_protected"] is True

    rules = model_bundle["decision_rules"]
    assert len(rules) >= 4
    for r in rules:
        assert "reason_code" in r
        assert "firewall_action" in r
        assert "trigger_condition" in r


def test_bundle_inference_execution(model_bundle):
    """Test end-to-end inference using pipeline and calibrated model."""
    raw_data = pd.DataFrame([
        {
            "proto": "tcp",
            "service": "http",
            "conn_state": "SF",
            "history": "ShADdfFa",
            "id.orig_p": 49152,
            "id.resp_p": 80,
            "duration": 0.45,
            "orig_bytes": 240,
            "resp_bytes": 1420,
            "missed_bytes": 0,
            "orig_pkts": 5,
            "orig_ip_bytes": 480,
            "resp_pkts": 8,
            "resp_ip_bytes": 1820,
        },
        {
            "proto": "tcp",
            "service": "-",
            "conn_state": "S0",
            "history": "S",
            "id.orig_p": 55123,
            "id.resp_p": 23,
            "duration": 0.0,
            "orig_bytes": 0,
            "resp_bytes": 0,
            "missed_bytes": 0,
            "orig_pkts": 200,
            "orig_ip_bytes": 12000,
            "resp_pkts": 0,
            "resp_ip_bytes": 0,
        },
    ])

    feat_df = make_features(raw_data)
    assert list(feat_df.columns) == FEATURE_COLUMNS

    pipeline = model_bundle["pipeline"]
    calibrated = model_bundle["calibrated_model"]

    # 1. Pipeline predictions
    preds = pipeline.predict(feat_df)
    assert len(preds) == 2
    assert all(p in [0, 1, 2, 3, 4] for p in preds)

    # 2. Calibrated probabilities
    probs = calibrated.predict_proba(feat_df)
    assert probs.shape == (2, 5)
    assert np.allclose(probs.sum(axis=1), [1.0, 1.0], atol=1e-3)
    assert np.all((probs >= 0.0) & (probs <= 1.0))


def test_model_card_file():
    """Verify model card document exists and contains core sections."""
    assert MODEL_CARD_PATH.exists(), f"Model card missing at {MODEL_CARD_PATH}"
    content = MODEL_CARD_PATH.read_text(encoding="utf-8")
    mandatory_headers = [
        "# Model Card: IoT IP-Camera Intrusion Detection Engine",
        "## 1. Model Details",
        "## 2. Intended Use & Scope",
        "## 3. Training & Validation Data",
        "## 4. Quantitative Performance Metrics",
        "## 5. Cost-Sensitive Operational Decision Thresholds",
        "## 6. Explainable Decision Rules & Audit Reason Codes",
        "## 7. Ethical Considerations & Safety Guardrails",
        "## 8. Caveats, Limitations & Next Steps",
    ]
    for header in mandatory_headers:
        assert header in content, f"Model card missing mandatory section: {header}"
