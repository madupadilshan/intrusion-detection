#!/usr/bin/env python3
"""
Unit and Integration Tests for Step 14:
Random Forest Classifier Training, Pipeline & Model Artifacts
=============================================================
"""

import time
from pathlib import Path
import pytest
import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from ml_engine.train import (
    build_rf_pipeline,
    CLASS_NAMES,
    CLASS_INDICES,
    DEFAULT_MODEL_PATH,
    DEFAULT_EXPERIMENTS_DIR,
)
from ml_engine.features import (
    FEATURE_COLUMNS,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RF_SEARCH_CSV = DEFAULT_EXPERIMENTS_DIR / "rf_search.csv"
RF_CV_CSV = DEFAULT_EXPERIMENTS_DIR / "rf_cv_results.csv"
RF_REPORT_MD = DEFAULT_EXPERIMENTS_DIR / "rf_training_report.md"


def test_build_rf_pipeline_structure():
    """Verify default RF pipeline components and ColumnTransformer mapping."""
    pipe = build_rf_pipeline(random_seed=42, n_estimators=10, max_depth=5)
    assert isinstance(pipe, Pipeline)
    assert "pre" in pipe.named_steps
    assert "model" in pipe.named_steps

    pre = pipe.named_steps["pre"]
    transformers = pre.transformers
    assert len(transformers) == 1
    name, encoder, cols = transformers[0]
    assert name == "cat"
    assert cols == CATEGORICAL_FEATURES


def test_pipeline_unseen_categories_robustness():
    """Verify that the pipeline gracefully transforms unseen categorical values without errors."""
    pipe = build_rf_pipeline(random_seed=42, n_estimators=5, max_depth=5)

    # Train on small known set
    train_data = {
        "proto": ["tcp", "udp", "icmp"] * 20,
        "service": ["http", "dns", "ssl"] * 20,
        "conn_state": ["S0", "SF", "REJ"] * 20,
        "history": ["ShAdDa", "Dd", "Sr"] * 20,
        "orig_port_cat": ["registered", "dynamic", "well_known"] * 20,
        "resp_port_cat": ["well_known", "registered", "dynamic"] * 20,
    }
    for num_col in NUMERICAL_FEATURES:
        train_data[num_col] = [1.0] * 60

    df_train = pd.DataFrame(train_data)[FEATURE_COLUMNS]
    y_train = np.array([0, 1, 2] * 20)

    pipe.fit(df_train, y_train)

    # Test on completely novel categories
    test_data = {
        "proto": ["sctp", "unknown_proto"],
        "service": ["custom_p2p", "tor"],
        "conn_state": ["STATE_99", "UNKNOWN_STATE"],
        "history": ["ZZZZ", "????"],
        "orig_port_cat": ["new_bin", "alien"],
        "resp_port_cat": ["new_bin2", "alien2"],
    }
    for num_col in NUMERICAL_FEATURES:
        test_data[num_col] = [0.0, 500.0]

    df_test = pd.DataFrame(test_data)[FEATURE_COLUMNS]

    # Should predict without throwing ValueError
    preds = pipe.predict(df_test)
    probs = pipe.predict_proba(df_test)

    assert len(preds) == 2
    assert probs.shape == (2, 3)
    # Probabilities must sum to 1.0
    np.testing.assert_allclose(probs.sum(axis=1), np.ones(2), rtol=1e-5)


@pytest.mark.skipif(not DEFAULT_MODEL_PATH.exists(), reason="Trained model artifact not yet generated")
def test_saved_model_bundle_integrity():
    """Verify serialized model bundle contains all expected keys, classes, and metadata."""
    bundle = joblib.load(DEFAULT_MODEL_PATH)
    assert isinstance(bundle, dict)

    expected_keys = [
        "pipeline",
        "preprocessor",
        "model",
        "feature_columns",
        "categorical_features",
        "numerical_features",
        "classes",
        "class_names",
        "best_params",
        "overall_macro_f1",
        "mean_fold_macro_f1",
        "std_fold_macro_f1",
        "benign_fpr",
        "inference_latency_us",
        "throughput_fps",
        "random_seed",
        "training_samples_count",
    ]
    for key in expected_keys:
        assert key in bundle, f"Missing key in bundle: {key}"

    assert bundle["classes"] == CLASS_INDICES
    assert bundle["class_names"] == CLASS_NAMES
    assert bundle["feature_columns"] == FEATURE_COLUMNS
    assert bundle["training_samples_count"] == 1384070
    assert 0.0 < bundle["overall_macro_f1"] <= 1.0, f"Invalid Macro-F1: {bundle['overall_macro_f1']}"
    assert 0.0 <= bundle["benign_fpr"] <= 1.0, f"Invalid Benign FPR: {bundle['benign_fpr']}"


@pytest.mark.skipif(not DEFAULT_MODEL_PATH.exists(), reason="Trained model artifact not yet generated")
def test_inference_latency_benchmark():
    """Verify that inference latency per flow is well under 1 millisecond (1,000 µs)."""
    bundle = joblib.load(DEFAULT_MODEL_PATH)
    pipeline = bundle["pipeline"]

    dummy_data = {
        "proto": ["tcp"] * 1000,
        "service": ["http"] * 1000,
        "conn_state": ["SF"] * 1000,
        "history": ["ShAdDa"] * 1000,
        "orig_port_cat": ["registered"] * 1000,
        "resp_port_cat": ["well_known"] * 1000,
    }
    for num_col in NUMERICAL_FEATURES:
        dummy_data[num_col] = [10.0] * 1000

    df_bench = pd.DataFrame(dummy_data)[FEATURE_COLUMNS]

    t0 = time.perf_counter()
    _ = pipeline.predict(df_bench)
    t1 = time.perf_counter()

    latency_us_per_flow = ((t1 - t0) / 1000) * 1_000_000
    # Must be under 1,000 µs (1 ms) per flow
    assert latency_us_per_flow < 1000.0, f"Latency too slow: {latency_us_per_flow:.2f} µs/flow"


@pytest.mark.skipif(not RF_REPORT_MD.exists(), reason="Training report not yet generated")
def test_reports_and_csv_artifacts_exist():
    """Verify search CSV, fold results CSV, and markdown training report are present and non-empty."""
    assert RF_SEARCH_CSV.exists()
    assert RF_CV_CSV.exists()
    assert RF_REPORT_MD.exists()

    df_search = pd.read_csv(RF_SEARCH_CSV)
    assert len(df_search) >= 2
    assert "mean_test_score" in df_search.columns

    df_cv = pd.read_csv(RF_CV_CSV)
    assert len(df_cv) == 5
    assert "macro_f1" in df_cv.columns

    report_content = RF_REPORT_MD.read_text(encoding="utf-8")
    assert "Random Forest Model Training & Validation Report" in report_content
    assert "Level 1 Grouped Cross-Validation" in report_content

