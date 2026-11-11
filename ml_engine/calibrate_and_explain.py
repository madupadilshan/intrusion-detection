"""ml_engine/calibrate_and_explain.py - Step 17: calibration, explanation and final thresholds.

Proposal links: Sections 2.4 and 3.4; Table 9; Table 11.

What this step does, and which data each part uses:

| Part                                   | Data used                                              |
| -------------------------------------- | ------------------------------------------------------ |
| Probability calibration                | Grouped out-of-fold (OOF) probabilities from Step 14    |
| (method chosen in Step 17a, D-044)     | (`ml_engine/select_calibration.py`, OOF data only)      |
| Reliability curve and Brier score      | OOF probabilities (main), held-out 34-1 (reported)     |
| Alert thresholds                       | Calibrated OOF probabilities ONLY                      |
| Block thresholds (D-046)               | Calibrated OOF probabilities ONLY, with the live repeat |
|                                        | rule replayed on each training flow's time and IPs     |
| Results per original IoT-23 label      | OOF data and held-out 34-1 (proposal 3.2)              |
| Final check of the deployed model      | Held-out scenario 34-1, once, with the fixed thresholds |
| Permutation importance                 | Held-out scenario 34-1 (proposal 2.4: "on held-out data") |
| Example decision paths                 | Trees of the final Random Forest                       |

The held-out scenario is never used to choose a threshold or a setting (proposal 3.4:
"We will not touch the test set while we choose the preprocessing and the hyperparameters").

Inputs:
    data/processed/rf_oof_predictions.npz   (written by ml_engine/train.py, Step 14)
    reports/experiments/calibration_selection.json (written by ml_engine/select_calibration.py, Step 17a)
    ml_engine/models/rf_model.joblib         (final Random Forest from Step 14)
    data/processed/heldout/held_out_test.parquet
Outputs:
    ml_engine/models/calibrated_rf_model.joblib
    reports/experiments/operational_thresholds.json
    reports/experiments/step17_results.json
    reports/experiments/calibration_curve.png
    reports/experiments/feature_importance.png
    reports/experiments/thresholds_and_explanation.md
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.inspection import permutation_importance
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    brier_score_loss,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine.calibration import (
    CALIBRATION_METHODS,
    METHOD_DESCRIPTIONS,
    OOFCalibratedClassifier,
    apply_calibrator,
    fit_calibrator,
)
from ml_engine.features import CATEGORICAL_FEATURES, FEATURE_COLUMNS
from ml_engine.training_rows import load_training_frame
from ml_engine.response_replay import (
    BLOCK_MAX_BENIGN_TARGETS,
    BLOCK_MIN_EVENTS,
    BLOCK_MIN_SAFE_SHARE,
    MIN_LABEL_FLOWS,
    choose_block_threshold,
    detailed_label_table,
    replay_blocks,
)

TARGET_CLASSES = [0, 1, 2, 3, 4]
CLASS_NAMES = ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]
CLASS_TO_NAME = dict(zip(TARGET_CLASSES, CLASS_NAMES))

# Threshold rules (fixed BEFORE looking at any result; applied to calibrated OOF data).
THRESHOLD_GRID = [round(x, 2) for x in np.arange(0.30, 0.991, 0.01)]
ALERT_MIN_PRECISION = 0.50       # an alert should be right at least half of the time
BLOCK_MIN_PRECISION = 0.95       # an automatic block must be right at least 95% of the time
BLOCK_MAX_BENIGN_TRIGGER = 0.01  # at most 1% of benign flows may reach the block threshold
MIN_RECALL_FOR_THRESHOLD = 0.01  # a threshold that catches < 1% of the class is not useful

# Response action per class (proposal Table 5). Used by the decision engine.
CLASS_ACTIONS = {
    "DDoS_DoS": ("drop_source", "DOS_HIGH_RATE_PACKET_FLOOD"),
    "PortScan": ("drop_source", "SCAN_RAPID_PROBE_SWEEP"),
    "CnC": ("block_destination_or_isolate", "CNC_PERSISTENT_BEACON"),
    "Malware_Download": ("block_by_direction", "MALWARE_STAGING_TRANSFER"),
}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("calibrate_explain")


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def load_inputs(oof_path: Path, rf_model_path: Path, held_out_parquet: Path):
    """Load OOF predictions, the final RF bundle and the held-out data."""
    if not oof_path.exists():
        raise FileNotFoundError(
            f"{oof_path} not found. Run Step 14 (ml_engine/train.py) first; it saves the "
            "grouped out-of-fold probabilities."
        )
    oof = np.load(oof_path, allow_pickle=False)
    bundle = joblib.load(rf_model_path)
    pipeline = bundle["pipeline"] if isinstance(bundle, dict) else bundle
    df_test = pd.read_parquet(held_out_parquet)
    X_test = df_test[FEATURE_COLUMNS]
    y_test = df_test["label_idx"].to_numpy(dtype=np.int64)
    return oof, bundle, pipeline, X_test, y_test


# ---------------------------------------------------------------------------
# Calibration metrics
# ---------------------------------------------------------------------------

def calibration_metrics(raw: np.ndarray, cal: np.ndarray, y: np.ndarray) -> Dict[str, Dict[str, Any]]:
    """Brier score and reliability-curve points per class (raw vs calibrated)."""
    out: Dict[str, Dict[str, Any]] = {}
    for k in TARGET_CLASSES:
        name = CLASS_TO_NAME[k]
        yb = (y == k).astype(int)
        if yb.sum() == 0:
            out[name] = {"raw_brier": None, "cal_brier": None}
            continue
        rf, rp = calibration_curve(yb, raw[:, k], n_bins=10)
        cf, cp = calibration_curve(yb, cal[:, k], n_bins=10)
        out[name] = {
            "raw_brier": round(float(brier_score_loss(yb, raw[:, k])), 4),
            "cal_brier": round(float(brier_score_loss(yb, cal[:, k])), 4),
            "raw_curve": [rp.tolist(), rf.tolist()],
            "cal_curve": [cp.tolist(), cf.tolist()],
        }
    return out


def plot_calibration(metrics: Dict[str, Dict[str, Any]], output_png: Path, title: str) -> None:
    names = [n for n in CLASS_NAMES if metrics[n]["raw_brier"] is not None]
    fig, axes = plt.subplots(1, len(names), figsize=(4.2 * len(names), 4.2), dpi=130)
    axes = np.atleast_1d(axes)
    for ax, name in zip(axes, names):
        m = metrics[name]
        ax.plot([0, 1], [0, 1], "k--", alpha=0.6, label="Perfect")
        ax.plot(*m["raw_curve"], "s-", color="#d9534f", label=f"Raw (Brier {m['raw_brier']:.4f})")
        ax.plot(*m["cal_curve"], "o-", color="#0275d8", label=f"Calibrated (Brier {m['cal_brier']:.4f})")
        ax.set_title(name)
        ax.set_xlabel("Mean predicted probability")
        ax.set_ylabel("Fraction of positives")
        ax.grid(True, linestyle=":", alpha=0.6)
        ax.legend(fontsize=7)
    plt.suptitle(title, fontsize=12)
    plt.tight_layout()
    output_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_png, bbox_inches="tight")
    plt.close()


# ---------------------------------------------------------------------------
# Thresholds (OOF only)
# ---------------------------------------------------------------------------

def _rates_at(cal: np.ndarray, y: np.ndarray, k: int, t: float) -> Tuple[float, float, float, int]:
    """Precision, recall and benign trigger rate when class k is flagged.

    A flow is flagged for class k when argmax == k AND max probability >= t. This is the
    same rule the decision engine uses on live flows.
    """
    pred = np.argmax(cal, axis=1)
    conf = cal.max(axis=1)
    flagged = (pred == k) & (conf >= t)
    n_flag = int(flagged.sum())
    tp = int((flagged & (y == k)).sum())
    n_pos = int((y == k).sum())
    n_benign = int((y == 0).sum())
    precision = tp / n_flag if n_flag else 0.0
    recall = tp / n_pos if n_pos else 0.0
    benign_trigger = int((flagged & (y == 0)).sum()) / n_benign if n_benign else 0.0
    return precision, recall, benign_trigger, n_flag


def choose_thresholds(cal_oof: np.ndarray, y_oof: np.ndarray) -> Dict[str, Any]:
    """Choose alert and block thresholds per class from calibrated OOF data only."""
    classes: Dict[str, Any] = {
        "Benign": {
            "active_response_threshold": None,
            "passive_alert_threshold": None,
            "policy": "ALLOW_ALWAYS",
            "notes": "Benign traffic is logged in the traffic summary and never blocked (Table 5).",
        }
    }
    for k in TARGET_CLASSES[1:]:
        name = CLASS_TO_NAME[k]
        rows = [(t, *_rates_at(cal_oof, y_oof, k, t)) for t in THRESHOLD_GRID]

        alert = next((r for r in rows if r[1] >= ALERT_MIN_PRECISION and r[2] >= MIN_RECALL_FOR_THRESHOLD), None)
        alert_note = f"lowest threshold with OOF precision >= {ALERT_MIN_PRECISION:.2f}"
        if alert is None:
            useful = [r for r in rows if r[2] >= MIN_RECALL_FOR_THRESHOLD] or rows
            alert = max(useful, key=lambda r: (r[1], -r[0]))
            alert_note = (
                f"OOF precision never reached {ALERT_MIN_PRECISION:.2f}; threshold with the best "
                "precision was used. Alerts for this class are weak."
            )

        block = next(
            (
                r for r in rows
                if r[1] >= BLOCK_MIN_PRECISION and r[3] <= BLOCK_MAX_BENIGN_TRIGGER and r[2] >= MIN_RECALL_FOR_THRESHOLD
            ),
            None,
        )
        action, reason = CLASS_ACTIONS[name]
        entry: Dict[str, Any] = {
            "passive_alert_threshold": alert[0],
            "oof_alert_precision": round(alert[1], 4),
            "oof_alert_recall": round(alert[2], 4),
            "oof_alert_benign_trigger_rate": round(alert[3], 5),
            "alert_rule": alert_note,
            "action": action,
            "reason_code": reason,
        }
        if block is None:
            entry.update({
                "active_response_threshold": None,
                "block_rule": (
                    f"No threshold reached OOF precision >= {BLOCK_MIN_PRECISION:.2f} with benign trigger "
                    f"rate <= {BLOCK_MAX_BENIGN_TRIGGER:.0%}. This class is NEVER blocked automatically; "
                    "it only raises alerts."
                ),
            })
        else:
            entry.update({
                "active_response_threshold": block[0],
                "oof_block_precision": round(block[1], 4),
                "oof_block_recall": round(block[2], 4),
                "oof_block_benign_trigger_rate": round(block[3], 5),
                "block_rule": (
                    f"lowest threshold with OOF precision >= {BLOCK_MIN_PRECISION:.2f} and benign trigger rate "
                    f"<= {BLOCK_MAX_BENIGN_TRIGGER:.0%}"
                ),
            })
        classes[name] = entry
    return classes


# ---------------------------------------------------------------------------
# Held-out check (once, fixed thresholds)
# ---------------------------------------------------------------------------

def heldout_check(cal: np.ndarray, y: np.ndarray, thresholds: Dict[str, Any]) -> Dict[str, Any]:
    pred = np.argmax(cal, axis=1)
    present = sorted(set(y.tolist()))
    prec, rec, f1, sup = precision_recall_fscore_support(y, pred, labels=TARGET_CLASSES, zero_division=0)
    per_class = {}
    for k in TARGET_CLASSES:
        name = CLASS_TO_NAME[k]
        yb = (y == k).astype(int)
        per_class[name] = {
            "support": int(sup[k]),
            "precision": round(float(prec[k]), 4),
            "recall": round(float(rec[k]), 4),
            "f1": round(float(f1[k]), 4),
            "pr_auc": round(float(average_precision_score(yb, cal[:, k])), 4) if yb.sum() else None,
        }
        cfg = thresholds.get(name, {})
        for level, key in (("alert", "passive_alert_threshold"), ("block", "active_response_threshold")):
            t = cfg.get(key)
            if t is None or k == 0:
                continue
            p_, r_, b_, n_ = _rates_at(cal, y, k, t)
            per_class[name][f"{level}_precision"] = round(p_, 4)
            per_class[name][f"{level}_recall"] = round(r_, 4)
            per_class[name][f"{level}_benign_trigger_rate"] = round(b_, 5)

    conf = cal.max(axis=1)
    benign = y == 0
    alert_any = np.zeros(len(y), dtype=bool)
    block_any = np.zeros(len(y), dtype=bool)
    for k in TARGET_CLASSES[1:]:
        cfg = thresholds.get(CLASS_TO_NAME[k], {})
        if cfg.get("passive_alert_threshold") is not None:
            alert_any |= (pred == k) & (conf >= cfg["passive_alert_threshold"])
        if cfg.get("active_response_threshold") is not None:
            block_any |= (pred == k) & (conf >= cfg["active_response_threshold"])

    return {
        "flows": int(len(y)),
        "accuracy": round(float(accuracy_score(y, pred)), 4),
        "macro_f1_5class": round(float(f1_score(y, pred, labels=TARGET_CLASSES, average="macro", zero_division=0)), 4),
        "macro_f1_present_classes": round(float(f1_score(y, pred, labels=present, average="macro", zero_division=0)), 4),
        "weighted_f1": round(float(f1_score(y, pred, average="weighted", zero_division=0)), 4),
        "benign_fpr_argmax": round(float((benign & (pred != 0)).sum() / max(1, benign.sum())), 5),
        "benign_alert_rate": round(float((benign & alert_any).sum() / max(1, benign.sum())), 5),
        "benign_block_candidate_rate": round(float((benign & block_any).sum() / max(1, benign.sum())), 5),
        "per_class": per_class,
        "confusion_matrix": confusion_matrix(y, pred, labels=TARGET_CLASSES).tolist(),
    }


# ---------------------------------------------------------------------------
# Explanation
# ---------------------------------------------------------------------------

def permutation_importances(pipeline: Any, X: pd.DataFrame, y: np.ndarray, out_png: Path) -> pd.DataFrame:
    """Gini importance (training) and permutation importance on held-out data (proposal 2.4)."""
    rf = pipeline.named_steps["model"]
    gini = pd.Series(rf.feature_importances_, index=FEATURE_COLUMNS)
    idx = np.random.RandomState(42).choice(len(X), size=min(5000, len(X)), replace=False)
    present = sorted(set(y[idx].tolist()))

    def macro_f1_present(est, Xs, ys):
        return f1_score(ys, est.predict(Xs), labels=present, average="macro", zero_division=0)

    perm = permutation_importance(pipeline, X.iloc[idx], y[idx], n_repeats=5, random_state=42,
                                  scoring=macro_f1_present, n_jobs=-1)
    df = pd.DataFrame({
        "feature": FEATURE_COLUMNS,
        "gini_importance": gini.values,
        "perm_importance_mean": perm.importances_mean,
        "perm_importance_std": perm.importances_std,
    }).sort_values("perm_importance_mean", ascending=False).reset_index(drop=True)

    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 6), dpi=130)
    g = df.sort_values("gini_importance", ascending=False).head(10)[::-1]
    a1.barh(g["feature"], g["gini_importance"], color="#2e6da4")
    a1.set_title("Top 10 Gini importances (training data)")
    p = df.head(10)[::-1]
    a2.barh(p["feature"], p["perm_importance_mean"], xerr=p["perm_importance_std"], color="#5cb85c", capsize=3)
    a2.set_title("Top 10 permutation importances (held-out 34-1, macro-F1 drop)")
    for a in (a1, a2):
        a.grid(True, linestyle=":", alpha=0.6)
    plt.tight_layout()
    out_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(out_png, bbox_inches="tight")
    plt.close()
    return df


def example_decision_paths(pipeline: Any, X: pd.DataFrame, y: np.ndarray, cal: np.ndarray,
                           max_conditions: int = 8) -> List[Dict[str, Any]]:
    """Real decision paths: for each class present, the correctly predicted held-out flow with
    the highest calibrated probability, followed through tree 0 of the forest.

    One tree is only one of many votes, so a path is an EXAMPLE of how the model splits the
    data. It is not proof of what caused an attack (proposal 3.4).
    """
    pre = pipeline.named_steps["pre"]
    rf = pipeline.named_steps["model"]
    names = list(pre.get_feature_names_out())
    tree = rf.estimators_[0].tree_
    pred = np.argmax(cal, axis=1)
    paths = []
    for k in sorted(set(y.tolist())):
        cand = np.where((y == k) & (pred == k))[0]
        if len(cand) == 0:
            continue
        i = int(cand[np.argmax(cal[cand, k])])
        row = X.iloc[[i]]
        enc = pre.transform(row)
        node_ids = rf.estimators_[0].decision_path(enc).indices
        conds = []
        for node in node_ids:
            f = tree.feature[node]
            if f < 0:
                continue
            raw_name = names[f].split("__", 1)[-1]
            val = enc[0, f]
            op = "<=" if val <= tree.threshold[node] else ">"
            shown = row.iloc[0][raw_name] if raw_name in row.columns else val
            if raw_name in CATEGORICAL_FEATURES:
                conds.append(f"{raw_name} = {shown} (code {val:g} {op} {tree.threshold[node]:.1f})")
            else:
                conds.append(f"{raw_name} = {float(shown):.4g} ({op} {tree.threshold[node]:.4g})")
        paths.append({
            "class_name": CLASS_TO_NAME[k],
            "calibrated_probability": round(float(cal[i, k]), 4),
            "conditions": conds[:max_conditions],
            "path_length": len(conds),
        })
    return paths


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.yaml"
TRAIN_PARQUET = PROJECT_ROOT / "data" / "processed" / "train_features.parquet"
AUDIT_COLS = ["label_idx", "scenario_id", "ts", "id.orig_h", "id.resp_h", "detailed_label"]


def load_response_settings() -> Dict[str, float]:
    """The repeat rule used live (config/settings.yaml, response section)."""
    import yaml

    cfg: Dict[str, Any] = {}
    for path in (SETTINGS_PATH, PROJECT_ROOT / "config" / "settings.example.yaml"):
        if path.exists():
            cfg = (yaml.safe_load(path.read_text(encoding="utf-8")) or {}).get("response", {}) or {}
            break
    return {
        "min_repeats": int(cfg.get("min_repeats", 3)),
        "repeat_window_seconds": float(cfg.get("repeat_window_seconds", 60)),
        "max_rule_minutes": float(cfg.get("max_rule_minutes", 30)),
    }


def load_audit(train_parquet: Path, y_oof: np.ndarray, groups: np.ndarray) -> pd.DataFrame:
    """Audit columns of the training flows, in the same row order as the OOF arrays (checked)."""
    df = load_training_frame(train_parquet, columns=AUDIT_COLS)  # same rows as Step 14 (D-051)
    if len(df) != len(y_oof) or not np.array_equal(df["label_idx"].to_numpy(np.int64), y_oof) \
            or not np.array_equal(df["scenario_id"].astype(str).to_numpy(), np.asarray(groups).astype(str)):
        raise ValueError("train_features.parquet rows do not line up with the OOF predictions; re-run Steps 12 and 14.")
    return df


def apply_block_rule(thresholds: Dict[str, Any], cal: np.ndarray, y: np.ndarray, audit: pd.DataFrame,
                     rs: Dict[str, float]) -> Dict[str, Any]:
    """D-046: choose each block threshold by replaying the live repeat rule on OOF data."""
    replays: Dict[str, Any] = {}
    sc = audit["scenario_id"].astype(str).to_numpy()
    ts = audit["ts"].to_numpy(np.float64)
    src = audit["id.orig_h"].astype(str).to_numpy()
    dst = audit["id.resp_h"].astype(str).to_numpy()
    for k in TARGET_CLASSES[1:]:
        name = CLASS_TO_NAME[k]
        entry = thresholds[name]
        res = choose_block_threshold(cal, y, sc, ts, src, dst, k, start=entry["passive_alert_threshold"],
                                     min_repeats=rs["min_repeats"], window_s=rs["repeat_window_seconds"],
                                     rule_minutes=rs["max_rule_minutes"])
        replays[name] = res["rows"]
        for key in ("oof_block_precision", "oof_block_recall", "oof_block_benign_trigger_rate"):
            entry.pop(key, None)
        c = res["chosen"]
        if c is None:
            entry["active_response_threshold"] = None
            entry["block_rule"] = (
                f"Replay of the repeat rule ({rs['min_repeats']:.0f} block candidates for the same target in "
                f"{rs['repeat_window_seconds']:.0f} s) on OOF data: no threshold gave >= {BLOCK_MIN_EVENTS} blocks with "
                f">= {BLOCK_MIN_SAFE_SHARE:.0%} fired by malicious flows and <= {BLOCK_MAX_BENIGN_TARGETS:.0%} of benign "
                "targets blocked. This class only raises alerts (D-046)."
            )
        else:
            entry["active_response_threshold"] = c["threshold"]
            entry["oof_replay_blocks"] = c["blocks"]
            entry["oof_replay_safe_share"] = c["safe_share"]
            entry["oof_replay_benign_target_rate"] = c["benign_target_rate"]
            entry["block_rule"] = (
                f"lowest threshold where the replayed repeat rule ({rs['min_repeats']:.0f} in "
                f"{rs['repeat_window_seconds']:.0f} s) gave >= {BLOCK_MIN_EVENTS} blocks, >= {BLOCK_MIN_SAFE_SHARE:.0%} "
                f"fired by malicious flows and <= {BLOCK_MAX_BENIGN_TARGETS:.0%} of benign targets blocked (D-046)"
            )
    return replays


def heldout_replay(thresholds: Dict[str, Any], cal: np.ndarray, y: np.ndarray, df: pd.DataFrame,
                   rs: Dict[str, float]) -> Dict[str, Any]:
    """Replay the chosen block thresholds on 34-1 (reported only)."""
    out: Dict[str, Any] = {}
    if not {"ts", "id.orig_h", "id.resp_h"}.issubset(df.columns):
        return out
    pred, conf = cal.argmax(axis=1), cal.max(axis=1)
    sc = df["scenario_id"].astype(str).to_numpy()
    ts = df["ts"].to_numpy(np.float64)
    src = df["id.orig_h"].astype(str).to_numpy()
    dst = df["id.resp_h"].astype(str).to_numpy()
    for k in TARGET_CLASSES[1:]:
        name = CLASS_TO_NAME[k]
        thr = thresholds[name].get("active_response_threshold")
        if thr is not None:
            out[name] = replay_blocks(pred, conf, y, sc, ts, src, dst, k, thr, rs["min_repeats"],
                                      rs["repeat_window_seconds"], rs["max_rule_minutes"])
    return out


def _pct(v: Optional[float], digits: int = 2) -> str:
    return "—" if v is None else f"{v * 100:.{digits}f}%"


def write_report(path: Path, meta: Dict[str, Any], cal_oof: Dict, cal_ho: Dict, thresholds: Dict,
                 ho: Dict, imp: pd.DataFrame, paths: List[Dict[str, Any]], replays: Optional[Dict[str, Any]] = None,
                 ho_replay: Optional[Dict[str, Any]] = None, labels_oof: Optional[List[Dict[str, Any]]] = None,
                 labels_ho: Optional[List[Dict[str, Any]]] = None, rs: Optional[Dict[str, float]] = None) -> None:
    L: List[str] = [
        "# Step 17: Calibration, Explanation and Final Thresholds",
        "",
        f"**Generated:** {meta['generated']}  ",
        "**Proposal:** Sections 2.4, 3.4; Table 9; Table 11  ",
        f"**Model:** Random Forest from Step 14 + calibration `{meta['calibration_method_id']}` "
        f"({METHOD_DESCRIPTIONS[meta['calibration_method_id']]}), fitted on grouped out-of-fold data "
        f"({meta['oof_rows']:,} training flows, {meta['oof_scenarios']} scenarios). The method was chosen in Step 17a "
        "by the D-044 rule, from out-of-fold data only (`calibration_selection.md`).  ",
        f"**Held-out scenario (used once, for the final check only):** `{meta['heldout_scenario']}` ({ho['flows']:,} flows)",
        "",
        "## 1. What data was used for what",
        "",
        "| Part | Data |",
        "| --- | --- |",
        "| Calibration fit | Grouped OOF probabilities from Step 14 (each flow scored by a model that did not see its scenario) |",
        "| Alert thresholds | Calibrated OOF probabilities only |",
        "| Block thresholds | Calibrated OOF probabilities, with the live repeat rule replayed on the flows' time and IPs (D-046) |",
        "| Final check of the deployed model | Held-out 34-1, once, with the fixed thresholds |",
        "| Permutation importance | Held-out 34-1 (proposal 2.4) |",
        "",
        "Note: scenario 34-1 was already opened once in Step 16 (raw Random Forest). In this version of Step 17 nothing "
        "was chosen from 34-1. Because the team has seen 34-1 results before, this is written down as a limitation.",
        "",
        "## 2. Calibration (reliability and Brier score)",
        "",
        "Lower Brier score is better. The calibration curve plot uses the OOF data (`calibration_curve.png`).",
        "",
        "| Class | OOF raw Brier | OOF calibrated Brier | 34-1 raw Brier | 34-1 calibrated Brier |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for n in CLASS_NAMES:
        a, b = cal_oof[n], cal_ho[n]
        f = lambda v: "—" if v is None else f"{v:.4f}"
        L.append(f"| {n} | {f(a['raw_brier'])} | {f(a['cal_brier'])} | {f(b['raw_brier'])} | {f(b['cal_brier'])} |")
    L += [
        "",
        "## 3. Thresholds (chosen from calibrated OOF data only)",
        "",
        "Rules fixed before looking at any result:",
        f"- **Alert threshold (D-040):** lowest value in 0.30–0.99 where OOF alert precision ≥ {ALERT_MIN_PRECISION:.2f}.",
        "- **Block threshold (D-046, proposal 3.4: a confidence threshold *and* repeats inside a time window):** the live "
        "response rule is replayed on the OOF flows. A block fires when the same target has "
        f"{(rs or {}).get('min_repeats', 3):.0f} block candidates of the class within {(rs or {}).get('repeat_window_seconds', 60):.0f} s "
        f"and is not already blocked (a block lasts {(rs or {}).get('max_rule_minutes', 30):.0f} min). The block threshold is the "
        f"lowest value where at least {BLOCK_MIN_EVENTS} blocks happen, at least {BLOCK_MIN_SAFE_SHARE:.0%} of them are fired by a "
        f"truly malicious flow, and at most {BLOCK_MAX_BENIGN_TARGETS:.0%} of the benign targets are blocked. Otherwise the class "
        "is alert only.",
        "- A flow is flagged for class *k* when the model's top class is *k* and its calibrated probability is at least the threshold "
        "(the same rule the decision engine uses).",
        "- An automatic block also needs the other safety rules (repeats in the time window, allowlist, local-network "
        "protection, maximum rule time, master switch) — see `docs/response_policy.md`.",
        "",
        "| Class | Alert threshold | OOF alert precision | OOF alert recall | Block threshold | OOF replay: blocks | fired by malicious flows | benign targets blocked |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for n in CLASS_NAMES[1:]:
        c = thresholds[n]
        bt = "none (alert only)" if c["active_response_threshold"] is None else f"{c['active_response_threshold']:.2f}"
        L.append(
            f"| {n} | {c['passive_alert_threshold']:.2f} | {_pct(c['oof_alert_precision'])} | {_pct(c['oof_alert_recall'])} | "
            f"{bt} | {c.get('oof_replay_blocks', '—')} | {_pct(c.get('oof_replay_safe_share'))} | "
            f"{_pct(c.get('oof_replay_benign_target_rate'), 3)} |"
        )
    if replays:
        L += ["", "Replay of the repeat rule on the OOF data at each threshold (until no block happens):", ""]
        for n in CLASS_NAMES[1:]:
            rows = replays.get(n, [])
            if not rows:
                continue
            L += [f"**{n}**", "", "| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |",
                  "| ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
            for r in rows:
                L.append(f"| {r['threshold']:.2f} | {r['blocks']} | {r['wrong_blocks']} | {r['right_class_blocks']} | "
                         f"{_pct(r['safe_share'])} | {r['benign_targets_blocked']} of {r['benign_targets']} | {r['scenarios_with_blocks']} |")
            L.append("")
        L += ["Limit: the training data is a sample (at most 50,000 flows per class and scenario), so repeats are rarer than "
              "in full traffic. Large attack classes were cut the most, so correct blocks are likely under-counted.", ""]
    L += [
        "",
        "## 4. Final check on the held-out scenario 34-1 (deployed model, fixed thresholds)",
        "",
        f"- Accuracy: **{ho['accuracy']:.4f}**",
        f"- Macro-F1 over all 5 classes: **{ho['macro_f1_5class']:.4f}** (proposal target ≥ 0.85: "
        f"**{'met' if ho['macro_f1_5class'] >= 0.85 else 'not met'}**)",
        f"- Macro-F1 over the classes present in 34-1: **{ho['macro_f1_present_classes']:.4f}** (34-1 has no Malware_Download flows)",
        f"- Weighted F1: {ho['weighted_f1']:.4f}",
        f"- IoT-23 benign flows predicted as an attack (top class): {_pct(ho['benign_fpr_argmax'], 3)}; "
        f"raising an alert: {_pct(ho['benign_alert_rate'], 3)}; reaching a block threshold: {_pct(ho['benign_block_candidate_rate'], 3)}. "
        "These are IoT-23 benign flows, **not** the local camera traffic named in Hypothesis H1.",
        "",
        "| Class | Support | Precision | Recall | F1 | PR-AUC | Alert precision | Alert recall | Block precision | Block recall |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for n in CLASS_NAMES:
        c = ho["per_class"][n]
        pr_auc = "—" if c["pr_auc"] is None else f"{c['pr_auc']:.4f}"
        L.append(
            f"| {n} | {c['support']:,} | {c['precision']:.4f} | {c['recall']:.4f} | {c['f1']:.4f} | "
            f"{pr_auc} | {_pct(c.get('alert_precision'))} | {_pct(c.get('alert_recall'))} | "
            f"{_pct(c.get('block_precision'))} | {_pct(c.get('block_recall'))} |"
        )
    if ho_replay:
        L += ["", "Replay of the repeat rule on 34-1 with the chosen block thresholds (reported only; nothing chosen from it):", "",
              "| Class | Threshold | Blocks | Wrong (benign) | Right class | Benign targets blocked |",
              "| --- | ---: | ---: | ---: | ---: | ---: |"]
        for n, r in ho_replay.items():
            L.append(f"| {n} | {r['threshold']:.2f} | {r['blocks']} | {r['wrong_blocks']} | {r['right_class_blocks']} | "
                     f"{r['benign_targets_blocked']} of {r['benign_targets']} |")
    L += [
        "",
        "Confusion matrix (rows = true class, columns = predicted class, order: " + ", ".join(CLASS_NAMES) + "):",
        "",
        "```",
    ]
    for n, row in zip(CLASS_NAMES, ho["confusion_matrix"]):
        L.append(f"{n:<17}" + "".join(f"{v:>10,}" for v in row))
    L += [
        "```",
        "",
        "## 5. Feature importance",
        "",
        "Gini importance comes from training. Permutation importance is the drop in macro-F1 (classes present) when one "
        "feature is shuffled in a 5,000-flow sample of 34-1 (proposal 2.4). One importance value is not proof of what "
        "caused an attack (proposal 3.4).",
        "",
        "| Feature | Gini importance | Permutation importance (mean ± std) |",
        "| --- | ---: | ---: |",
    ]
    for _, r in imp.iterrows():
        L.append(f"| `{r['feature']}` | {r['gini_importance']:.4f} | {r['perm_importance_mean']:.4f} ± {r['perm_importance_std']:.4f} |")
    L += [
        "",
        "## 6. Example decision paths (tree 0 of the forest)",
        "",
        "For each class in 34-1, the correctly predicted flow with the highest calibrated probability, followed through the "
        "first tree. These are real splits from the trained model, shown as examples only.",
        "",
    ]
    for p in paths:
        L.append(f"**{p['class_name']}** (calibrated probability {p['calibrated_probability']:.4f}; "
                 f"first {len(p['conditions'])} of {p['path_length']} splits):")
        L += [f"{i}. {c}" for i, c in enumerate(p["conditions"], 1)]
        L.append("")
    L += [
        "## 7. Reason codes used by the response policy",
        "",
        "The reason codes (`DOS_HIGH_RATE_PACKET_FLOOD`, `SCAN_RAPID_PROBE_SWEEP`, `CNC_PERSISTENT_BEACON`, "
        "`MALWARE_STAGING_TRANSFER`) are names the team gave to each class for the audit log. They are **not** rules taken "
        "from the model.",
        "",
    ]
    for title, rows in (("out-of-fold training data", labels_oof), ("held-out scenario 34-1", labels_ho)):
        if not rows:
            continue
        L += [f"## 8. Results per original IoT-23 label — {title} (proposal 3.2)", "",
              f"Labels with at least {MIN_LABEL_FLOWS} flows. 'Right group' = the model's top class is the group the label "
              "belongs to (Table 5 mapping).", "",
              "| Original label | Group | Flows | Put in the right group | Called an attack |",
              "| --- | --- | ---: | ---: | ---: |"]
        for r in rows:
            L.append(f"| {r['label']} | {r['group']} | {r['flows']:,} | {_pct(r['right_group_share'])} | {_pct(r['called_attack_share'])} |")
        L.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Step 17: calibration, explanation and final thresholds.")
    ap.add_argument("--oof-path", type=Path, default=PROJECT_ROOT / "data/processed/rf_oof_predictions.npz")
    ap.add_argument("--rf-model-path", type=Path, default=PROJECT_ROOT / "ml_engine/models/rf_model.joblib")
    ap.add_argument("--held-out-parquet", type=Path, default=PROJECT_ROOT / "data/processed/heldout/held_out_test.parquet")
    ap.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "reports/experiments")
    ap.add_argument("--calibrated-model-path", type=Path, default=PROJECT_ROOT / "ml_engine/models/calibrated_rf_model.joblib")
    ap.add_argument("--selection-path", type=Path, default=PROJECT_ROOT / "reports/experiments/calibration_selection.json",
                    help="Result of Step 17a (ml_engine/select_calibration.py).")
    ap.add_argument("--train-parquet", type=Path, default=TRAIN_PARQUET,
                    help="Training flows with audit columns (Step 12), same row order as the OOF arrays.")
    ap.add_argument("--method", choices=CALIBRATION_METHODS, default=None,
                    help="Override the method chosen in Step 17a (for testing only).")
    args = ap.parse_args()

    method = args.method
    if method is None:
        if not args.selection_path.exists():
            raise FileNotFoundError(
                f"{args.selection_path} not found. Run Step 17a first: python ml_engine/select_calibration.py"
            )
        method = json.loads(args.selection_path.read_text(encoding="utf-8"))["chosen_method"]
    logger.info("Calibration method: %s (%s)", method, METHOD_DESCRIPTIONS[method])

    t0 = time.perf_counter()
    oof, base_bundle, pipeline, X_test, y_test = load_inputs(args.oof_path, args.rf_model_path, args.held_out_parquet)
    raw_oof, y_oof = oof["oof_probs"].astype(np.float64), oof["y"].astype(np.int64)
    logger.info("Loaded %d OOF rows from %d scenarios.", len(y_oof), len(set(oof["groups"].tolist())))

    # 1. Calibration on grouped OOF data
    params = fit_calibrator(method, raw_oof, y_oof, len(TARGET_CLASSES))
    cal_oof = apply_calibrator(method, raw_oof, params)
    calibrated = OOFCalibratedClassifier(pipeline, method, params, TARGET_CLASSES)

    # 2. Thresholds from calibrated OOF data only (alert: D-040; block: D-046 repeat-rule replay)
    thresholds = choose_thresholds(cal_oof, y_oof)
    rs = load_response_settings()
    audit = load_audit(args.train_parquet, y_oof, oof["groups"])
    replays = apply_block_rule(thresholds, cal_oof, y_oof, audit, rs)
    labels_oof = detailed_label_table(cal_oof.argmax(axis=1), y_oof, audit["detailed_label"].to_numpy())

    # 3. Final check on held-out 34-1 (once)
    raw_ho = pipeline.predict_proba(X_test)
    cal_ho = apply_calibrator(method, raw_ho, params)
    ho = heldout_check(cal_ho, y_test, thresholds)
    df_ho = pd.read_parquet(args.held_out_parquet)
    ho_replay = heldout_replay(thresholds, cal_ho, y_test, df_ho, rs)
    labels_ho = (detailed_label_table(cal_ho.argmax(axis=1), y_test, df_ho["detailed_label"].to_numpy())
                 if "detailed_label" in df_ho.columns else [])

    # 4. Calibration metrics and plot
    cm_oof = calibration_metrics(raw_oof, cal_oof, y_oof)
    cm_ho = calibration_metrics(raw_ho, cal_ho, y_test)
    plot_calibration(cm_oof, args.output_dir / "calibration_curve.png",
                     "Reliability curves on grouped out-of-fold training data")

    # 5. Explanation
    imp = permutation_importances(pipeline, X_test, y_test, args.output_dir / "feature_importance.png")
    paths = example_decision_paths(pipeline, X_test, y_test, cal_ho)

    # 6. Save
    joblib.dump({
        "calibrated_pipeline": calibrated,
        "calibration_method_id": method,
        "calibration_params": params,
        "calibration_method": f"{METHOD_DESCRIPTIONS[method]}; fitted on grouped out-of-fold probabilities "
                              "(method chosen in Step 17a: D-044 rule, D-045 final choice)",
        "oof_rows": int(len(y_oof)),
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    }, args.calibrated_model_path, compress=3)

    meta = {
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "oof_rows": int(len(y_oof)),
        "oof_scenarios": int(len(set(oof["groups"].tolist()))),
        "heldout_scenario": "CTU-IoT-Malware-Capture-34-1",
        "calibration_method_id": method,
    }
    thresholds_json = {
        "metadata": {
            "version": "3.0",
            "generated_date": meta["generated"][:10],
            "chosen_from": "calibrated grouped out-of-fold training data (Step 14 OOF); held-out scenario not used",
            "rules": {
                "alert_min_precision": ALERT_MIN_PRECISION,
                "min_recall_for_threshold": MIN_RECALL_FOR_THRESHOLD,
                "block_rule": "D-046: confidence threshold + repeats in a time window (proposal 3.4), replayed on OOF data",
                "block_min_events": BLOCK_MIN_EVENTS,
                "block_min_safe_share": BLOCK_MIN_SAFE_SHARE,
                "block_max_benign_target_rate": BLOCK_MAX_BENIGN_TARGETS,
                "replay_min_repeats": rs["min_repeats"],
                "replay_window_seconds": rs["repeat_window_seconds"],
                "replay_max_rule_minutes": rs["max_rule_minutes"],
            },
        },
        "classes": thresholds,
    }
    (args.output_dir / "operational_thresholds.json").write_text(json.dumps(thresholds_json, indent=2), encoding="utf-8")
    results = {
        "meta": meta,
        "level_1_oof": {
            "macro_f1": round(float(f1_score(y_oof, np.argmax(raw_oof, axis=1), labels=TARGET_CLASSES, average="macro", zero_division=0)), 4),
            "accuracy": round(float(accuracy_score(y_oof, np.argmax(raw_oof, axis=1))), 4),
        },
        "calibration_oof": {k: {"raw_brier": v["raw_brier"], "cal_brier": v["cal_brier"]} for k, v in cm_oof.items()},
        "calibration_heldout": {k: {"raw_brier": v["raw_brier"], "cal_brier": v["cal_brier"]} for k, v in cm_ho.items()},
        "heldout_final_check": ho,
        "block_replay_oof": replays,
        "block_replay_heldout": ho_replay,
        "original_labels_oof": labels_oof,
        "original_labels_heldout": labels_ho,
        "permutation_importance_top5": imp.head(5)[["feature", "perm_importance_mean"]].to_dict("records"),
        "example_decision_paths": paths,
        "rf_best_params": base_bundle.get("best_params", {}) if isinstance(base_bundle, dict) else {},
        "rf_inference_latency_us": base_bundle.get("inference_latency_us") if isinstance(base_bundle, dict) else None,
        "rf_throughput_fps": base_bundle.get("throughput_fps") if isinstance(base_bundle, dict) else None,
        "training_samples_count": base_bundle.get("training_samples_count") if isinstance(base_bundle, dict) else None,
    }
    (args.output_dir / "step17_results.json").write_text(json.dumps(results, indent=2, default=str), encoding="utf-8")
    write_report(args.output_dir / "thresholds_and_explanation.md", meta, cm_oof, cm_ho, thresholds, ho, imp, paths,
                 replays, ho_replay, labels_oof, labels_ho, rs)
    logger.info("Step 17 finished in %.1f s. Held-out macro-F1 (5 classes) = %.4f", time.perf_counter() - t0, ho["macro_f1_5class"])


if __name__ == "__main__":
    main()
