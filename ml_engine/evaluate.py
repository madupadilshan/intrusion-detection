"""ml_engine/evaluate.py - Level 2 Held-Out Evaluation on Scenario Capture-34-1.

Governing Standards:
- Group 03 Research Proposal: Sections 1.3, 2.4, 3.4; Table 9; Hypothesis H1; RQ1, RQ2.
- Step-by-Step Guide: Step 16 (Evaluate on the held-out scenario).
- Supervisor Checkpoint C4: Seal held-out test data until model training is frozen.

This module evaluates the primary Random Forest classifier alongside the baseline models
(Logistic Regression and HistGradientBoosting) on the sealed held-out dataset:
`data/processed/heldout/held_out_test.parquet` (Scenario: CTU-IoT-Malware-Capture-34-1, 23,145 flows).

It computes:
1. Multi-class Macro, Micro, and Weighted Precision, Recall, and F1.
2. Per-class Precision, Recall, F1, and PR-AUC.
3. Confusion matrix for 5 target classes.
4. Benign False Positive Rate (FPR).
5. Inference latency on the held-out batch.
6. Generalisation gap between Level 1 (5-fold Grouped CV) and Level 2 (Held-out).
7. Formal scientific evaluation of Hypothesis H1 (Macro-F1 >= 0.85).
"""

from __future__ import annotations

import argparse
import datetime
import logging
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import joblib
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless plot generation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.preprocessing import label_binarize

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine.features import FEATURE_COLUMNS

TARGET_CLASSES = [0, 1, 2, 3, 4]
CLASS_NAMES = ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]
CLASS_TO_NAME = dict(zip(TARGET_CLASSES, CLASS_NAMES))

# Setup module logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("evaluate")


def load_held_out_data(held_out_path: Path) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    """Load and validate the sealed held-out test parquet dataset.

    Args:
        held_out_path: Path to `held_out_test.parquet`.

    Returns:
        Tuple of (full DataFrame, feature DataFrame X, ground-truth label array y).
    """
    if not held_out_path.exists():
        raise FileNotFoundError(f"Held-out test dataset not found at {held_out_path}")

    logger.info("Loading sealed held-out test dataset from: %s", held_out_path)
    df = pd.read_parquet(held_out_path)

    # Validate row count and scenario integrity
    expected_scenario = "CTU-IoT-Malware-Capture-34-1"
    unique_scenarios = df["scenario_id"].unique()
    if len(unique_scenarios) != 1 or unique_scenarios[0] != expected_scenario:
        raise ValueError(
            f"Held-out dataset must strictly contain only scenario '{expected_scenario}'. "
            f"Found: {unique_scenarios}"
        )

    logger.info(
        "Successfully verified scenario '%s' with %d flows across classes: %s",
        expected_scenario,
        len(df),
        dict(df["label_idx"].value_counts().sort_index()),
    )

    # Verify all feature columns exist
    missing_cols = [c for c in FEATURE_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(f"Held-out dataset missing required feature columns: {missing_cols}")

    X = df[FEATURE_COLUMNS]
    y = df["label_idx"].to_numpy(dtype=np.int64)

    return df, X, y


def load_model_pipeline(model_path: Path) -> Tuple[Any, Optional[Dict[str, Any]]]:
    """Load a serialized model bundle or pipeline.

    Args:
        model_path: Path to serialized `.joblib` file.

    Returns:
        Tuple of (pipeline, metadata_dict or None).
    """
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found at: {model_path}")

    loaded = joblib.load(model_path)
    if isinstance(loaded, dict) and "pipeline" in loaded:
        return loaded["pipeline"], loaded
    return loaded, None


def evaluate_single_model(
    name: str,
    pipeline: Any,
    X: pd.DataFrame,
    y: np.ndarray,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Evaluate a single pipeline on the held-out feature set.

    Args:
        name: Name of the model.
        pipeline: Trained scikit-learn Pipeline.
        X: Feature DataFrame.
        y: Ground-truth class indices.
        metadata: Optional metadata dictionary saved during training.

    Returns:
        Dictionary of comprehensive evaluation metrics.
    """
    logger.info("Evaluating model: %s on %d held-out flows...", name, len(X))

    # Benchmark latency on held-out batch
    start_time = time.perf_counter()
    y_pred = pipeline.predict(X)
    elapsed_sec = time.perf_counter() - start_time
    latency_us_flow = (elapsed_sec / len(X)) * 1e6
    throughput_fps = len(X) / elapsed_sec if elapsed_sec > 0 else 0.0

    # Obtain class probabilities if supported
    probs: Optional[np.ndarray] = None
    if hasattr(pipeline, "predict_proba"):
        try:
            probs = pipeline.predict_proba(X)
        except Exception as e:
            logger.warning("Could not obtain predict_proba for %s: %s", name, e)

    # Multi-class macro, micro, weighted metrics (across all 5 possible classes)
    macro_p = float(precision_score(y, y_pred, average="macro", zero_division=0))
    macro_r = float(recall_score(y, y_pred, average="macro", zero_division=0))
    macro_f1 = float(f1_score(y, y_pred, average="macro", zero_division=0))

    micro_p = float(precision_score(y, y_pred, average="micro", zero_division=0))
    micro_r = float(recall_score(y, y_pred, average="micro", zero_division=0))
    micro_f1 = float(f1_score(y, y_pred, average="micro", zero_division=0))

    weighted_p = float(precision_score(y, y_pred, average="weighted", zero_division=0))
    weighted_r = float(recall_score(y, y_pred, average="weighted", zero_division=0))
    weighted_f1 = float(f1_score(y, y_pred, average="weighted", zero_division=0))

    accuracy = float(accuracy_score(y, y_pred))

    # Macro-F1 strictly on classes with non-zero support in Capture-34-1 (classes 0, 1, 2, 3)
    present_classes = sorted(np.unique(y))
    present_macro_f1 = float(
        f1_score(y, y_pred, labels=present_classes, average="macro", zero_division=0)
    )

    # Per-class metrics
    class_precisions = precision_score(y, y_pred, labels=TARGET_CLASSES, average=None, zero_division=0)
    class_recalls = recall_score(y, y_pred, labels=TARGET_CLASSES, average=None, zero_division=0)
    class_f1s = f1_score(y, y_pred, labels=TARGET_CLASSES, average=None, zero_division=0)

    # Confusion matrix (5x5)
    cm = confusion_matrix(y, y_pred, labels=TARGET_CLASSES)

    # Benign False Positive Rate (FPR): Benign (class 0) predicted as any attack (classes 1, 2, 3, 4)
    # cm[0, 0] is True Benign. cm[0, 1:] are Benign false alarms.
    total_benign = int(cm[0, :].sum())
    benign_false_alarms = int(cm[0, 1:].sum())
    benign_fpr = float(benign_false_alarms / total_benign) if total_benign > 0 else 0.0

    # PR-AUC per class
    pr_auc_scores: Dict[str, Optional[float]] = {}
    if probs is not None:
        y_bin = label_binarize(y, classes=TARGET_CLASSES)
        for idx, cls_id in enumerate(TARGET_CLASSES):
            cls_name = CLASS_TO_NAME[cls_id]
            if y_bin[:, idx].sum() > 0:
                ap = float(average_precision_score(y_bin[:, idx], probs[:, idx]))
                pr_auc_scores[cls_name] = round(ap, 4)
            else:
                pr_auc_scores[cls_name] = None
    else:
        for cls_id in TARGET_CLASSES:
            pr_auc_scores[CLASS_TO_NAME[cls_id]] = None

    # Generalisation Gap: Level 2 Macro-F1 minus Level 1 Grouped CV Macro-F1
    level_1_macro_f1 = None
    if metadata and "overall_macro_f1" in metadata:
        level_1_macro_f1 = float(metadata["overall_macro_f1"])
    generalisation_gap = (
        round(macro_f1 - level_1_macro_f1, 4) if level_1_macro_f1 is not None else None
    )

    per_class_dict = {}
    for idx, cls_id in enumerate(TARGET_CLASSES):
        cls_name = CLASS_TO_NAME[cls_id]
        support_cnt = int((y == cls_id).sum())
        per_class_dict[cls_name] = {
            "precision": round(float(class_precisions[idx]), 4),
            "recall": round(float(class_recalls[idx]), 4),
            "f1": round(float(class_f1s[idx]), 4),
            "support": support_cnt,
            "pr_auc": pr_auc_scores.get(cls_name),
        }

    return {
        "model_name": name,
        "sample_count": len(X),
        "accuracy": round(accuracy, 4),
        "macro_f1_5class": round(macro_f1, 4),
        "macro_f1_present": round(present_macro_f1, 4),
        "macro_precision": round(macro_p, 4),
        "macro_recall": round(macro_r, 4),
        "micro_f1": round(micro_f1, 4),
        "weighted_f1": round(weighted_f1, 4),
        "benign_fpr": round(benign_fpr, 5),
        "benign_false_alarms": benign_false_alarms,
        "benign_total": total_benign,
        "latency_us_flow": round(latency_us_flow, 2),
        "throughput_fps": round(throughput_fps, 1),
        "level_1_cv_macro_f1": level_1_macro_f1,
        "generalisation_gap": generalisation_gap,
        "confusion_matrix": cm.tolist(),
        "per_class": per_class_dict,
        "predictions": y_pred,
        "probabilities": probs,
    }


def plot_confusion_matrices(
    results: List[Dict[str, Any]],
    output_png: Path,
) -> None:
    """Plot and save multi-class confusion matrices for evaluated models.

    Args:
        results: List of model evaluation dictionaries.
        output_png: Path to save confusion matrix image.
    """
    n_models = len(results)
    fig, axes = plt.subplots(1, n_models, figsize=(6.5 * n_models, 5.5), dpi=150)
    if n_models == 1:
        axes = [axes]

    display_labels = [CLASS_TO_NAME[c] for c in TARGET_CLASSES]

    for ax, res in zip(axes, results):
        cm = np.array(res["confusion_matrix"])
        disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=display_labels)
        disp.plot(
            ax=ax,
            cmap="Blues",
            values_format="d",
            colorbar=False,
        )
        ax.set_title(
            f"{res['model_name']}\nAccuracy: {res['accuracy']*100:.2f}% | Macro-F1: {res['macro_f1_5class']:.4f}",
            fontsize=11,
            fontweight="bold",
            pad=10,
        )
        ax.set_xticklabels(display_labels, rotation=35, ha="right", fontsize=9)
        ax.set_yticklabels(display_labels, fontsize=9)
        ax.set_xlabel("Predicted Class", fontsize=10, fontweight="semibold")
        ax.set_ylabel("True Class", fontsize=10, fontweight="semibold")

    plt.tight_layout()
    output_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_png, bbox_inches="tight")
    plt.close()
    logger.info("Saved confusion matrix visualization to: %s", output_png)


def generate_evaluation_csv(results: List[Dict[str, Any]], output_csv: Path) -> None:
    """Export machine-readable evaluation metrics to CSV.

    Args:
        results: List of evaluation result dictionaries.
        output_csv: Path to destination CSV.
    """
    rows = []
    for res in results:
        row = {
            "model_name": res["model_name"],
            "test_scenario": "CTU-IoT-Malware-Capture-34-1",
            "samples_count": res["sample_count"],
            "accuracy": res["accuracy"],
            "macro_f1_5class": res["macro_f1_5class"],
            "macro_f1_present": res["macro_f1_present"],
            "macro_precision": res["macro_precision"],
            "macro_recall": res["macro_recall"],
            "micro_f1": res["micro_f1"],
            "weighted_f1": res["weighted_f1"],
            "benign_fpr": res["benign_fpr"],
            "benign_false_alarms": res["benign_false_alarms"],
            "benign_total": res["benign_total"],
            "latency_us_flow": res["latency_us_flow"],
            "throughput_fps": res["throughput_fps"],
            "level_1_cv_macro_f1": res["level_1_cv_macro_f1"],
            "generalisation_gap": res["generalisation_gap"],
        }
        for cls_name, pstats in res["per_class"].items():
            row[f"recall_{cls_name}"] = pstats["recall"]
            row[f"precision_{cls_name}"] = pstats["precision"]
            row[f"f1_{cls_name}"] = pstats["f1"]
            row[f"pr_auc_{cls_name}"] = pstats["pr_auc"]
        rows.append(row)

    df_out = pd.DataFrame(rows)
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    df_out.to_csv(output_csv, index=False)
    logger.info("Saved evaluation summary CSV to: %s", output_csv)


def generate_evaluation_markdown(
    results: List[Dict[str, Any]],
    output_md: Path,
) -> None:
    """Generate comprehensive scientific markdown report evaluating held-out generalization and H1.

    Args:
        results: List of evaluation dictionaries.
        output_md: Path to destination markdown file.
    """
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rf_res = next((r for r in results if "Random Forest" in r["model_name"]), results[0])

    h1_target = 0.85
    h1_actual = rf_res["macro_f1_5class"]
    h1_actual_present = rf_res["macro_f1_present"]
    h1_passed = bool(h1_actual >= h1_target)

    md_lines = [
        "# Level 2 Held-Out Scenario Evaluation Report (Step 16)",
        "",
        f"**Generated:** {now}  ",
        "**Governing Standards:** Group 03 Research Proposal (Sections 1.3, 2.4, 3.4; Table 9; Hypothesis H1; RQ1, RQ2)  ",
        "**Evaluated Dataset:** `data/processed/heldout/held_out_test.parquet`  ",
        f"**Held-out scenario:** `CTU-IoT-Malware-Capture-34-1` (Mirai, {rf_res['sample_count']:,} flows)  ",
        "**Use of this scenario:** used only here and in the Step 17 final check, after all choices were made from training data (proposal 3.4). It was first opened in November 2026 for the v1 model (19 features); this model (D-051) was not tuned on it, but its score is reported as measured after the scenario had been seen once. Raw models, top class, no thresholds.  ",
        "",
        "---",
        "",
        "## 1. Summary and Hypothesis H1",
        "",
        "> **Hypothesis H1 (proposal Section 1.5):** *\"If the IoT-23 flow features are mapped carefully and the Random Forest is trained in a scenario-aware way, then the model will reach a macro-F1 score of at least 0.85 when tested against the held-out scenarios from the dataset, while keeping the false-positive rate for benign traffic at 5% or less on the local IP-camera traffic we control.\"*",
        "",
        "| H1 part | Target | Measured (Random Forest) | Result |",
        "| :--- | :---: | :---: | :--- |",
        f"| Macro-F1 on the held-out scenario (5 classes) | >= 0.85 | **{rf_res['macro_f1_5class']:.4f}** (classes present: {rf_res['macro_f1_present']:.4f}) | **{'met' if h1_passed else 'not met'}** |",
        "| Benign FPR on **local IP-camera traffic** | <= 5% | not measured in this step | measured in the lab (Steps 20 and 35) |",
        "",
        f"For information only (not part of H1): IoT-23 benign flows in 34-1 predicted as an attack = **{rf_res['benign_fpr']*100:.3f}%** ({rf_res['benign_false_alarms']:,} / {rf_res['benign_total']:,}). The model inference time is {rf_res['latency_us_flow']} µs per flow on the development PC; this is not the end-to-end latency in Table 9 (median < 2 s, p95 < 5 s), which is measured in Step 37.",
        "",
        "### Why the macro-F1 is below the target",
        "1. 34-1 has **no Malware_Download flows**. Any Malware_Download prediction is then a false positive, so this class gets F1 = 0 and the 5-class macro-F1 cannot be higher than 0.80. The score over the classes that are present is also reported.",
        "2. Even over the present classes the score is below 0.85. Weak classes (F1 < 0.60): " + (", ".join(f"`{c}` (F1 {rf_res['per_class'][c]['f1']:.2f}, precision {rf_res['per_class'][c]['precision']:.2f}, recall {rf_res['per_class'][c]['recall']:.2f})" for c in CLASS_NAMES if rf_res['per_class'][c]['support'] > 0 and rf_res['per_class'][c]['f1'] < 0.60) or "none") + ".",
        "3. The proposal (Section 1.5) names the likely reasons: domain shift between scenarios, feature mismatch, or too few examples in some classes. The per-class table and the confusion matrix below show where the errors are.",
        "4. No label, split or test file was changed after seeing these results. The D-051 changes (window features, trusted-label flag) were decided from the training scenarios only.",
        "",
        "---",
        "",
        "## 2. Multi-Model Performance Comparison Matrix",
        "",
        "| Evaluation Metric | Random Forest (Bagging) | Logistic Regression (Linear) | HistGradientBoosting (Boosting) | Target / Ideal |",
        "| :--- | :---: | :---: | :---: | :--- |",
    ]

    for label, key, fmt in [
        ("Macro-F1 (All 5 Target Classes)", "macro_f1_5class", ".4f"),
        ("Macro-F1 (4 Classes Present)", "macro_f1_present", ".4f"),
        ("Overall Accuracy", "accuracy", ".2f"),
        ("Weighted F1-Score", "weighted_f1", ".4f"),
        ("Macro Precision", "macro_precision", ".4f"),
        ("Macro Recall", "macro_recall", ".4f"),
        ("Benign FPR (Capture-34-1)", "benign_fpr", ".3f"),
        ("Inference Latency per Flow", "latency_us_flow", " µs"),
        ("Inference Throughput", "throughput_fps", " flows/s"),
        ("Level 1 Grouped CV Macro-F1", "level_1_cv_macro_f1", ".4f"),
        ("Generalisation Gap (L2 - L1)", "generalisation_gap", "+.4f"),
    ]:
        vals = []
        for r in results:
            val = r[key]
            if val is None:
                vals.append("N/A")
            elif "µs" in fmt:
                vals.append(f"{val:.2f} µs")
            elif "flows/s" in fmt:
                vals.append(f"{val:,.0f} flows/s")
            elif key in ("accuracy", "benign_fpr"):
                vals.append(f"{val*100:{fmt}}%")
            elif "+" in fmt:
                vals.append(f"{val:{fmt}}")
            else:
                vals.append(f"{val:{fmt}}")
        md_lines.append(f"| **{label}** | {vals[0]} | {vals[1]} | {vals[2]} | Benchmark |")

    md_lines.extend([
        "",
        "---",
        "",
        "## 3. Per-Class Detailed Performance (Random Forest Primary Prototype)",
        "",
        "| Class Name | Target Class ID | Support (Flows) | Precision | Recall | F1-Score | PR-AUC | Primary Flow Pattern |",
        "| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |",
    ])

    for cls_id in TARGET_CLASSES:
        cname = CLASS_TO_NAME[cls_id]
        pdata = rf_res["per_class"][cname]
        pr_str = f"{pdata['pr_auc']:.4f}" if pdata["pr_auc"] is not None else "N/A (0 Support)"
        pattern_desc = {
            "Benign": "DNS queries, NTP sync, legitimate IoT chatter",
            "DDoS_DoS": "High-rate UDP/TCP flooding (Mirai attack engine)",
            "PortScan": "Reconnaissance SYN sweeps across ports",
            "CnC": "Periodic botnet beaconing & telemetry",
            "Malware_Download": "Payload staging & binary fetches (Absent in 34-1)",
        }[cname]
        md_lines.append(
            f"| **`{cname}`** | {cls_id} | {pdata['support']:,} | {pdata['precision']:.4f} | "
            f"{pdata['recall']:.4f} | {pdata['f1']:.4f} | {pr_str} | {pattern_desc} |"
        )

    md_lines.extend([
        "",
        "---",
        "",
        "## 4. Multi-Class Confusion Matrix (Random Forest)",
        "",
        "```",
        f"Total Held-Out Flows: {rf_res['sample_count']:,} (Scenario: CTU-IoT-Malware-Capture-34-1)",
        "",
        "True \\ Pred         Benign    DDoS_DoS    PortScan         CnC    Malware_Download    Total",
        "------------------------------------------------------------------------------------------",
    ])

    cm = rf_res["confusion_matrix"]
    for i, row in enumerate(cm):
        cname = CLASS_TO_NAME[i]
        total_row = sum(row)
        md_lines.append(
            f"{cname:<16} {row[0]:>8} {row[1]:>11} {row[2]:>11} {row[3]:>11} {row[4]:>19} {total_row:>8}"
        )
    md_lines.extend([
        "------------------------------------------------------------------------------------------",
        "",
        "```",
        "",
        "Confusion matrix visualization saved to: `reports/experiments/confusion_matrix_heldout.png`.",
        "",
        "---",
        "",
        "## 5. Level 1 (grouped CV) compared with Level 2 (held-out scenario)",
        "",
        f"- Level 1 out-of-fold macro-F1 (22 training scenarios): `{rf_res['level_1_cv_macro_f1']:.4f}`." if rf_res.get('level_1_cv_macro_f1') is not None else "- Level 1 macro-F1: not available.",
        f"- Level 2 macro-F1 on `CTU-IoT-Malware-Capture-34-1`: `{rf_res['macro_f1_5class']:.4f}`.",
        "- One held-out scenario is a small test. A score on one scenario does not show how the model works on other scenarios or on camera traffic.",
        "",
        "---",
        "",
        "## 6. Next step",
        "",
        "Step 17 checks the probability calibration and chooses the alert and block thresholds. It uses only the grouped out-of-fold predictions of the training scenarios, never this held-out scenario.",
    ])

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text("\n".join(md_lines), encoding="utf-8")
    logger.info("Saved held-out evaluation markdown report to: %s", output_md)


def main() -> None:
    """Main CLI entry point for Step 16 evaluation."""
    parser = argparse.ArgumentParser(
        description="Step 16: Level 2 Held-out scenario evaluation on CTU-IoT-Malware-Capture-34-1."
    )
    parser.add_argument(
        "--held-out-path",
        type=Path,
        default=Path("data/processed/heldout/held_out_test.parquet"),
        help="Path to held-out test parquet.",
    )
    parser.add_argument(
        "--rf-model-path",
        type=Path,
        default=Path("ml_engine/models/rf_model.joblib"),
        help="Path to primary Random Forest model bundle.",
    )
    parser.add_argument(
        "--lr-model-path",
        type=Path,
        default=Path("ml_engine/models/lr_model.joblib"),
        help="Path to Logistic Regression baseline model.",
    )
    parser.add_argument(
        "--hgb-model-path",
        type=Path,
        default=Path("ml_engine/models/hgb_model.joblib"),
        help="Path to HistGradientBoosting baseline model.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("reports/experiments"),
        help="Directory to save evaluation reports and plots.",
    )
    args = parser.parse_args()

    logger.info("Starting Step 16 Held-Out Scenario Evaluation...")
    df, X, y = load_held_out_data(args.held_out_path)

    # Models to evaluate
    model_configs = [
        ("Random Forest (Bagging)", args.rf_model_path),
        ("Logistic Regression (Linear)", args.lr_model_path),
        ("HistGradientBoosting (Boosting)", args.hgb_model_path),
    ]

    results: List[Dict[str, Any]] = []
    for model_name, path in model_configs:
        if not path.exists():
            logger.warning("Model file %s does not exist; skipping %s", path, model_name)
            continue
        pipe, metadata = load_model_pipeline(path)
        res = evaluate_single_model(model_name, pipe, X, y, metadata)
        results.append(res)

    if not results:
        logger.error("No models could be evaluated.")
        sys.exit(1)

    # Generate deliverables
    output_dir = args.output_dir
    output_csv = output_dir / "evaluation_iot23.csv"
    output_md = output_dir / "evaluation_iot23.md"
    output_png = output_dir / "confusion_matrix_heldout.png"

    generate_evaluation_csv(results, output_csv)
    generate_evaluation_markdown(results, output_md)
    plot_confusion_matrices(results, output_png)

    logger.info("Step 16 evaluation complete! Deliverables generated in %s", output_dir)


if __name__ == "__main__":
    main()
