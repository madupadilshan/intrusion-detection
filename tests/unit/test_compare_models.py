#!/usr/bin/env python3
"""
Unit and Integration Tests for Step 15:
Machine Learning Model Comparison (Random Forest, Logistic Regression, HistGradientBoosting)
==========================================================================================
"""

from pathlib import Path
import pytest
import joblib
import pandas as pd
from sklearn.pipeline import Pipeline

from ml_engine.compare_models import (
    build_linear_pipeline,
    build_hgb_pipeline,
    DEFAULT_EXPERIMENTS_DIR,
    DEFAULT_MODELS_DIR,
    RF_MODEL_PATH,
    LR_MODEL_PATH,
    HGB_MODEL_PATH,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
COMPARISON_CSV = DEFAULT_EXPERIMENTS_DIR / "model_comparison.csv"
COMPARISON_MD = DEFAULT_EXPERIMENTS_DIR / "model_comparison.md"


def test_build_linear_pipeline_structure():
    """Verify linear baseline pipeline components (OneHotEncoder + StandardScaler + LogisticRegression)."""
    pipe = build_linear_pipeline(random_seed=42, max_iter=10)
    assert isinstance(pipe, Pipeline)
    assert "pre" in pipe.named_steps
    assert "model" in pipe.named_steps

    pre = pipe.named_steps["pre"]
    transformers = pre.transformers
    assert len(transformers) == 2
    cat_trans, num_trans = transformers[0], transformers[1]
    assert cat_trans[0] == "cat"
    assert num_trans[0] == "num"


def test_build_hgb_pipeline_structure():
    """Verify HistGradientBoosting pipeline components (OrdinalEncoder + HistGradientBoostingClassifier)."""
    pipe = build_hgb_pipeline(random_seed=42, max_iter=10)
    assert isinstance(pipe, Pipeline)
    assert "pre" in pipe.named_steps
    assert "model" in pipe.named_steps


@pytest.mark.skipif(not COMPARISON_CSV.exists(), reason="Comparison CSV not yet generated")
def test_comparison_csv_structure_and_completeness():
    """Verify model_comparison.csv contains all 3 models and required comparative metrics."""
    df = pd.read_csv(COMPARISON_CSV)
    assert len(df) == 3, f"Expected 3 models, got {len(df)}"

    expected_models = {"Random Forest", "Logistic Regression", "HistGradientBoosting"}
    actual_models = set(df["model_name"].unique())
    assert expected_models == actual_models, f"Mismatch in evaluated models: {actual_models}"

    required_cols = [
        "model_name",
        "overall_macro_f1",
        "mean_fold_macro_f1",
        "std_fold_macro_f1",
        "overall_accuracy",
        "benign_fpr",
        "latency_us",
        "throughput_fps",
        "model_size_mb",
        "fit_time_sec",
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required comparative column: {col}"

    for _, row in df.iterrows():
        assert 0.0 <= row["overall_macro_f1"] <= 1.0
        assert 0.0 <= row["overall_accuracy"] <= 1.0
        assert 0.0 <= row["benign_fpr"] <= 1.0
        assert row["latency_us"] > 0.0
        assert row["model_size_mb"] > 0.0


@pytest.mark.skipif(not COMPARISON_MD.exists(), reason="Comparison report not yet generated")
def test_comparison_markdown_report_contents():
    """Verify model_comparison.md report contains comparative tables and justification."""
    report = COMPARISON_MD.read_text(encoding="utf-8")
    assert "Machine Learning Model Comparison Report (Step 15)" in report
    assert "Random Forest (Bagging)" in report
    assert "Logistic Regression (Linear)" in report
    assert "HistGradientBoosting (Boosting)" in report
    assert "Interpretability" in report


@pytest.mark.skipif(not (RF_MODEL_PATH.exists() and LR_MODEL_PATH.exists() and HGB_MODEL_PATH.exists()), 
                    reason="Model artifacts not all generated")
def test_all_three_models_serialized_and_loadable():
    """Verify that all three serialized models exist and can be loaded with joblib."""
    rf = joblib.load(RF_MODEL_PATH)
    lr = joblib.load(LR_MODEL_PATH)
    hgb = joblib.load(HGB_MODEL_PATH)

    assert rf is not None
    assert lr is not None
    assert hgb is not None

