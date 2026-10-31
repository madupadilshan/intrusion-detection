"""tests/unit/test_evaluate.py - Unit test suite for Step 16 Held-Out Evaluation.

Validates:
1. Held-out dataset loading and schema validation.
2. Evaluation output artifacts existence and schema.
3. Multi-class confusion matrix conservation (sum == 23,145).
4. Benign False Positive Rate calculation consistency.
5. PR-AUC score bounding and validity.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import pytest

from ml_engine.evaluate import (
    load_held_out_data,
    load_model_pipeline,
    evaluate_single_model,
    TARGET_CLASSES,
    CLASS_NAMES,
)
from ml_engine.features import FEATURE_COLUMNS


@pytest.fixture
def held_out_path() -> Path:
    return Path("data/processed/heldout/held_out_test.parquet")


@pytest.fixture
def rf_model_path() -> Path:
    return Path("ml_engine/models/rf_model.joblib")


def test_load_held_out_data_integrity(held_out_path: Path):
    """Verify loading held-out test dataset enforces strict scenario and schema rules."""
    assert held_out_path.exists(), f"Held-out test parquet missing at {held_out_path}"
    df, X, y = load_held_out_data(held_out_path)

    assert len(df) == 23145, f"Expected 23,145 flows, found {len(df)}"
    assert (df["scenario_id"] == "CTU-IoT-Malware-Capture-34-1").all()
    assert X.shape == (23145, 19)
    assert len(y) == 23145
    assert set(np.unique(y)).issubset(set(TARGET_CLASSES))


def test_evaluation_artifacts_exist_and_valid():
    """Verify generated CSV, Markdown report, and PNG plot exist and are populated."""
    reports_dir = Path("reports/experiments")
    csv_path = reports_dir / "evaluation_iot23.csv"
    md_path = reports_dir / "evaluation_iot23.md"
    png_path = reports_dir / "confusion_matrix_heldout.png"

    assert csv_path.exists(), "evaluation_iot23.csv not found"
    assert md_path.exists(), "evaluation_iot23.md not found"
    assert png_path.exists(), "confusion_matrix_heldout.png not found"

    df_csv = pd.read_csv(csv_path)
    assert len(df_csv) >= 1
    assert "model_name" in df_csv.columns
    assert "macro_f1_5class" in df_csv.columns
    assert "benign_fpr" in df_csv.columns

    md_content = md_path.read_text(encoding="utf-8")
    assert "Hypothesis H1" in md_content
    assert "CTU-IoT-Malware-Capture-34-1" in md_content
    assert "Confusion Matrix" in md_content


def test_confusion_matrix_conservation(held_out_path: Path, rf_model_path: Path):
    """Verify that confusion matrix rows sum exactly to the true support of each class."""
    df, X, y = load_held_out_data(held_out_path)
    pipe, meta = load_model_pipeline(rf_model_path)
    res = evaluate_single_model("Random Forest", pipe, X, y, meta)

    cm = np.array(res["confusion_matrix"])
    assert cm.shape == (5, 5)
    assert cm.sum() == 23145

    # Check true class support matches confusion matrix row sums
    for cls_id in TARGET_CLASSES:
        expected_support = int((y == cls_id).sum())
        assert cm[cls_id, :].sum() == expected_support


def test_benign_fpr_calculation(held_out_path: Path, rf_model_path: Path):
    """Verify that benign false positive rate matches false alarms divided by total benign."""
    df, X, y = load_held_out_data(held_out_path)
    pipe, meta = load_model_pipeline(rf_model_path)
    res = evaluate_single_model("Random Forest", pipe, X, y, meta)

    cm = np.array(res["confusion_matrix"])
    total_benign = int(cm[0, :].sum())
    false_alarms = int(cm[0, 1:].sum())
    expected_fpr = false_alarms / total_benign

    assert total_benign == 1923
    assert res["benign_total"] == total_benign
    assert res["benign_false_alarms"] == false_alarms
    assert pytest.approx(res["benign_fpr"], rel=1e-4) == expected_fpr


def test_pr_auc_bounded(held_out_path: Path, rf_model_path: Path):
    """Verify PR-AUC scores are strictly bounded between 0 and 1 for present classes."""
    df, X, y = load_held_out_data(held_out_path)
    pipe, meta = load_model_pipeline(rf_model_path)
    res = evaluate_single_model("Random Forest", pipe, X, y, meta)

    for cname, pstats in res["per_class"].items():
        if pstats["support"] > 0:
            pr_auc = pstats["pr_auc"]
            assert pr_auc is not None, f"PR-AUC should not be None for {cname}"
            assert 0.0 <= pr_auc <= 1.0, f"PR-AUC {pr_auc} out of bounds for {cname}"
        else:
            assert pstats["pr_auc"] is None

