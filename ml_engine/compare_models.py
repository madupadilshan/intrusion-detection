#!/usr/bin/env python3
"""
IoT Intrusion Detection: Model Comparison Engine (Step 15)
==========================================================

Implements Group 03 Research Proposal Sections 1.3, 2.4, Table 9, and
STEP_BY_STEP_GUIDE.md Step 15.

Key Objectives:
  1. Compare Three Distinct Algorithmic Families:
     - Random Forest Classifier (Bagging Ensemble - Primary Prototype Model)
     - Linear Model (Logistic Regression with One-Hot Encoding & StandardScaler)
     - Gradient Boosting Model (HistGradientBoostingClassifier with OrdinalEncoder)
  2. Strict Scientific Fairness & Zero Leakage:
     - Evaluated on the exact same features (FEATURE_COLUMNS: 26 since D-051) and the same training rows (variant, D-051).
     - Evaluated on the exact same Level 1 5-fold StratifiedGroupKFold
       splits (random_state=42, groups=scenario_id) across all 1,384,070 flows.
     - Held-out scenario CTU-IoT-Malware-Capture-34-1 remains 100% sealed
       in data/processed/heldout/ (Checkpoint C4).
  3. Single Unified Comparison Matrix:
     - Macro-F1 score
     - Per-class recall (Benign, DDoS_DoS, PortScan, CnC, Malware_Download)
     - Benign False Positive Rate (FPR)
     - Training runtime (seconds)
     - Inference latency per flow (microseconds/flow) and throughput (flows/sec)
     - Model size on disk (MB)
     - Qualitative interpretability & prototype suitability
  4. Reporting:
     - Exports machine-readable CSV to reports/experiments/model_comparison.csv.
     - Generates audit-ready markdown report at reports/experiments/model_comparison.md.
"""

import sys
import os
import json
import time
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional

import yaml
import joblib
import numpy as np
import pandas as pd
import pyarrow.parquet as pq

from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler, OrdinalEncoder
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    accuracy_score,
)

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine.training_rows import VARIANT_FILE, load_training_frame
from ml_engine.features import (
    FEATURE_COLUMNS,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)
from ml_engine.train import build_rf_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("compare_models")

# Fixed Paths and Constants
DEFAULT_DATA_PATH = PROJECT_ROOT / "data" / "processed" / "train_features.parquet"
DEFAULT_EXPERIMENTS_DIR = PROJECT_ROOT / "reports" / "experiments"
DEFAULT_MODELS_DIR = PROJECT_ROOT / "ml_engine" / "models"
RF_MODEL_PATH = DEFAULT_MODELS_DIR / "rf_model.joblib"
LR_MODEL_PATH = DEFAULT_MODELS_DIR / "lr_model.joblib"
HGB_MODEL_PATH = DEFAULT_MODELS_DIR / "hgb_model.joblib"
SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.yaml"

CLASS_NAMES = ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]
CLASS_INDICES = [0, 1, 2, 3, 4]


def load_settings() -> Dict[str, Any]:
    """Load settings from config/settings.yaml with fallback defaults."""
    if SETTINGS_PATH.exists():
        try:
            with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
                cfg = yaml.safe_load(f)
                return cfg or {}
        except Exception as e:
            logger.warning(f"Could not load settings: {e}. Using defaults.")
    return {}


def build_linear_pipeline(random_seed: int = 42, max_iter: int = 200, n_jobs: int = -1) -> Pipeline:
    """
    Build Linear Classifier Pipeline with OneHotEncoder and StandardScaler.
    Scaling is applied only to the linear baseline per Proposal Section 2.4.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OneHotEncoder(
                    handle_unknown="ignore",
                    min_frequency=50,
                    sparse_output=True,
                ),
                CATEGORICAL_FEATURES,
            ),
            (
                "num",
                StandardScaler(),
                NUMERICAL_FEATURES,
            ),
        ]
    )
    pipeline = Pipeline(
        steps=[
            ("pre", preprocessor),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=max_iter,
                    solver="lbfgs",
                    random_state=random_seed,
                    n_jobs=n_jobs,
                ),
            ),
        ]
    )
    return pipeline


def build_hgb_pipeline(random_seed: int = 42, max_iter: int = 100) -> Pipeline:
    """
    Build Gradient Boosting Pipeline with HistGradientBoostingClassifier.
    Uses OrdinalEncoder for categoricals.
    """
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                    min_frequency=50,
                ),
                CATEGORICAL_FEATURES,
            ),
        ],
        remainder="passthrough",
    )
    pipeline = Pipeline(
        steps=[
            ("pre", preprocessor),
            (
                "model",
                HistGradientBoostingClassifier(
                    class_weight="balanced",
                    max_iter=max_iter,
                    early_stopping=True,
                    validation_fraction=0.1,
                    n_iter_no_change=10,
                    random_state=random_seed,
                ),
            ),
        ]
    )
    return pipeline


def benchmark_latency(pipeline: Pipeline, X_bench: pd.DataFrame, num_samples: int = 10000) -> Tuple[float, float]:
    """Measure inference latency per flow in microseconds and throughput."""
    sample = X_bench.iloc[:num_samples].copy()
    # Warmup
    _ = pipeline.predict(sample.iloc[:50])

    t0 = time.perf_counter()
    _ = pipeline.predict(sample)
    t1 = time.perf_counter()

    total_time = t1 - t0
    latency_us = (total_time / len(sample)) * 1_000_000
    throughput_fps = len(sample) / total_time
    return latency_us, throughput_fps


def evaluate_pipeline_grouped_cv(
    name: str,
    pipeline_builder_fn,
    X: pd.DataFrame,
    y: np.ndarray,
    groups: np.ndarray,
    cv_splits: int,
    random_seed: int,
) -> Tuple[Dict[str, Any], np.ndarray]:
    """
    Evaluate a pipeline across the 5-fold StratifiedGroupKFold splits.
    """
    logger.info("=" * 70)
    logger.info(f"EVALUATING MODEL: {name} ON 5-FOLD GROUPED CV...")
    logger.info("=" * 70)

    sgkf = StratifiedGroupKFold(n_splits=cv_splits, shuffle=True, random_state=random_seed)

    oof_preds = np.zeros(len(y), dtype=np.int8)
    fold_macro_f1s = []
    fold_accuracies = []
    fold_times = []

    for fold, (train_idx, val_idx) in enumerate(sgkf.split(X, y, groups=groups), 1):
        t0 = time.time()
        X_tr, y_tr = X.iloc[train_idx], y[train_idx]
        X_va, y_va = X.iloc[val_idx], y[val_idx]

        pipe = pipeline_builder_fn(random_seed=random_seed + fold)
        pipe.fit(X_tr, y_tr)
        val_preds = pipe.predict(X_va)
        oof_preds[val_idx] = val_preds
        t1 = time.time()

        f1_m = f1_score(y_va, val_preds, average="macro", zero_division=0)
        acc = accuracy_score(y_va, val_preds)

        fold_macro_f1s.append(f1_m)
        fold_accuracies.append(acc)
        fold_times.append(t1 - t0)

        logger.info(
            f"[{name}] Fold {fold}/{cv_splits} [{t1 - t0:.1f}s]: "
            f"Macro-F1={f1_m:.4f}, Accuracy={acc:.4f}"
        )

    # Compute overall out-of-fold metrics
    overall_macro_f1 = f1_score(y, oof_preds, average="macro", zero_division=0)
    overall_weighted_f1 = f1_score(y, oof_preds, average="weighted", zero_division=0)
    overall_accuracy = accuracy_score(y, oof_preds)

    recalls = recall_score(y, oof_preds, labels=CLASS_INDICES, average=None, zero_division=0)
    precisions = precision_score(y, oof_preds, labels=CLASS_INDICES, average=None, zero_division=0)
    f1s = f1_score(y, oof_preds, labels=CLASS_INDICES, average=None, zero_division=0)

    benign_total = (y == 0).sum()
    benign_fp = ((y == 0) & (oof_preds != 0)).sum()
    benign_fpr = (benign_fp / benign_total) if benign_total > 0 else 0.0

    total_cv_time = sum(fold_times)

    metrics = {
        "model_name": name,
        "overall_macro_f1": overall_macro_f1,
        "mean_fold_macro_f1": float(np.mean(fold_macro_f1s)),
        "std_fold_macro_f1": float(np.std(fold_macro_f1s)),
        "overall_weighted_f1": overall_weighted_f1,
        "overall_accuracy": overall_accuracy,
        "benign_fpr": benign_fpr,
        "benign_fp": int(benign_fp),
        "benign_total": int(benign_total),
        "total_cv_time_sec": total_cv_time,
    }
    for idx, cname in enumerate(CLASS_NAMES):
        metrics[f"recall_{cname}"] = float(recalls[idx])
        metrics[f"precision_{cname}"] = float(precisions[idx])
        metrics[f"f1_{cname}"] = float(f1s[idx])

    logger.info(
        f"[{name}] Completed: OOF Macro-F1 = {overall_macro_f1:.4f} "
        f"(Fold Mean: {metrics['mean_fold_macro_f1']:.4f} ± {metrics['std_fold_macro_f1']:.4f}), "
        f"Benign FPR = {benign_fpr*100:.2f}%, Total CV Time = {total_cv_time:.1f}s"
    )
    return metrics, oof_preds



def _ranking_text(df_results: pd.DataFrame) -> str:
    """Plain, data-driven ranking of the models by out-of-fold macro-F1."""
    order = df_results.sort_values("overall_macro_f1", ascending=False)
    parts = [f"{r.model_name} {r.overall_macro_f1:.4f}" for r in order.itertuples()]
    best = order.iloc[0]
    lines = [
        "- Out-of-fold macro-F1, highest first: " + "; ".join(parts) + ".",
        f"- Highest out-of-fold macro-F1: **{best.model_name}**.",
        "- Each validation fold contains only scenarios that the model never saw, so these scores show "
        "how well a model transfers to new scenarios.",
    ]
    return "\n".join(lines)

def export_model_comparison_report(
    report_path: Path,
    csv_path: Path,
    results: List[Dict[str, Any]],
    elapsed_total_sec: float,
    n_rows: int = 0,
    n_scenarios: int = 0,
    variant: str = "",
):
    """Generate Markdown and CSV comparison deliverables."""
    df_results = pd.DataFrame(results)
    df_results.to_csv(csv_path, index=False)
    logger.info(f"Saved machine-readable comparison table to {csv_path}")

    # Build Markdown
    content = f"""# Machine Learning Model Comparison Report (Step 15)

**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Execution Runtime:** {elapsed_total_sec:.2f} seconds ({elapsed_total_sec / 60.0:.2f} minutes)  
**Governing Standard:** Group 03 Research Proposal (Sections 1.3, 2.4, Table 9)  
**Evaluated Data:** `data/processed/train_features.parquet` ({n_rows:,} flows across {n_scenarios} scenarios; training variant {variant})  
**Cross-Validation:** 5-Fold `StratifiedGroupKFold(random_state=42, groups=scenario_id)`  

---

## 1. Executive Summary & Model Selection Justification

This report presents the empirical comparison of three distinct machine learning algorithmic families for real-time IP-camera IoT network intrusion detection:

1. **Random Forest Classifier (Ensemble - Bagging):** Main prototype model.
2. **Linear Baseline Classifier (Logistic Regression):** Classical linear model with One-Hot categorical encoding and feature standardisation (`StandardScaler`).
3. **Gradient Boosting Classifier (`HistGradientBoostingClassifier`):** State-of-the-art sequential gradient-boosted decision trees.

### Main finding (Level 1, grouped out-of-fold):
{_ranking_text(df_results)}

**Model choice:** Random Forest stays the main model of the prototype. The proposal (Section 2.4) keeps it as the main model "because it is easier to look inside its decisions", and asks for this comparison to show whether it gives a good balance between accuracy and speed (Section 1.3). The numbers below are reported as measured, including where another model scores higher.

---

## 2. Comprehensive Model Comparison Matrix

| Evaluation Metric | Random Forest (Bagging) | Logistic Regression (Linear) | HistGradientBoosting (Boosting) | Target / Benchmark |
| :--- | :---: | :---: | :---: | :--- |
| **Out-of-Fold Macro-F1** | **{df_results.loc[df_results['model_name']=='Random Forest', 'overall_macro_f1'].values[0]:.4f}** | {df_results.loc[df_results['model_name']=='Logistic Regression', 'overall_macro_f1'].values[0]:.4f} | **{df_results.loc[df_results['model_name']=='HistGradientBoosting', 'overall_macro_f1'].values[0]:.4f}** | reported (no target) |
| **Fold Mean Macro-F1** | **{df_results.loc[df_results['model_name']=='Random Forest', 'mean_fold_macro_f1'].values[0]:.4f} ± {df_results.loc[df_results['model_name']=='Random Forest', 'std_fold_macro_f1'].values[0]:.4f}** | {df_results.loc[df_results['model_name']=='Logistic Regression', 'mean_fold_macro_f1'].values[0]:.4f} ± {df_results.loc[df_results['model_name']=='Logistic Regression', 'std_fold_macro_f1'].values[0]:.4f} | {df_results.loc[df_results['model_name']=='HistGradientBoosting', 'mean_fold_macro_f1'].values[0]:.4f} ± {df_results.loc[df_results['model_name']=='HistGradientBoosting', 'std_fold_macro_f1'].values[0]:.4f} | reported |
| **Overall Accuracy** | {df_results.loc[df_results['model_name']=='Random Forest', 'overall_accuracy'].values[0]*100:.2f}% | {df_results.loc[df_results['model_name']=='Logistic Regression', 'overall_accuracy'].values[0]*100:.2f}% | {df_results.loc[df_results['model_name']=='HistGradientBoosting', 'overall_accuracy'].values[0]*100:.2f}% | Secondary metric |
| **Recall: `Benign`** | {df_results.loc[df_results['model_name']=='Random Forest', 'recall_Benign'].values[0]*100:.2f}% | {df_results.loc[df_results['model_name']=='Logistic Regression', 'recall_Benign'].values[0]*100:.2f}% | {df_results.loc[df_results['model_name']=='HistGradientBoosting', 'recall_Benign'].values[0]*100:.2f}% | Legitimate flow preservation |
| **Recall: `DDoS_DoS`** | {df_results.loc[df_results['model_name']=='Random Forest', 'recall_DDoS_DoS'].values[0]*100:.2f}% | {df_results.loc[df_results['model_name']=='Logistic Regression', 'recall_DDoS_DoS'].values[0]*100:.2f}% | {df_results.loc[df_results['model_name']=='HistGradientBoosting', 'recall_DDoS_DoS'].values[0]*100:.2f}% | High-rate flood defense |
| **Recall: `PortScan`** | {df_results.loc[df_results['model_name']=='Random Forest', 'recall_PortScan'].values[0]*100:.2f}% | {df_results.loc[df_results['model_name']=='Logistic Regression', 'recall_PortScan'].values[0]*100:.2f}% | {df_results.loc[df_results['model_name']=='HistGradientBoosting', 'recall_PortScan'].values[0]*100:.2f}% | Reconnaissance detection |
| **Recall: `CnC` (Minority)** | **{df_results.loc[df_results['model_name']=='Random Forest', 'recall_CnC'].values[0]*100:.2f}%** | {df_results.loc[df_results['model_name']=='Logistic Regression', 'recall_CnC'].values[0]*100:.2f}% | {df_results.loc[df_results['model_name']=='HistGradientBoosting', 'recall_CnC'].values[0]*100:.2f}% | Botnet beacon detection |
| **Recall: `Malware_Download`** | **{df_results.loc[df_results['model_name']=='Random Forest', 'recall_Malware_Download'].values[0]*100:.2f}%** | {df_results.loc[df_results['model_name']=='Logistic Regression', 'recall_Malware_Download'].values[0]*100:.2f}% | {df_results.loc[df_results['model_name']=='HistGradientBoosting', 'recall_Malware_Download'].values[0]*100:.2f}% | Payload staging tracking |
| **Benign FPR (IoT-23)** | {df_results.loc[df_results['model_name']=='Random Forest', 'benign_fpr'].values[0]*100:.2f}% | {df_results.loc[df_results['model_name']=='Logistic Regression', 'benign_fpr'].values[0]*100:.2f}% | {df_results.loc[df_results['model_name']=='HistGradientBoosting', 'benign_fpr'].values[0]*100:.2f}% | IoT-23 benign; H1 uses local camera traffic |
| **Inference Latency** | **{df_results.loc[df_results['model_name']=='Random Forest', 'latency_us'].values[0]:.2f} µs/flow** | {df_results.loc[df_results['model_name']=='Logistic Regression', 'latency_us'].values[0]:.2f} µs/flow | {df_results.loc[df_results['model_name']=='HistGradientBoosting', 'latency_us'].values[0]:.2f} µs/flow | model step only (end-to-end target: Table 9) |
| **Inference Throughput** | **{df_results.loc[df_results['model_name']=='Random Forest', 'throughput_fps'].values[0]:,.0f} flows/s** | {df_results.loc[df_results['model_name']=='Logistic Regression', 'throughput_fps'].values[0]:,.0f} flows/s | {df_results.loc[df_results['model_name']=='HistGradientBoosting', 'throughput_fps'].values[0]:,.0f} flows/s | Higher is better |
| **Final Fit Time (all rows)** | {df_results.loc[df_results['model_name']=='Random Forest', 'fit_time_sec'].values[0]:.1f} s | {df_results.loc[df_results['model_name']=='Logistic Regression', 'fit_time_sec'].values[0]:.1f} s | **{df_results.loc[df_results['model_name']=='HistGradientBoosting', 'fit_time_sec'].values[0]:.1f} s** | Computational footprint |
| **5-Fold CV Time** | {df_results.loc[df_results['model_name']=='Random Forest', 'total_cv_time_sec'].values[0]:.1f} s | {df_results.loc[df_results['model_name']=='Logistic Regression', 'total_cv_time_sec'].values[0]:.1f} s | **{df_results.loc[df_results['model_name']=='HistGradientBoosting', 'total_cv_time_sec'].values[0]:.1f} s** | Evaluation efficiency |
| **Model Size on Disk** | {df_results.loc[df_results['model_name']=='Random Forest', 'model_size_mb'].values[0]:.2f} MB | **{df_results.loc[df_results['model_name']=='Logistic Regression', 'model_size_mb'].values[0]:.2f} MB** | **{df_results.loc[df_results['model_name']=='HistGradientBoosting', 'model_size_mb'].values[0]:.2f} MB** | Embedded edge storage |
| **Interpretability / Audit** | Trees and decision paths can be inspected | Linear weights | Many boosted trees; harder to inspect | Proposal 2.4 |

---

## 3. Notes on each model

- **Random Forest:** main model (proposal 2.4). Its trees can be inspected (Step 17 shows example decision paths). Model size {df_results.loc[df_results['model_name']=='Random Forest', 'model_size_mb'].values[0]:.2f} MB.
- **Logistic Regression:** linear baseline with one-hot encoding and scaling (scaling only for this model, proposal 3.3). Model size {df_results.loc[df_results['model_name']=='Logistic Regression', 'model_size_mb'].values[0]:.2f} MB.
- **HistGradientBoosting:** gradient-boosting comparison model (proposal 1.3). Model size {df_results.loc[df_results['model_name']=='HistGradientBoosting', 'model_size_mb'].values[0]:.2f} MB.
- Inference times are for the model step only on the development PC. The proposal's latency target (Table 9) is end-to-end and is measured in Step 37.

## 4. Next step

All three models are tested once on the held-out scenario `CTU-IoT-Malware-Capture-34-1` in Step 16.
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Saved comprehensive comparison report to {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Compare ML Models (Step 15)")
    parser.add_argument("--data-path", type=Path, default=DEFAULT_DATA_PATH)
    parser.add_argument("--experiments-dir", type=Path, default=DEFAULT_EXPERIMENTS_DIR)
    parser.add_argument("--models-dir", type=Path, default=DEFAULT_MODELS_DIR)
    parser.add_argument("--cv-splits", type=int, default=5)
    parser.add_argument("--rf-n-jobs", type=int, default=-1)
    args = parser.parse_args()

    start_time = time.time()
    args.experiments_dir.mkdir(parents=True, exist_ok=True)
    args.models_dir.mkdir(parents=True, exist_ok=True)

    settings = load_settings()
    random_seed = int(settings.get("model", {}).get("random_seed", 42))

    logger.info("=" * 70)
    logger.info("STARTING STEP 15: MACHINE LEARNING MODEL BENCHMARK & COMPARISON")
    logger.info(f"Training Parquet: {args.data_path}")
    logger.info(f"Random Seed: {random_seed}, CV Splits: {args.cv_splits}")
    logger.info("=" * 70)

    # 1. Load Training Dataset
    if not args.data_path.exists():
        logger.error(f"Training dataset not found at {args.data_path}!")
        sys.exit(1)

    t0_read = time.time()
    df = load_training_frame(args.data_path)  # same rows as Step 14 (variant, D-051)
    t1_read = time.time()
    logger.info(f"Loaded {len(df):,} flows in {t1_read - t0_read:.2f}s.")

    for c in CATEGORICAL_FEATURES:
        df[c] = df[c].astype("category")

    X = df[FEATURE_COLUMNS]
    y = df["label_idx"].values.astype(np.int8)
    groups = df["scenario_id"].values.astype(str)

    results: List[Dict[str, Any]] = []

    # 2. Retrieve / Load Random Forest Baseline (Step 14)
    if RF_MODEL_PATH.exists():
        logger.info(f"Loading existing Random Forest model bundle from {RF_MODEL_PATH}...")
        rf_bundle = joblib.load(RF_MODEL_PATH)
        rf_pipeline = rf_bundle["pipeline"]
        rf_latency_us = rf_bundle["inference_latency_us"]
        rf_throughput_fps = rf_bundle["throughput_fps"]
        rf_model_size_mb = RF_MODEL_PATH.stat().st_size / (1024 * 1024)

        # Retrieve CV metrics from rf_cv_results.csv or bundle
        rf_cv_csv = args.experiments_dir / "rf_cv_results.csv"
        if rf_cv_csv.exists():
            df_rf_cv = pd.read_csv(rf_cv_csv)
            rf_total_cv_time = df_rf_cv["elapsed_seconds"].sum()
        else:
            rf_total_cv_time = float("nan")  # not recorded

        # Random Forest numbers come from its own grouped out-of-fold predictions (Step 14,
        # data/processed/rf_oof_predictions.npz), on exactly these rows. (Until 11 Nov 2026 the
        # accuracy, weighted F1, recalls and benign counts here were fixed numbers typed in from
        # an old run; they were not measured. Found in the requirement check of 11 Nov 2026.)
        oof_file = PROJECT_ROOT / "data" / "processed" / "rf_oof_predictions.npz"
        z = np.load(oof_file, allow_pickle=False)
        if len(z["y"]) != len(y) or not np.array_equal(z["y"].astype(np.int8), y):
            logger.error("rf_oof_predictions.npz does not line up with these rows; re-run Step 14 / select_variant.")
            sys.exit(1)
        rf_pred = z["oof_probs"].argmax(axis=1)
        rf_rec = recall_score(y, rf_pred, labels=CLASS_INDICES, average=None, zero_division=0)
        rf_prec = precision_score(y, rf_pred, labels=CLASS_INDICES, average=None, zero_division=0)
        rf_f1s = f1_score(y, rf_pred, labels=CLASS_INDICES, average=None, zero_division=0)
        benign_total = int((y == 0).sum())
        benign_fp = int(((y == 0) & (rf_pred != 0)).sum())
        rf_metrics = {
            "model_name": "Random Forest",
            "overall_macro_f1": float(f1_score(y, rf_pred, labels=CLASS_INDICES, average="macro", zero_division=0)),
            "mean_fold_macro_f1": rf_bundle["mean_fold_macro_f1"],
            "std_fold_macro_f1": rf_bundle["std_fold_macro_f1"],
            "overall_weighted_f1": float(f1_score(y, rf_pred, average="weighted", zero_division=0)),
            "overall_accuracy": float(accuracy_score(y, rf_pred)),
            "benign_fpr": benign_fp / benign_total if benign_total else 0.0,
            "benign_fp": benign_fp,
            "benign_total": benign_total,
            "total_cv_time_sec": rf_total_cv_time,
            "fit_time_sec": rf_bundle.get("fit_time_sec") or float("nan"),
            "latency_us": rf_latency_us,
            "throughput_fps": rf_throughput_fps,
            "model_size_mb": rf_model_size_mb,
        }
        for idx, cname in enumerate(CLASS_NAMES):
            rf_metrics[f"recall_{cname}"] = float(rf_rec[idx])
            rf_metrics[f"precision_{cname}"] = float(rf_prec[idx])
            rf_metrics[f"f1_{cname}"] = float(rf_f1s[idx])
        results.append(rf_metrics)
    else:
        logger.error(f"Random Forest model not found at {RF_MODEL_PATH}! Please complete Step 14 first.")
        sys.exit(1)

    # 3. Evaluate Linear Model (Logistic Regression)
    lr_metrics, lr_oof_preds = evaluate_pipeline_grouped_cv(
        name="Logistic Regression",
        pipeline_builder_fn=lambda random_seed: build_linear_pipeline(
            random_seed=random_seed, max_iter=200, n_jobs=args.rf_n_jobs
        ),
        X=X,
        y=y,
        groups=groups,
        cv_splits=args.cv_splits,
        random_seed=random_seed,
    )

    # Fit final Linear pipeline on all 1.38M flows
    logger.info(f"Fitting final Logistic Regression pipeline on all {len(y):,} flows...")
    t0_lr_fit = time.time()
    final_lr_pipeline = build_linear_pipeline(random_seed=random_seed, max_iter=200, n_jobs=args.rf_n_jobs)
    final_lr_pipeline.fit(X, y)
    t1_lr_fit = time.time()

    lr_latency_us, lr_throughput = benchmark_latency(final_lr_pipeline, X)
    joblib.dump(final_lr_pipeline, LR_MODEL_PATH, compress=3)
    lr_model_size_mb = LR_MODEL_PATH.stat().st_size / (1024 * 1024)

    lr_metrics["fit_time_sec"] = t1_lr_fit - t0_lr_fit
    lr_metrics["latency_us"] = lr_latency_us
    lr_metrics["throughput_fps"] = lr_throughput
    lr_metrics["model_size_mb"] = lr_model_size_mb
    results.append(lr_metrics)

    # 4. Evaluate Gradient Boosting Model (HistGradientBoostingClassifier)
    hgb_metrics, hgb_oof_preds = evaluate_pipeline_grouped_cv(
        name="HistGradientBoosting",
        pipeline_builder_fn=lambda random_seed: build_hgb_pipeline(
            random_seed=random_seed, max_iter=100
        ),
        X=X,
        y=y,
        groups=groups,
        cv_splits=args.cv_splits,
        random_seed=random_seed,
    )

    # Fit final HGB pipeline on all 1.38M flows
    logger.info(f"Fitting final HistGradientBoosting pipeline on all {len(y):,} flows...")
    t0_hgb_fit = time.time()
    final_hgb_pipeline = build_hgb_pipeline(random_seed=random_seed, max_iter=100)
    final_hgb_pipeline.fit(X, y)
    t1_hgb_fit = time.time()

    hgb_latency_us, hgb_throughput = benchmark_latency(final_hgb_pipeline, X)
    joblib.dump(final_hgb_pipeline, HGB_MODEL_PATH, compress=3)
    hgb_model_size_mb = HGB_MODEL_PATH.stat().st_size / (1024 * 1024)

    hgb_metrics["fit_time_sec"] = t1_hgb_fit - t0_hgb_fit
    hgb_metrics["latency_us"] = hgb_latency_us
    hgb_metrics["throughput_fps"] = hgb_throughput
    hgb_metrics["model_size_mb"] = hgb_model_size_mb
    results.append(hgb_metrics)

    # 5. Export Deliverables
    elapsed_total = time.time() - start_time
    csv_report_path = args.experiments_dir / "model_comparison.csv"
    md_report_path = args.experiments_dir / "model_comparison.md"
    export_model_comparison_report(
        report_path=md_report_path,
        csv_path=csv_report_path,
        results=results,
        elapsed_total_sec=elapsed_total,
        n_rows=len(y),
        n_scenarios=len(set(groups)),
        variant=(json.loads(VARIANT_FILE.read_text(encoding="utf-8")).get("chosen", "") if VARIANT_FILE.exists() else ""),
    )

    logger.info("=" * 70)
    logger.info("STEP 15 COMPLETE: MODEL COMPARISON DELIVERABLES EXPORTED SUCCESSFULLY")
    logger.info(f"Total Execution Time: {elapsed_total:.2f}s ({elapsed_total/60:.2f} minutes)")
    for r in results:
        logger.info(
            f"-> {r['model_name']:20s} | Macro-F1: {r['overall_macro_f1']:.4f} | "
            f"Latency: {r['latency_us']:.2f} µs | Size: {r['model_size_mb']:.2f} MB"
        )
    logger.info("=" * 70)


if __name__ == "__main__":
    main()

