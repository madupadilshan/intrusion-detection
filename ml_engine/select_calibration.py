"""ml_engine/select_calibration.py - Step 17a: choose the calibration method (decision D-044).

Proposal links: Sections 2.4 and 3.4; Table 9.

Why:
    D-043 found that the per-class sigmoid calibration makes the model never pick CnC.
    This script compares several calibration methods and picks one with a rule that was
    written in the decision log (D-044) BEFORE the comparison was run.

Data used:
    ONLY the grouped out-of-fold (OOF) probabilities saved by Step 14
    (data/processed/rf_oof_predictions.npz). The held-out scenario 34-1 is NOT used.

How each method is scored (cross-fitted):
    For each of the 5 grouped folds, the calibrator is fitted on the OOF rows of the other
    4 folds and applied to this fold. So no row is scored by a calibrator fitted on it.

Selection rule (D-044):
    1. Keep only methods where every one of the 5 classes has recall >= 0.05.
    2. Among those, choose the highest macro-F1.
    3. If none passes step 1, choose the highest lowest-class recall (ties: higher macro-F1).

Final choice (decision D-045, added after the D-044 choice failed the final check):
    Calibration may change how sure the model is, but not which class wins. So only
    methods that keep the Random Forest's top class are allowed (TOP_CLASS_KEEPING).
    Of these, the one with the lower mean Brier score is used. The D-044 rule result
    is still computed and written, so the history stays visible.

Outputs:
    reports/experiments/calibration_selection.json   (read by Step 17)
    reports/experiments/calibration_selection.md
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
from sklearn.metrics import brier_score_loss, f1_score, precision_recall_fscore_support

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine.calibrate_and_explain import CLASS_NAMES, TARGET_CLASSES, choose_thresholds
from ml_engine.calibration import CALIBRATION_METHODS, METHOD_DESCRIPTIONS, apply_calibrator, fit_calibrator

MIN_CLASS_RECALL = 0.05  # D-044 rule, step 1
TOP_CLASS_KEEPING = ("none", "temperature")  # D-045: methods that never change the winning class

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("select_calibration")


def cross_fitted_probs(method: str, raw: np.ndarray, y: np.ndarray, fold_ids: np.ndarray) -> np.ndarray:
    """Calibrated OOF probabilities where each fold is calibrated by a fit on the other folds."""
    out = np.empty_like(raw, dtype=np.float64)
    for f in np.unique(fold_ids):
        test = fold_ids == f
        params = fit_calibrator(method, raw[~test], y[~test], len(TARGET_CLASSES))
        out[test] = apply_calibrator(method, raw[test], params)
    return out


def score(cal: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    pred = cal.argmax(axis=1)
    prec, rec, f1, _ = precision_recall_fscore_support(y, pred, labels=TARGET_CLASSES, zero_division=0)
    thresholds = choose_thresholds(cal, y)
    blockable = [n for n in CLASS_NAMES[1:] if thresholds[n].get("active_response_threshold") is not None]
    return {
        "macro_f1": round(float(f1_score(y, pred, labels=TARGET_CLASSES, average="macro", zero_division=0)), 4),
        "recall": {n: round(float(r), 4) for n, r in zip(CLASS_NAMES, rec)},
        "precision": {n: round(float(p), 4) for n, p in zip(CLASS_NAMES, prec)},
        "f1": {n: round(float(v), 4) for n, v in zip(CLASS_NAMES, f1)},
        "min_class_recall": round(float(rec.min()), 4),
        "mean_brier": round(float(np.mean([brier_score_loss((y == k).astype(int), cal[:, k]) for k in TARGET_CLASSES])), 4),
        "classes_reaching_block_rule": blockable,
        "thresholds": thresholds,
    }


def select(results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    passing = [m for m, r in results.items() if r["min_class_recall"] >= MIN_CLASS_RECALL]
    if passing:
        best = max(passing, key=lambda m: results[m]["macro_f1"])
        why = (f"every class has recall >= {MIN_CLASS_RECALL:.2f} for: {', '.join(passing)}; "
               f"'{best}' has the highest macro-F1 among them")
    else:
        best = max(results, key=lambda m: (results[m]["min_class_recall"], results[m]["macro_f1"]))
        why = (f"no method gives every class recall >= {MIN_CLASS_RECALL:.2f}; "
               f"'{best}' has the highest lowest-class recall")
    return {"chosen_method": best, "reason": why}


def final_choice(results: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    """D-045: only methods that keep the top class; of these, the lower mean Brier score."""
    allowed = [m for m in TOP_CLASS_KEEPING if m in results]
    best = min(allowed, key=lambda m: results[m]["mean_brier"])
    return {
        "chosen_method": best,
        "reason": (f"D-045: only methods that keep the Random Forest's top class are allowed ({', '.join(allowed)}); "
                   f"'{best}' has the lower mean Brier score"),
    }


def write_report(path: Path, meta: Dict[str, Any], results: Dict[str, Dict[str, Any]], choice: Dict[str, str],
                 rule_choice: Dict[str, str]) -> None:
    L: List[str] = [
        "# Step 17a: Choice of the Calibration Method (D-044)",
        "",
        f"**Generated:** {meta['generated']}  ",
        f"**Data:** grouped out-of-fold probabilities from Step 14 ({meta['rows']:,} flows, {meta['scenarios']} scenarios, "
        f"{meta['folds']} folds). **The held-out scenario 34-1 is not used.**  ",
        "**Scoring:** cross-fitted — each fold is calibrated by a fit on the other folds.",
        "",
        "## 1. Rule (written in D-044 before this comparison)",
        "",
        f"1. Keep only methods where every one of the 5 classes has recall ≥ {MIN_CLASS_RECALL:.2f}.",
        "2. Among those, choose the highest macro-F1.",
        "3. If none passes step 1, choose the highest lowest-class recall (ties: higher macro-F1).",
        "",
        "## 2. Results",
        "",
        "| Method | Macro-F1 | Lowest class recall | " + " | ".join(f"Recall {n}" for n in CLASS_NAMES)
        + " | Mean Brier | Classes reaching the block rule |",
        "| --- | ---: | ---: | " + " | ".join("---:" for _ in CLASS_NAMES) + " | ---: | --- |",
    ]
    for m, r in results.items():
        mark = " **(used)**" if m == choice["chosen_method"] else (" (D-044 rule)" if m == rule_choice["chosen_method"] else "")
        block = ", ".join(r["classes_reaching_block_rule"]) or "none"
        L.append(
            f"| `{m}`{mark} | {r['macro_f1']:.4f} | {r['min_class_recall']:.4f} | "
            + " | ".join(f"{r['recall'][n]:.4f}" for n in CLASS_NAMES)
            + f" | {r['mean_brier']:.4f} | {block} |"
        )
    L += [
        "",
        "Method descriptions:",
        "",
    ]
    L += [f"- `{m}`: {METHOD_DESCRIPTIONS[m]}" for m in results]
    L += [
        "",
        "## 3. Choice",
        "",
        f"**D-044 rule result: `{rule_choice['chosen_method']}`** — {rule_choice['reason']}.",
        "",
        "This method then **failed** the single final check on the held-out scenario 34-1 (decision D-045): it learns "
        "how the model confuses classes on unseen out-of-fold scenarios, and these confusions do not carry over to the "
        "final model trained on all 22 scenarios. For example, it turned most 34-1 DDoS flows into Benign.",
        "",
        f"**Method used now: `{choice['chosen_method']}`** — {choice['reason']}.",
        "",
        "Because this choice was made after a 34-1 result, 34-1 is no longer a clean unseen test (D-045). The clean "
        "test of the model is the local lab data (Steps 20 and 35).",
        "",
        "The block rule is the one from D-040 (precision ≥ 0.95 and at most 1% of benign flows reach the threshold, "
        "measured on the out-of-fold data). It is shown here for information; it was not part of the selection rule.",
        "",
        "## 4. Limits",
        "",
        "- Out-of-fold scores are pessimistic for classes that appear in few scenarios: a fold that holds a scenario "
        "trains without it. For example, each DDoS scenario is a different flood type.",
        "- The class mix of the out-of-fold data comes from the Step 12 sampling (at most 50,000 flows per class and "
        "scenario), not from a real network. Precision depends on this mix.",
        "- The team had seen results for `none` and `sigmoid_per_class` before writing the rule (D-044).",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Step 17a: choose the calibration method from out-of-fold data (D-044).")
    ap.add_argument("--oof-path", type=Path, default=PROJECT_ROOT / "data/processed/rf_oof_predictions.npz")
    ap.add_argument("--output-dir", type=Path, default=PROJECT_ROOT / "reports/experiments")
    args = ap.parse_args()

    t0 = time.perf_counter()
    oof = np.load(args.oof_path, allow_pickle=False)
    raw = oof["oof_probs"].astype(np.float64)
    y = oof["y"].astype(np.int64)
    fold_ids = oof["fold_ids"]
    logger.info("Loaded %d OOF rows, %d folds.", len(y), len(np.unique(fold_ids)))

    results: Dict[str, Dict[str, Any]] = {}
    for m in CALIBRATION_METHODS:
        t = time.perf_counter()
        results[m] = score(cross_fitted_probs(m, raw, y, fold_ids), y)
        logger.info("%-22s macro-F1 %.4f | lowest recall %.4f | block rule reached: %s (%.1f s)", m,
                    results[m]["macro_f1"], results[m]["min_class_recall"],
                    results[m]["classes_reaching_block_rule"] or "none", time.perf_counter() - t)

    rule_choice = select(results)
    choice = final_choice(results)
    meta = {
        "generated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "rows": int(len(y)),
        "scenarios": int(len(set(oof["groups"].tolist()))),
        "folds": int(len(np.unique(fold_ids))),
        "decision": "D-044 (rule), D-045 (final choice)",
        "data": "grouped out-of-fold probabilities from Step 14; held-out scenario not used",
        "scoring": "cross-fitted by fold",
        "min_class_recall_rule": MIN_CLASS_RECALL,
    }
    out = {"meta": meta, **choice, "d044_rule_choice": rule_choice,
           "results": {m: {k: v for k, v in r.items() if k != "thresholds"} for m, r in results.items()}}
    (args.output_dir / "calibration_selection.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    write_report(args.output_dir / "calibration_selection.md", meta, results, choice, rule_choice)
    logger.info("Chosen: %s (%s). Finished in %.1f s.", choice["chosen_method"], choice["reason"], time.perf_counter() - t0)


if __name__ == "__main__":
    main()
