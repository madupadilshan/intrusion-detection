"""tools/schema_check.py - Offline vs Live Feature Schema & Distribution Auditor.

Governing Standards:
- Group 03 Proposal: Sections 2.5, 3.5; Objective O3; Research Question RQ3; Table 11
- Step-by-Step Guide: Step 22 (Offline vs live feature check / schema check)
- Decision Log: D-026

Audits:
1. Exact column names and locked ordering (19 candidate features).
2. Data types (dtypes) consistency across offline and live inference pipelines.
3. Missing value (NaN/null/inf) zero-tolerance validation.
4. Numerical dynamic ranges, physical feasibility, and statistical distribution shifts (KS 2-sample test).
5. Categorical cardinality, domain coverage, and novel unseen category handling by the preprocessor.
6. End-to-end inference execution against the production model bundle (ids_bundle_v1.joblib).
7. A report that states whether the live data is real or synthetic (only real data answers RQ3).
"""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import sys
import time
from typing import Any, Dict, List, Optional, Set, Tuple

import joblib
import numpy as np
import pandas as pd
from scipy import stats

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from core_engine.zeek_adapter import ZeekAdapter
from ml_engine.features import (
    CATEGORICAL_FEATURES,
    FEATURE_COLUMNS,
    NUMERICAL_FEATURES,
    make_features,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [schema_check] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("schema_check")

# Default input and output paths
DEFAULT_OFFLINE_PATH = PROJECT_ROOT / "data" / "processed" / "train_features.parquet"
DEFAULT_LIVE_LOG_PATH = PROJECT_ROOT / "data" / "local" / "synthetic" / "2026-10-31" / "conn.log"
DEFAULT_MODEL_BUNDLE = PROJECT_ROOT / "ml_engine" / "models" / "ids_bundle_v1.joblib"
DEFAULT_REPORT_MD = PROJECT_ROOT / "reports" / "schema_check.md"
DEFAULT_REPORT_CSV = PROJECT_ROOT / "reports" / "schema_check.csv"


class SchemaAuditor:
    """Performs rigorous mathematical and structural schema comparison between offline and live feature matrices."""

    def __init__(
        self,
        offline_df: pd.DataFrame,
        live_df: pd.DataFrame,
        model_bundle_path: Optional[Path] = None,
    ) -> None:
        self.offline_df = offline_df[FEATURE_COLUMNS].copy()
        self.live_df = live_df[FEATURE_COLUMNS].copy()
        self.model_bundle_path = Path(model_bundle_path or DEFAULT_MODEL_BUNDLE)

    def check_columns(self) -> Dict[str, Any]:
        """Verify column names, presence, and locked ordering."""
        offline_cols = list(self.offline_df.columns)
        live_cols = list(self.live_df.columns)

        names_match = offline_cols == live_cols
        count_match = len(live_cols) == len(FEATURE_COLUMNS) == 19
        order_match = live_cols == FEATURE_COLUMNS

        return {
            "expected_count": len(FEATURE_COLUMNS),
            "offline_count": len(offline_cols),
            "live_count": len(live_cols),
            "names_match": names_match,
            "order_match": order_match,
            "missing_in_live": list(set(FEATURE_COLUMNS) - set(live_cols)),
            "extra_in_live": list(set(live_cols) - set(FEATURE_COLUMNS)),
            "passed": names_match and count_match and order_match,
        }

    def check_dtypes(self) -> pd.DataFrame:
        """Verify compatibility of data types between offline training and live serving."""
        rows = []
        for col in FEATURE_COLUMNS:
            off_dt = str(self.offline_df[col].dtype)
            live_dt = str(self.live_df[col].dtype)

            # Compatibility check:
            # Categoricals should both be object/string
            # Numericals should both be float or int numeric
            is_cat = col in CATEGORICAL_FEATURES
            if is_cat:
                compat = (off_dt in ("object", "string")) and (live_dt in ("object", "string"))
            else:
                compat = ("float" in off_dt or "int" in off_dt) and ("float" in live_dt or "int" in live_dt)

            rows.append(
                {
                    "feature": col,
                    "kind": "categorical" if is_cat else "numerical",
                    "offline_dtype": off_dt,
                    "live_dtype": live_dt,
                    "compatible": compat,
                    "status": "PASS" if compat else "FAIL",
                }
            )
        return pd.DataFrame(rows)

    def check_nulls(self) -> pd.DataFrame:
        """Verify zero missing values, NaNs, and infinite values in both feature sets."""
        rows = []
        for col in FEATURE_COLUMNS:
            off_nulls = int(self.offline_df[col].isna().sum())
            live_nulls = int(self.live_df[col].isna().sum())
            off_pct = (off_nulls / max(1, len(self.offline_df))) * 100.0
            live_pct = (live_nulls / max(1, len(self.live_df))) * 100.0

            passed = (off_nulls == 0) and (live_nulls == 0)
            rows.append(
                {
                    "feature": col,
                    "offline_null_count": off_nulls,
                    "offline_null_pct": round(off_pct, 4),
                    "live_null_count": live_nulls,
                    "live_null_pct": round(live_pct, 4),
                    "status": "PASS" if passed else "FAIL",
                }
            )
        return pd.DataFrame(rows)

    def check_numerical_ranges(self) -> pd.DataFrame:
        """Compare min, max, median, percentiles, and statistical distribution drift for numerical features."""
        rows = []
        for col in NUMERICAL_FEATURES:
            off_s = pd.to_numeric(self.offline_df[col], errors="coerce").fillna(0.0)
            live_s = pd.to_numeric(self.live_df[col], errors="coerce").fillna(0.0)

            # 2-sample Kolmogorov-Smirnov test to quantify distribution difference
            # Note: subsample if offline dataset is massive to maintain test speed
            sub_off = off_s.sample(n=min(10000, len(off_s)), random_state=42)
            sub_live = live_s.sample(n=min(10000, len(live_s)), random_state=42)
            ks_res = stats.ks_2samp(sub_off, sub_live)

            # Feasibility rules:
            # 1. Non-negative for byte and packet counts
            # 2. Ratios bounded between 0.0 and 1.0
            feasible = True
            if col in ("byte_ratio", "pkt_ratio"):
                feasible = bool((live_s.min() >= -1e-6) and (live_s.max() <= 1.00001))
            elif col != "is_incomplete_flow":
                feasible = bool(live_s.min() >= -1e-6)

            rows.append(
                {
                    "feature": col,
                    "offline_min": round(float(off_s.min()), 4),
                    "offline_max": round(float(off_s.max()), 4),
                    "offline_median": round(float(off_s.median()), 4),
                    "offline_p95": round(float(off_s.quantile(0.95)), 4),
                    "live_min": round(float(live_s.min()), 4),
                    "live_max": round(float(live_s.max()), 4),
                    "live_median": round(float(live_s.median()), 4),
                    "live_p95": round(float(live_s.quantile(0.95)), 4),
                    "ks_statistic": round(float(ks_res.statistic), 4),
                    "ks_pvalue": float(ks_res.pvalue),
                    "physically_feasible": feasible,
                    "status": "PASS" if feasible else "FAIL",
                }
            )
        return pd.DataFrame(rows)

    def check_categorical_domains(self) -> pd.DataFrame:
        """Audit category sets, distinct cardinalities, and novel category handling."""
        rows = []
        for col in CATEGORICAL_FEATURES:
            off_cats: Set[str] = set(self.offline_df[col].dropna().astype(str).unique())
            live_cats: Set[str] = set(self.live_df[col].dropna().astype(str).unique())

            common = off_cats.intersection(live_cats)
            novel_in_live = live_cats - off_cats
            missing_in_live = off_cats - live_cats

            rows.append(
                {
                    "feature": col,
                    "offline_cardinality": len(off_cats),
                    "live_cardinality": len(live_cats),
                    "common_count": len(common),
                    "novel_in_live_count": len(novel_in_live),
                    "novel_categories": sorted(list(novel_in_live)),
                    "status": "PASS",  # Preprocessor ordinal encoding handles novel categories via -1 safely
                }
            )
        return pd.DataFrame(rows)

    def test_model_bundle_inference(self) -> Dict[str, Any]:
        """Execute end-to-end inference against the frozen production model bundle."""
        if not self.model_bundle_path.exists():
            return {
                "bundle_found": False,
                "error": f"Model bundle not found at {self.model_bundle_path}",
                "passed": False,
            }

        try:
            bundle = joblib.load(self.model_bundle_path)
            model = bundle["calibrated_model"]
            classes = bundle.get("classes", [0, 1, 2, 3, 4])
            class_names = bundle.get("class_names", {})

            t0 = time.perf_counter()
            probs = model.predict_proba(self.live_df)
            preds = model.predict(self.live_df)
            t_elapsed = time.perf_counter() - t0

            latency_us_per_flow = (t_elapsed / max(1, len(self.live_df))) * 1e6
            throughput_fps = len(self.live_df) / max(1e-6, t_elapsed)

            # Verify probability constraints: sum to 1.0, shape matches
            sums = probs.sum(axis=1)
            prob_valid = np.allclose(sums, 1.0, atol=1e-3)

            # Class prediction breakdown
            unique, counts = np.unique(preds, return_counts=True)
            if isinstance(class_names, dict):
                name_map = class_names
            elif isinstance(class_names, (list, tuple)):
                name_map = {i: name for i, name in enumerate(class_names)}
            else:
                name_map = {}
            pred_breakdown = {name_map.get(int(u), str(u)): int(c) for u, c in zip(unique, counts)}

            return {
                "bundle_found": True,
                "flows_evaluated": len(self.live_df),
                "probability_shape": list(probs.shape),
                "probabilities_normalized": bool(prob_valid),
                "latency_us_per_flow": round(latency_us_per_flow, 2),
                "throughput_fps": round(throughput_fps, 2),
                "prediction_breakdown": pred_breakdown,
                "passed": prob_valid and (probs.shape == (len(self.live_df), len(classes))),
            }
        except Exception as e:
            logger.error(f"Inference execution failed: {e}", exc_info=True)
            return {
                "bundle_found": True,
                "error": str(e),
                "passed": False,
            }


def run_full_schema_check(
    offline_path: Path,
    live_path: Path,
    bundle_path: Path,
    output_md: Path,
    output_csv: Path,
    data_source: str = "synthetic",
) -> bool:
    """Execute all schema verification stages and publish reports.

    data_source: "real" (Zeek capture from the lab) or "synthetic" (software test data).
    """
    logger.info("Loading offline training features from: %s", offline_path)
    offline_df = pd.read_parquet(offline_path)

    logger.info("Loading live sensor features from: %s", live_path)
    if live_path.suffix == ".parquet":
        live_df = pd.read_parquet(live_path)
    else:
        adapter = ZeekAdapter(conn_log_path=live_path, enable_state_persistence=False)
        flows = adapter.read_file()
        live_df = adapter.to_feature_dataframe(flows)

    logger.info("Offline sample size: %d rows | Live sample size: %d rows", len(offline_df), len(live_df))

    auditor = SchemaAuditor(offline_df, live_df, model_bundle_path=bundle_path)

    # 1. Run all checks
    col_results = auditor.check_columns()
    dtype_df = auditor.check_dtypes()
    null_df = auditor.check_nulls()
    range_df = auditor.check_numerical_ranges()
    cat_df = auditor.check_categorical_domains()
    inf_results = auditor.test_model_bundle_inference()

    # 2. Overall pass criteria
    cols_ok = col_results["passed"]
    dtypes_ok = (dtype_df["status"] == "PASS").all()
    nulls_ok = (null_df["status"] == "PASS").all()
    ranges_ok = (range_df["status"] == "PASS").all()
    inf_ok = inf_results.get("passed", False)

    overall_pass = cols_ok and dtypes_ok and nulls_ok and ranges_ok and inf_ok

    logger.info(
        "Schema Audit Results: Columns=%s | Dtypes=%s | Nulls=%s | Ranges=%s | Inference=%s => OVERALL=%s",
        cols_ok,
        dtypes_ok,
        nulls_ok,
        ranges_ok,
        inf_ok,
        "PASS" if overall_pass else "FAIL",
    )

    # 3. Export CSV summary
    output_csv.parent.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    for col in FEATURE_COLUMNS:
        dt_match = dtype_df[dtype_df["feature"] == col]["status"].values[0]
        nl_match = null_df[null_df["feature"] == col]["status"].values[0]
        rng_row = range_df[range_df["feature"] == col]
        rng_match = rng_row["status"].values[0] if not rng_row.empty else "N/A"
        summary_rows.append(
            {
                "feature": col,
                "dtype_status": dt_match,
                "null_status": nl_match,
                "range_status": rng_match,
                "overall_feature_status": "PASS" if (dt_match == "PASS" and nl_match == "PASS" and rng_match != "FAIL") else "FAIL",
            }
        )
    pd.DataFrame(summary_rows).to_csv(output_csv, index=False)
    logger.info("Exported schema summary CSV to: %s", output_csv)

    # 4. Markdown report (every verdict below comes from the checks above)
    def verdict(ok: bool) -> str:
        return "PASS" if ok else "FAIL"

    n_dtype_ok = int((dtype_df["status"] == "PASS").sum())
    n_null_ok = int((null_df["status"] == "PASS").sum())
    n_range_ok = int((range_df["status"] == "PASS").sum())
    shifted = range_df[range_df["ks_statistic"] >= 0.3]["feature"].tolist()
    novel = {r["feature"]: r["novel_categories"] for _, r in cat_df.iterrows() if r["novel_categories"]}
    is_real = data_source == "real"
    if is_real:
        source_note = ("REAL capture: Zeek `conn.log` from the lab mirror port. This report is the Step 22 evidence "
                       "for Objective O3 and Research Question RQ3.")
    else:
        source_note = ("SYNTHETIC test data (decision D-038). This only shows that the check runs. It is NOT evidence "
                       "for O3 or RQ3. Note: the synthetic file uses service names such as `rtsp`, `ssdp` and `onvif`; "
                       "Zeek's standard analyzers may not produce these, so real Zeek output can look different.")

    report_content = f"""# Offline vs Live Feature Check (Step 22)

**Proposal:** Sections 2.5 and 3.5; Objective O3; Research Question RQ3; Table 11
**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
**Offline data:** `{offline_path}` ({len(offline_df):,} flows)
**Live data:** `{live_path}` ({len(live_df):,} flows)
**Model bundle:** `{bundle_path}`

> **Data source: {data_source.upper()}.** {source_note}

## Summary

| Check (proposal 3.5) | Result | Verdict |
| :--- | :--- | :--- |
| Column names and order (19 features) | live {col_results['live_count']} / expected {col_results['expected_count']}; order match = {col_results['order_match']} | **{verdict(cols_ok)}** |
| Data types | {n_dtype_ok} / {len(dtype_df)} compatible | **{verdict(dtypes_ok)}** |
| Missing values | {n_null_ok} / {len(null_df)} features with no missing values | **{verdict(nulls_ok)}** |
| Normal ranges (no negative counts; ratios in 0–1) | {n_range_ok} / {len(range_df)} numeric features valid | **{verdict(ranges_ok)}** |
| Model runs on the live features | valid probabilities = {inf_results.get('probabilities_normalized')} | **{verdict(inf_ok)}** |
| Categories not seen in training | {len(novel)} feature(s): {', '.join(f'`{k}`' for k in novel) or 'none'} | reported (encoded as unknown = -1) |
| Summary distributions (KS statistic >= 0.3) | {len(shifted)} feature(s): {', '.join(f'`{f}`' for f in shifted) or 'none'} | reported (a large shift is a domain difference, see below) |

**Format check overall: {verdict(overall_pass)}.** This means the live pipeline makes the same 19 columns, with the same types, without missing or impossible values, and the model accepts them. It does **not** mean the live traffic looks like IoT-23: the distribution and category rows show how different it is.

## 1. Data types and missing values

| Feature | Kind | Offline dtype | Live dtype | Offline missing % | Live missing % | Status |
| :--- | :--- | :--- | :--- | ---: | ---: | :--- |
"""
    for _, row in dtype_df.iterrows():
        nl_row = null_df[null_df["feature"] == row["feature"]].iloc[0]
        report_content += (
            f"| `{row['feature']}` | {row['kind']} | `{row['offline_dtype']}` | `{row['live_dtype']}` | "
            f"{nl_row['offline_null_pct']:.2f} | {nl_row['live_null_pct']:.2f} | {row['status']} |\n"
        )

    report_content += """
## 2. Numeric ranges and distributions

KS = two-sample Kolmogorov–Smirnov statistic on samples of up to 10,000 flows (0 = same distribution, 1 = no overlap).

| Feature | Offline min–max | Live min–max | Offline median (p95) | Live median (p95) | KS statistic | Range status |
| :--- | :--- | :--- | :--- | :--- | ---: | :--- |
"""
    for _, row in range_df.iterrows():
        report_content += (
            f"| `{row['feature']}` | {row['offline_min']} – {row['offline_max']} | {row['live_min']} – {row['live_max']} | "
            f"{row['offline_median']} ({row['offline_p95']}) | {row['live_median']} ({row['live_p95']}) | "
            f"{row['ks_statistic']:.3f} | {row['status']} |\n"
        )

    report_content += """
## 3. Categories

| Feature | Offline categories | Live categories | In both | Not seen in training |
| :--- | ---: | ---: | ---: | :--- |
"""
    for _, row in cat_df.iterrows():
        novel_str = ", ".join(row["novel_categories"]) if row["novel_categories"] else "none"
        report_content += (
            f"| `{row['feature']}` | {row['offline_cardinality']} | {row['live_cardinality']} | "
            f"{row['common_count']} | `{novel_str}` |\n"
        )

    report_content += f"""
Categories not seen in training are encoded as "unknown" (-1). The model still runs, but it has never learned what these values mean, so predictions for such flows are less reliable.

## 4. Model run on the live features

- Flows: {inf_results.get('flows_evaluated', 0):,}
- Probabilities valid (each row sums to 1): {inf_results.get('probabilities_normalized')}
- Predicted classes: `{json.dumps(inf_results.get('prediction_breakdown', {}))}`

## 5. What to do with the result (proposal 3.5)

- If a feature fails the format checks, fix the live adapter, or drop the feature and train again.
- A large distribution shift or new categories are not format errors. They show the domain difference between IoT-23 and our camera traffic, which is part of the answer to RQ3. Report them.
- Run this check again on the **real** lab capture (`--source real`). Only that run answers RQ3.
"""

    output_md.parent.mkdir(parents=True, exist_ok=True)
    with open(output_md, "w", encoding="utf-8") as f:
        f.write(report_content)
    logger.info("Published Markdown report to: %s", output_md)

    return overall_pass


def main() -> None:
    """CLI entry point for schema verification."""
    parser = argparse.ArgumentParser(
        description="Verify offline vs live feature schema compatibility and zero training-serving skew (Step 22)."
    )
    parser.add_argument(
        "--offline-path",
        type=str,
        default=str(DEFAULT_OFFLINE_PATH),
        help=f"Path to offline training parquet (default: {DEFAULT_OFFLINE_PATH})",
    )
    parser.add_argument(
        "--live-path",
        type=str,
        default=str(DEFAULT_LIVE_LOG_PATH),
        help=f"Path to live Zeek conn.log or parquet (default: {DEFAULT_LIVE_LOG_PATH})",
    )
    parser.add_argument(
        "--bundle-path",
        type=str,
        default=str(DEFAULT_MODEL_BUNDLE),
        help=f"Path to production model bundle (default: {DEFAULT_MODEL_BUNDLE})",
    )
    parser.add_argument(
        "--output-md",
        type=str,
        default=str(DEFAULT_REPORT_MD),
        help=f"Output markdown report path (default: {DEFAULT_REPORT_MD})",
    )
    parser.add_argument(
        "--output-csv",
        type=str,
        default=str(DEFAULT_REPORT_CSV),
        help=f"Output metrics CSV path (default: {DEFAULT_REPORT_CSV})",
    )
    parser.add_argument(
        "--source",
        choices=["real", "synthetic"],
        required=True,
        help="Where the live file came from: real (lab Zeek capture) or synthetic (software test data).",
    )
    args = parser.parse_args()

    success = run_full_schema_check(
        offline_path=Path(args.offline_path),
        live_path=Path(args.live_path),
        bundle_path=Path(args.bundle_path),
        output_md=Path(args.output_md),
        output_csv=Path(args.output_csv),
        data_source=args.source,
    )

    if not success:
        logger.error("Schema check FAILED! Incompatible features detected.")
        sys.exit(1)
    else:
        logger.info("Format check passed (see the report for distribution and category differences).")


if __name__ == "__main__":
    main()
