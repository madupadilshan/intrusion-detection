"""ml_engine/calibration.py - Probability calibration fitted on grouped out-of-fold predictions.

Why (proposal Sections 2.4 and 3.4):
    Random Forest probabilities may not be well calibrated, so we check and calibrate them
    before confidence values can start an automatic response. The calibration must not be
    fitted on rows that the model was trained on, and it must not use the held-out scenario.

How:
    Step 14 saves the grouped out-of-fold (OOF) probabilities: every training flow gets a
    probability from a model that did NOT see its scenario. For each class k we fit one
    sigmoid (Platt scaling) on these OOF probabilities:

        q_k = 1 / (1 + exp(-(a_k * p_k + b_k)))

    and then divide by the row sum so the 5 values add up to 1. This is the same method as
    scikit-learn's CalibratedClassifierCV(method="sigmoid"), but fitted on OOF data from
    StratifiedGroupKFold (grouped by scenario).
"""

from __future__ import annotations

from typing import Any, List, Sequence

import numpy as np
from sklearn.linear_model import LogisticRegression


def fit_sigmoid_parameters(oof_probs: np.ndarray, y: np.ndarray, n_classes: int) -> List[List[float]]:
    """Fit one Platt sigmoid per class on out-of-fold probabilities. Returns [[a, b], ...]."""
    params: List[List[float]] = []
    for k in range(n_classes):
        target = (y == k).astype(int)
        if target.min() == target.max():
            # Class missing (or the only class): keep probabilities as they are.
            params.append([1.0, 0.0])
            continue
        lr = LogisticRegression(C=1e6, solver="lbfgs", max_iter=1000)
        lr.fit(oof_probs[:, k].reshape(-1, 1), target)
        params.append([float(lr.coef_[0][0]), float(lr.intercept_[0])])
    return params


def apply_sigmoid(probs: np.ndarray, params: Sequence[Sequence[float]]) -> np.ndarray:
    """Apply per-class sigmoids and re-normalise rows to sum to 1."""
    probs = np.asarray(probs, dtype=np.float64)
    out = np.empty_like(probs)
    for k, (a, b) in enumerate(params):
        out[:, k] = 1.0 / (1.0 + np.exp(-(a * probs[:, k] + b)))
    total = out.sum(axis=1, keepdims=True)
    total[total == 0] = 1.0
    return out / total


class OOFSigmoidCalibratedClassifier:
    """A fitted pipeline plus per-class sigmoid calibration (fitted on grouped OOF data)."""

    def __init__(self, base_pipeline: Any, sigmoid_params: Sequence[Sequence[float]], classes: Sequence[int]):
        self.base_pipeline = base_pipeline
        self.sigmoid_params = [list(map(float, p)) for p in sigmoid_params]
        self.classes_ = np.asarray(classes)

    def predict_proba(self, X: Any) -> np.ndarray:
        return apply_sigmoid(self.base_pipeline.predict_proba(X), self.sigmoid_params)

    def predict(self, X: Any) -> np.ndarray:
        return self.classes_[np.argmax(self.predict_proba(X), axis=1)]


# ---------------------------------------------------------------------------
# Other calibration methods (D-044). All are fitted on grouped out-of-fold data only.
# ---------------------------------------------------------------------------

CALIBRATION_METHODS = ("none", "sigmoid_per_class", "temperature", "multinomial", "multinomial_balanced")

METHOD_DESCRIPTIONS = {
    "none": "raw Random Forest probabilities (no calibration)",
    "sigmoid_per_class": "per-class sigmoid (Platt), rows re-normalised",
    "temperature": "one temperature on the log-probabilities (softmax); keeps the raw top class",
    "multinomial": "multinomial logistic regression on the 5 log-probabilities",
    "multinomial_balanced": "multinomial logistic regression on the 5 log-probabilities, class_weight='balanced'",
}

LOG_EPS = 1e-4  # Random Forest gives exact zeros; log(0) is not defined


def _log_probs(probs: np.ndarray) -> np.ndarray:
    return np.log(np.clip(np.asarray(probs, dtype=np.float64), LOG_EPS, 1.0))


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def fit_calibrator(method: str, oof_probs: np.ndarray, y: np.ndarray, n_classes: int) -> dict:
    """Fit one calibration method on out-of-fold probabilities. Returns its parameters."""
    if method not in CALIBRATION_METHODS:
        raise ValueError(f"Unknown calibration method {method!r}; choose one of {CALIBRATION_METHODS}")
    y = np.asarray(y, dtype=np.int64)
    if method == "none":
        return {}
    if method == "sigmoid_per_class":
        return {"sigmoid_params": fit_sigmoid_parameters(oof_probs, y, n_classes)}
    z = _log_probs(oof_probs)
    if method == "temperature":
        from scipy.optimize import minimize_scalar

        rows = np.arange(len(y))

        def nll(log_t: float) -> float:
            p = _softmax(z / np.exp(log_t))
            return float(-np.mean(np.log(np.clip(p[rows, y], 1e-12, 1.0))))

        res = minimize_scalar(nll, bounds=(-3.0, 3.0), method="bounded")
        return {"temperature": float(np.exp(res.x))}
    # multinomial / multinomial_balanced
    lr = LogisticRegression(
        C=1.0,  # with about 1 million rows, this is almost no regularisation
        solver="lbfgs",
        max_iter=300,
        class_weight="balanced" if method == "multinomial_balanced" else None,
    )
    # Standardise the inputs so the solver converges quickly, then fold the scaling back
    # into the weights, so apply_calibrator works on the raw log-probabilities.
    mean = z.mean(axis=0)
    std = z.std(axis=0)
    std[std == 0] = 1.0
    lr.fit((z - mean) / std, y)
    w = lr.coef_ / std
    b0 = lr.intercept_ - w @ mean
    coef = np.zeros((n_classes, z.shape[1]))
    intercept = np.full(n_classes, -1e3)  # a class missing from the fit data gets ~0 probability
    for row, k in enumerate(lr.classes_):
        coef[int(k)] = w[row]
        intercept[int(k)] = b0[row]
    return {"coef": coef.tolist(), "intercept": intercept.tolist()}


def apply_calibrator(method: str, probs: np.ndarray, params: dict) -> np.ndarray:
    """Apply a fitted calibration method. Rows always sum to 1."""
    probs = np.asarray(probs, dtype=np.float64)
    if method == "none":
        total = probs.sum(axis=1, keepdims=True)
        total[total == 0] = 1.0
        return probs / total
    if method == "sigmoid_per_class":
        return apply_sigmoid(probs, params["sigmoid_params"])
    z = _log_probs(probs)
    if method == "temperature":
        return _softmax(z / params["temperature"])
    if method in ("multinomial", "multinomial_balanced"):
        return _softmax(z @ np.asarray(params["coef"]).T + np.asarray(params["intercept"]))
    raise ValueError(f"Unknown calibration method {method!r}")


class OOFCalibratedClassifier:
    """A fitted pipeline plus a calibration method fitted on grouped out-of-fold data (D-044)."""

    def __init__(self, base_pipeline: Any, method: str, params: dict, classes: Sequence[int]):
        if method not in CALIBRATION_METHODS:
            raise ValueError(f"Unknown calibration method {method!r}")
        self.base_pipeline = base_pipeline
        self.method = method
        self.params = params
        self.classes_ = np.asarray(classes)

    def predict_proba(self, X: Any) -> np.ndarray:
        return apply_calibrator(self.method, self.base_pipeline.predict_proba(X), self.params)

    def predict(self, X: Any) -> np.ndarray:
        return self.classes_[np.argmax(self.predict_proba(X), axis=1)]
