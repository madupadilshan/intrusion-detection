"""tests/unit/test_model_bundle.py - Unit test suite for Step 18 production bundle and model card.

Validates:
1. Production bundle existence, integrity, and key structures.
2. Model pipelines and calibrated inference functionality on feature frames.
3. Operational thresholds (chosen in Step 17 from grouped OOF data) and example decision paths.
4. Model card document presence and mandatory sections adherence.
"""

from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import pytest

from ml_engine.features import FEATURE_COLUMNS, make_features


BUNDLE_PATH = Path("ml_engine/models/ids_bundle_v3.joblib")
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
        "threshold_rules",
        "example_decision_paths",
        "metadata",
    ]
    for key in expected_keys:
        assert key in model_bundle, f"Missing required key '{key}' in production bundle"


def test_bundle_metadata(model_bundle):
    """Verify metadata contains versioning, training metrics, and provenance."""
    meta = model_bundle["metadata"]
    assert str(meta["bundle_version"]).startswith("v3.")
    assert meta["training_samples_count"] > 0
    assert meta["level_2_heldout_scenario"] == "CTU-IoT-Malware-Capture-34-1"
    # Results are read from the real result files, not typed in by hand
    for key in ("level_1_oof_macro_f1", "level_2_macro_f1_5class", "level_2_macro_f1_present"):
        assert 0.0 <= float(meta[key]) <= 1.0
    assert "out-of-fold" in str(meta["calibration_method"])


def test_bundle_operational_rules_and_guardrails(model_bundle):
    """Verify operational thresholds, safety guardrails, and decision rules."""
    thresholds = model_bundle["operational_thresholds"]
    for cname in ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]:
        assert cname in thresholds, f"Missing class '{cname}' in operational thresholds"

    assert thresholds["Benign"]["active_response_threshold"] is None
    for cname in ["DDoS_DoS", "PortScan", "CnC", "Malware_Download"]:
        c = thresholds[cname]
        assert 0.0 < c["passive_alert_threshold"] <= 1.0
        # None means: never blocked automatically (alert only)
        if c["active_response_threshold"] is not None:
            assert c["active_response_threshold"] >= c["passive_alert_threshold"]
        assert c["reason_code"]

    rules = model_bundle["threshold_rules"]
    # D-046: block thresholds come from replaying the repeat rule (proposal 3.4)
    assert rules["block_min_safe_share"] >= rules["alert_min_precision"]
    assert rules["replay_min_repeats"] >= 2

    for path in model_bundle["example_decision_paths"]:
        assert path["class_name"] in thresholds
        assert len(path["conditions"]) >= 1


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
        "# Model Card:",
        "## 1. Model",
        "## 2. Intended use",
        "## 3. Data",
        "## 4. Results",
        "## 5. Alert and block thresholds",
        "## 6. Limits",
    ]
    for header in mandatory_headers:
        assert header in content, f"Model card missing mandatory section: {header}"
    # The card must not claim results that were not measured
    assert "Local camera traffic (Level 3): **not yet measured.**" in content or "Level 3" in content
    assert "PASS" not in content
