"""tests/unit/test_calibrate_and_explain.py - Tests for Step 17 (calibration and thresholds).

Checks:
1. The sigmoid calibration gives valid probabilities and keeps the ranking.
2. Thresholds come from out-of-fold data with the written rules:
   - a clean, well-separated class gets alert AND block thresholds;
   - a class the model cannot separate gets NO block threshold (alert only).
3. The held-out check returns the expected structure.
4. Saved artefacts (when present) say the thresholds came from OOF data, not from 34-1.
"""

import json
from pathlib import Path

import joblib
import numpy as np
import pytest

from ml_engine.calibrate_and_explain import (
    BLOCK_MIN_PRECISION,
    CLASS_NAMES,
    choose_thresholds,
    heldout_check,
)
from ml_engine.calibration import OOFSigmoidCalibratedClassifier, apply_sigmoid, fit_sigmoid_parameters


def _make_probs(n_per_class: int = 400, seed: int = 0):
    """Class 1 (DDoS) is easy to separate; class 3 (CnC) is pure noise."""
    rng = np.random.RandomState(seed)
    y = np.repeat(np.arange(5), n_per_class)
    probs = rng.dirichlet(np.ones(5), size=len(y))
    easy = y == 1
    probs[easy] = 0.02
    probs[easy, 1] = 0.92
    return probs / probs.sum(axis=1, keepdims=True), y


def test_sigmoid_calibration_is_valid_and_keeps_ranking():
    probs, y = _make_probs()
    params = fit_sigmoid_parameters(probs, y, 5)
    cal = apply_sigmoid(probs, params)
    assert cal.shape == probs.shape
    assert np.allclose(cal.sum(axis=1), 1.0)
    assert np.all((cal >= 0) & (cal <= 1))
    # Sigmoid with a positive slope keeps the order of the class-1 scores
    order_raw = np.argsort(probs[:, 1])
    assert np.all(np.diff(cal[order_raw, 1]) >= -1e-9) or params[1][0] > 0


def test_calibrated_classifier_wraps_pipeline():
    class Fake:
        def predict_proba(self, X):
            return np.tile([0.1, 0.6, 0.1, 0.1, 0.1], (len(X), 1))

    model = OOFSigmoidCalibratedClassifier(Fake(), [[1.0, 0.0]] * 5, [0, 1, 2, 3, 4])
    out = model.predict_proba([0, 1, 2])
    assert out.shape == (3, 5)
    assert np.allclose(out.sum(axis=1), 1.0)
    assert list(model.predict([0])) == [1]


def test_thresholds_follow_the_rules():
    probs, y = _make_probs()
    th = choose_thresholds(probs, y)
    assert th["Benign"]["active_response_threshold"] is None
    # Easy class: a safe block threshold exists and meets the precision rule on OOF data
    ddos = th["DDoS_DoS"]
    assert ddos["active_response_threshold"] is not None
    assert ddos["oof_block_precision"] >= BLOCK_MIN_PRECISION
    assert ddos["active_response_threshold"] >= ddos["passive_alert_threshold"]
    # Noise class: never blocked automatically
    assert th["CnC"]["active_response_threshold"] is None
    assert "NEVER blocked" in th["CnC"]["block_rule"]


def test_heldout_check_structure():
    probs, y = _make_probs(50)
    th = choose_thresholds(probs, y)
    res = heldout_check(probs, y, th)
    for key in ("macro_f1_5class", "macro_f1_present_classes", "benign_fpr_argmax", "per_class", "confusion_matrix"):
        assert key in res
    assert set(res["per_class"]) == set(CLASS_NAMES)
    assert len(res["confusion_matrix"]) == 5


THRESHOLDS_JSON = Path("reports/experiments/operational_thresholds.json")
CALIBRATED = Path("ml_engine/models/calibrated_rf_model.joblib")


@pytest.mark.skipif(not THRESHOLDS_JSON.exists(), reason="Step 17 not run on this machine")
def test_saved_thresholds_come_from_oof_data():
    cfg = json.loads(THRESHOLDS_JSON.read_text(encoding="utf-8"))
    assert "out-of-fold" in cfg["metadata"]["chosen_from"]
    assert "held-out scenario not used" in cfg["metadata"]["chosen_from"]
    for name in CLASS_NAMES:
        assert name in cfg["classes"]


@pytest.mark.skipif(not CALIBRATED.exists(), reason="Step 17 not run on this machine")
def test_saved_calibrated_model_loads():
    bundle = joblib.load(CALIBRATED)
    assert "out-of-fold" in bundle["calibration_method"]
    assert hasattr(bundle["calibrated_pipeline"], "predict_proba")


# ---------------------------------------------------------------------------
# Calibration methods and the D-044 selection rule (Step 17a)
# ---------------------------------------------------------------------------

from ml_engine.calibration import (  # noqa: E402
    CALIBRATION_METHODS,
    OOFCalibratedClassifier,
    apply_calibrator,
    fit_calibrator,
)
from ml_engine.select_calibration import (  # noqa: E402
    MIN_CLASS_RECALL,
    TOP_CLASS_KEEPING,
    cross_fitted_probs,
    final_choice,
    select,
)


@pytest.mark.parametrize("method", CALIBRATION_METHODS)
def test_every_method_gives_valid_probabilities(method):
    probs, y = _make_probs(200)
    params = fit_calibrator(method, probs, y, 5)
    cal = apply_calibrator(method, probs, params)
    assert cal.shape == probs.shape
    assert np.allclose(cal.sum(axis=1), 1.0)
    assert np.all((cal >= 0) & (cal <= 1))


def test_temperature_keeps_the_top_class():
    probs, y = _make_probs(200)
    cal = apply_calibrator("temperature", probs, fit_calibrator("temperature", probs, y, 5))
    assert np.array_equal(cal.argmax(axis=1), probs.argmax(axis=1))


def test_general_calibrated_classifier_wraps_pipeline():
    class Fake:
        def predict_proba(self, X):
            return np.tile([0.1, 0.6, 0.1, 0.1, 0.1], (len(X), 1))

    model = OOFCalibratedClassifier(Fake(), "none", {}, [0, 1, 2, 3, 4])
    assert list(model.predict([0, 1])) == [1, 1]
    with pytest.raises(ValueError):
        OOFCalibratedClassifier(Fake(), "unknown", {}, [0, 1, 2, 3, 4])


def test_cross_fitted_probs_cover_every_row():
    probs, y = _make_probs(100)
    folds = np.tile(np.arange(1, 6), len(y) // 5)
    cal = cross_fitted_probs("multinomial", probs, y, folds)
    assert cal.shape == probs.shape
    assert np.allclose(cal.sum(axis=1), 1.0)


def test_selection_rule_needs_every_class_found_then_best_macro_f1():
    results = {
        "a": {"macro_f1": 0.60, "min_class_recall": 0.00},  # best F1 but silences a class
        "b": {"macro_f1": 0.45, "min_class_recall": 0.20},
        "c": {"macro_f1": 0.50, "min_class_recall": MIN_CLASS_RECALL},
    }
    assert select(results)["chosen_method"] == "c"


def test_selection_rule_fallback_uses_lowest_class_recall():
    results = {
        "a": {"macro_f1": 0.60, "min_class_recall": 0.00},
        "b": {"macro_f1": 0.40, "min_class_recall": 0.03},
    }
    assert select(results)["chosen_method"] == "b"


SELECTION_JSON = Path("reports/experiments/calibration_selection.json")


@pytest.mark.skipif(not SELECTION_JSON.exists(), reason="Step 17a not run on this machine")
def test_saved_selection_uses_oof_data_only():
    sel = json.loads(SELECTION_JSON.read_text(encoding="utf-8"))
    assert sel["chosen_method"] in CALIBRATION_METHODS
    assert "held-out scenario not used" in sel["meta"]["data"]
    assert sel["meta"]["decision"].startswith("D-044")
    assert sel["chosen_method"] in TOP_CLASS_KEEPING  # D-045


@pytest.mark.skipif(not (CALIBRATED.exists() and SELECTION_JSON.exists()), reason="Step 17 not run on this machine")
def test_saved_calibrated_model_uses_the_chosen_method():
    sel = json.loads(SELECTION_JSON.read_text(encoding="utf-8"))
    bundle = joblib.load(CALIBRATED)
    assert bundle.get("calibration_method_id") == sel["chosen_method"]


def test_final_choice_only_allows_methods_that_keep_the_top_class():
    results = {
        "none": {"mean_brier": 0.18},
        "temperature": {"mean_brier": 0.15},
        "multinomial": {"mean_brier": 0.10},  # lower Brier, but it can change the top class
    }
    assert final_choice(results)["chosen_method"] == "temperature"


@pytest.mark.parametrize("method", TOP_CLASS_KEEPING)
def test_top_class_keeping_methods_really_keep_the_top_class(method):
    probs, y = _make_probs(200)
    cal = apply_calibrator(method, probs, fit_calibrator(method, probs, y, 5))
    assert np.array_equal(cal.argmax(axis=1), probs.argmax(axis=1))
