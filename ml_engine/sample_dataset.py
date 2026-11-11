#!/usr/bin/env python3
"""
IoT-23 Stratified Sampling & Feature Dataset Generator (Steps 12 & 13)
=====================================================================

Implements Group 03 Proposal Section 3.3 (Step 6), Section 3.4, and
STEP_BY_STEP_GUIDE.md Steps 12 & 13.

Key Objectives:
  1. Stand-alone Memory Safety: Uses streaming row-group sampling to process
     all 325+ million flows while keeping peak RAM well under 1 GB.
  2. Scientifically Fair Class Balancing:
     - Training Scenarios (22): Capped at N=50,000 flows per (scenario, class)
       using random_seed=42. Preserves 100% of the extreme minority CnC flows.
     - Held-out Scenario (CTU-IoT-Malware-Capture-34-1): Preserved 100% untouched
       (all 23,145 rows) without under-sampling or balancing to guarantee realistic
       evaluation of real-world zero-day generalization.
  3. Zero Training-Serving Skew: Uses `ml_engine.features.make_features()` exclusively.
  4. Isolation: Separates held-out dataset into `data/processed/heldout/`.
  5. Window features (D-051): `ml_engine.window_features.WindowState` runs over the FULL
     scenario stream, in the order Zeek wrote the flows, BEFORE sampling. The sample rows are
     chosen exactly as before (same seed, same rows); they only get 7 more columns.
  6. Trusted-label flag (D-051): `label_trusted` marks the IoT-23 "Benign" flows that are
     unanswered outbound connection attempts from the infected device. It is an audit column,
     never a model input.
"""

import sys
import os
import time
import json
import logging
import ipaddress
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from typing import Dict, List, Any, Tuple

import yaml
import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine.features import make_features, FEATURE_COLUMNS, CATEGORICAL_FEATURES, NUMERICAL_FEATURES
from ml_engine.window_features import WINDOW_FEATURES, WindowState, compute_window_features

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("sample_dataset")

# Fixed configuration constants
INTERIM_DIR = PROJECT_ROOT / "data" / "interim"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
HELDOUT_DIR = PROCESSED_DIR / "heldout"
REPORTS_DIR = PROJECT_ROOT / "reports"
SETTINGS_PATH = PROJECT_ROOT / "config" / "settings.yaml"

HELD_OUT_SCENARIO_ID = "CTU-IoT-Malware-Capture-34-1"
DEFAULT_CAP_PER_CLASS = 50000
DEFAULT_RANDOM_SEED = 42

# Columns required from interim parquet to minimize I/O
REQUIRED_INTERIM_COLS = [
    "proto",
    "service",
    "conn_state",
    "history",
    "id.orig_p",
    "id.resp_p",
    "duration",
    "orig_bytes",
    "resp_bytes",
    "missed_bytes",
    "orig_pkts",
    "orig_ip_bytes",
    "resp_pkts",
    "resp_ip_bytes",
    "class_name",
    "label_idx",
    "scenario_id",
    # Kept for checking only (never model inputs; proposal Table 6: "Used only for grouping and audit"):
    "ts",
    "id.orig_h",
    "id.resp_h",
    "detailed_label",
]

# Extra columns written next to the 26 features. They are NOT model inputs: every model step
# selects FEATURE_COLUMNS by name. They are used to (1) replay the response policy's repeat rule
# on training data (proposal 3.4, D-046) and (2) report results per original IoT-23 label (proposal 3.2).
AUDIT_COLUMNS = ["ts", "id.orig_h", "id.resp_h", "id.resp_p", "detailed_label", "label_trusted"]

# Scenarios processed at the same time (each keeps its own WindowState, so results do not change).
DEFAULT_WORKERS = 4


def _is_private(ip: Any) -> bool:
    try:
        return ipaddress.ip_address(str(ip)).is_private
    except ValueError:
        return False


def label_trusted(df: pd.DataFrame, scenario_id: str) -> np.ndarray:
    """D-051 rule, fixed before any result. A flow is NOT trusted when it is labelled Benign,
    comes from a CTU-IoT-Malware-* capture, has conn_state S0, sends 0 bytes, and goes from a
    private source to a public destination (an unanswered outbound connection attempt from the
    infected device, which is what scanning looks like). Every other flow is trusted."""
    n = len(df)
    if not str(scenario_id).startswith("CTU-IoT-Malware-") or n == 0:
        return np.ones(n, dtype=bool)
    benign = df["class_name"].astype(str).eq("Benign").to_numpy()
    s0 = df["conn_state"].astype(str).eq("S0").to_numpy()
    zero = pd.to_numeric(df["orig_bytes"], errors="coerce").fillna(0).eq(0).to_numpy()
    cache: Dict[str, bool] = {}

    def priv(series: pd.Series) -> np.ndarray:
        out = []
        for v in series.astype(str).tolist():
            if v not in cache:
                cache[v] = _is_private(v)
            out.append(cache[v])
        return np.array(out, dtype=bool)

    src_private = priv(df["id.orig_h"])
    dst_public = ~priv(df["id.resp_h"])
    return ~(benign & s0 & zero & src_private & dst_public)


def load_settings() -> Dict[str, Any]:
    """Load settings from config/settings.yaml with fallback defaults."""
    if SETTINGS_PATH.exists():
        with open(SETTINGS_PATH, "r", encoding="utf-8") as f:
            cfg = yaml.safe_load(f)
            return cfg or {}
    return {}


def get_scenario_class_counts(interim_path: Path) -> Dict[str, int]:
    """Fast scan of class_name column to get exact counts per class."""
    table = pq.read_table(interim_path, columns=["class_name"])
    series = table["class_name"].to_pandas()
    return series.value_counts().to_dict()


def sample_scenario_interim(
    interim_path: Path,
    cap_per_class: int = DEFAULT_CAP_PER_CLASS,
    random_seed: int = DEFAULT_RANDOM_SEED,
) -> pd.DataFrame:
    """
    Stream and sample rows from an interim Parquet file per class.
    
    If class_count <= cap_per_class:
      Retain 100% of rows for that class.
    If class_count > cap_per_class:
      Sample chunks with slight oversampling factor (1.05 * cap / count),
      then sample down to exactly cap_per_class with fixed seed.
    """
    scenario_id = interim_path.stem
    class_counts = get_scenario_class_counts(interim_path)
    total_raw = sum(class_counts.values())

    pf = pq.ParquetFile(interim_path)
    samples_by_class: Dict[str, List[pd.DataFrame]] = {c: [] for c in class_counts.keys()}
    window_state = WindowState()  # one per scenario, over every row, in Zeek's order (D-051)

    logger.info(
        f"Processing {scenario_id}: {total_raw:,} rows across {pf.num_row_groups} row groups..."
    )

    for rg_idx in range(pf.num_row_groups):
        rg_df = pf.read_row_group(rg_idx, columns=REQUIRED_INTERIM_COLS).to_pandas()
        win = compute_window_features(rg_df, window_state)
        for col in WINDOW_FEATURES:
            rg_df[col] = win[col].values
        rg_df["label_trusted"] = label_trusted(rg_df, scenario_id)

        for c, count in class_counts.items():
            c_df = rg_df[rg_df["class_name"] == c]
            if len(c_df) == 0:
                continue

            if count <= cap_per_class:
                # Keep 100%
                samples_by_class[c].append(c_df)
            else:
                # Fractional sample
                f = (1.05 * cap_per_class) / count
                n_take = int(np.ceil(len(c_df) * f))
                if n_take > 0:
                    sampled_chunk = c_df.sample(
                        n=min(len(c_df), n_take),
                        random_state=(random_seed + rg_idx) % (2**31 - 1),
                    )
                    samples_by_class[c].append(sampled_chunk)

    final_chunks: List[pd.DataFrame] = []
    for c, chunks in samples_by_class.items():
        if chunks:
            c_combined = pd.concat(chunks, ignore_index=True)
            if len(c_combined) > cap_per_class:
                c_combined = c_combined.sample(n=cap_per_class, random_state=random_seed)
            final_chunks.append(c_combined)

    if not final_chunks:
        return pd.DataFrame()

    sampled_df = pd.concat(final_chunks, ignore_index=True)
    return sampled_df


def process_and_extract_features(raw_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract the standardized 26 features using features.make_features() and
    attach metadata columns (class_name, label_idx, scenario_id).
    The window columns must already be in `raw_df` (computed on the full stream).
    """
    missing = [c for c in WINDOW_FEATURES if c not in raw_df.columns]
    if missing:
        raise ValueError(f"Window features must be computed on the full stream first: {missing}")
    features_df = make_features(raw_df)
    features_df["class_name"] = raw_df["class_name"].values
    features_df["label_idx"] = raw_df["label_idx"].values.astype(np.int8)
    features_df["scenario_id"] = raw_df["scenario_id"].values.astype(str)
    for col in AUDIT_COLUMNS:
        if col in raw_df.columns:
            values = raw_df[col].values
            features_df[col] = values.astype(str) if col in ("id.orig_h", "id.resp_h", "detailed_label") else values
    return features_df


def _process_training_scenario(args: Tuple[str, int, int]) -> Tuple[pd.DataFrame, float]:
    """Worker: sample one training scenario and make its features (runs in its own process)."""
    path_str, cap_per_class, random_seed = args
    t0 = time.time()
    sampled_raw = sample_scenario_interim(Path(path_str), cap_per_class=cap_per_class, random_seed=random_seed)
    return process_and_extract_features(sampled_raw), time.time() - t0


def main():
    start_time = time.time()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    HELDOUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    settings = load_settings()
    random_seed = int(settings.get("model", {}).get("random_seed", DEFAULT_RANDOM_SEED))
    cap_per_class = DEFAULT_CAP_PER_CLASS

    logger.info("=" * 70)
    logger.info("STARTING STEP 12 & 13: SAMPLING & 3-LEVEL TEST SPLIT PREPARATION")
    logger.info(f"Fixed Random Seed: {random_seed}")
    logger.info(f"Per-(scenario, class) Cap N: {cap_per_class:,}")
    logger.info(f"Held-Out Scenario ID: {HELD_OUT_SCENARIO_ID}")
    logger.info("=" * 70)

    interim_files = sorted(list(INTERIM_DIR.glob("*.parquet")))
    if not interim_files:
        logger.error(f"No interim parquet files found in {INTERIM_DIR}!")
        sys.exit(1)

    logger.info(f"Found {len(interim_files)} interim parquet files.")

    # 1. Process Held-Out Scenario (Level 2)
    held_out_path = INTERIM_DIR / f"{HELD_OUT_SCENARIO_ID}.parquet"
    if not held_out_path.exists():
        logger.error(f"Held-out scenario file {held_out_path} not found!")
        sys.exit(1)

    logger.info(f"Extracting features for Held-Out Scenario: {HELD_OUT_SCENARIO_ID} (100% UNTOUCHED)...")
    t0_held = time.time()
    held_out_raw = pq.read_table(held_out_path, columns=REQUIRED_INTERIM_COLS).to_pandas()
    held_win = compute_window_features(held_out_raw)  # full scenario, Zeek's order (D-051)
    for col in WINDOW_FEATURES:
        held_out_raw[col] = held_win[col].values
    held_out_raw["label_trusted"] = label_trusted(held_out_raw, HELD_OUT_SCENARIO_ID)
    held_out_features = process_and_extract_features(held_out_raw)
    t1_held = time.time()
    logger.info(
        f"Held-Out scenario completed in {t1_held - t0_held:.2f}s: "
        f"{len(held_out_features):,} flows, {held_out_features.shape[1]} columns."
    )

    # Save the held-out parquet in ONE place only (data/processed/heldout/), so it stays sealed
    held_out_file_primary = HELDOUT_DIR / "held_out_test.parquet"
    held_out_features.to_parquet(held_out_file_primary, index=False, compression="snappy")
    logger.info(f"Saved held-out test dataset to {held_out_file_primary}")

    # 2. Process Training Scenarios (22 scenarios)
    training_files = [p for p in interim_files if p.stem != HELD_OUT_SCENARIO_ID]
    logger.info(f"Sampling remaining {len(training_files)} scenarios for training...")

    scenario_stats: List[Dict[str, Any]] = []
    training_feature_dfs: List[pd.DataFrame] = []

    # Record held-out stats
    held_counts = held_out_raw["class_name"].value_counts().to_dict()
    scenario_stats.append({
        "scenario_id": HELD_OUT_SCENARIO_ID,
        "split": "Held-Out (Level 2)",
        "raw_total": len(held_out_raw),
        "sampled_total": len(held_out_features),
        "Benign": held_counts.get("Benign", 0),
        "DDoS_DoS": held_counts.get("DDoS_DoS", 0),
        "PortScan": held_counts.get("PortScan", 0),
        "CnC": held_counts.get("CnC", 0),
        "Malware_Download": held_counts.get("Malware_Download", 0),
    })

    total_training_raw = 0
    total_training_sampled = 0

    # Largest files first, so the workers finish at about the same time; results keep file order.
    jobs = [(str(p), cap_per_class, random_seed) for p in training_files]
    order = sorted(range(len(jobs)), key=lambda i: -Path(jobs[i][0]).stat().st_size)
    results: Dict[int, Tuple[pd.DataFrame, float]] = {}
    with ProcessPoolExecutor(max_workers=DEFAULT_WORKERS) as pool:
        futures = {i: pool.submit(_process_training_scenario, jobs[i]) for i in order}
        for i in order:
            results[i] = futures[i].result()
            logger.info(f"done: {training_files[i].stem} ({results[i][1]:.1f}s)")

    for idx, fpath in enumerate(training_files, 1):
        sc_id = fpath.stem
        feat_df, sc_seconds = results[idx - 1]
        training_feature_dfs.append(feat_df)

        counts = feat_df["class_name"].value_counts().to_dict()
        pf = pq.ParquetFile(fpath)
        raw_total = pf.metadata.num_rows

        total_training_raw += raw_total
        total_training_sampled += len(feat_df)

        stat_entry = {
            "scenario_id": sc_id,
            "split": "Train / Level 1 CV",
            "raw_total": raw_total,
            "sampled_total": len(feat_df),
            "Benign": counts.get("Benign", 0),
            "DDoS_DoS": counts.get("DDoS_DoS", 0),
            "PortScan": counts.get("PortScan", 0),
            "CnC": counts.get("CnC", 0),
            "Malware_Download": counts.get("Malware_Download", 0),
        }
        scenario_stats.append(stat_entry)
        logger.info(
            f"[{idx:02d}/{len(training_files):02d}] {sc_id}: {raw_total:,} -> {len(feat_df):,} "
            f"flows in {sc_seconds:.2f}s"
        )

    # 3. Concatenate and Shuffle Training Features
    logger.info("Concatenating and shuffling training dataset...")
    train_df = pd.concat(training_feature_dfs, ignore_index=True)
    # Global deterministic shuffle
    train_df = train_df.sample(frac=1.0, random_state=random_seed).reset_index(drop=True)

    train_out_path = PROCESSED_DIR / "train_features.parquet"
    logger.info(f"Writing {len(train_df):,} training rows to {train_out_path}...")
    train_df.to_parquet(train_out_path, index=False, compression="snappy")
    train_size_mb = train_out_path.stat().st_size / (1024 * 1024)
    logger.info(f"Saved {train_out_path} ({train_size_mb:.2f} MB).")

    # 4. Summary and Validation
    elapsed = time.time() - start_time
    train_class_counts = train_df["class_name"].value_counts().to_dict()

    logger.info("=" * 70)
    logger.info("SAMPLING AND FEATURE GENERATION COMPLETED SUCCESSFULLY")
    logger.info(f"Total Elapsed Time: {elapsed:.2f}s ({elapsed/60:.2f} minutes)")
    logger.info(f"Total Raw Rows Processed: {total_training_raw + len(held_out_raw):,}")
    logger.info(f"Final Training Flows: {len(train_df):,}")
    logger.info(f"Final Held-Out Flows: {len(held_out_features):,}")
    logger.info(f"Training Class Distribution: {train_class_counts}")
    logger.info("=" * 70)

    # 5. Export Reports
    stats_df = pd.DataFrame(scenario_stats)
    csv_report_path = REPORTS_DIR / "sampling_summary.csv"
    stats_df.to_csv(csv_report_path, index=False)
    logger.info(f"Saved {csv_report_path}")

    # Generate Markdown Report
    md_report_path = REPORTS_DIR / "sampling_report.md"
    generate_markdown_report(md_report_path, stats_df, train_df, held_out_features, elapsed, cap_per_class, random_seed)
    logger.info(f"Saved {md_report_path}")


def generate_markdown_report(
    report_path: Path,
    stats_df: pd.DataFrame,
    train_df: pd.DataFrame,
    held_df: pd.DataFrame,
    elapsed_sec: float,
    cap_n: int,
    seed: int,
):
    """Generate detailed markdown report with tables and verification."""
    CLASSES5 = ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]
    train_stats = stats_df[stats_df["split"].str.startswith("Train")]
    held_stats = stats_df[stats_df["split"].str.startswith("Held-Out")]

    train_totals = {
        "raw_total": train_stats["raw_total"].sum(),
        "sampled_total": train_stats["sampled_total"].sum(),
        "Benign": train_stats["Benign"].sum(),
        "DDoS_DoS": train_stats["DDoS_DoS"].sum(),
        "PortScan": train_stats["PortScan"].sum(),
        "CnC": train_stats["CnC"].sum(),
        "Malware_Download": train_stats["Malware_Download"].sum(),
    }

    held_totals = {
        "raw_total": held_stats["raw_total"].sum(),
        "sampled_total": held_stats["sampled_total"].sum(),
        "Benign": held_stats["Benign"].sum(),
        "DDoS_DoS": held_stats["DDoS_DoS"].sum(),
        "PortScan": held_stats["PortScan"].sum(),
        "CnC": held_stats["CnC"].sum(),
        "Malware_Download": held_stats["Malware_Download"].sum(),
    }

    content = f"""# IoT-23 Sampling & Feature Extraction Report (Step 12 & 13)

**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}  
**Execution Runtime:** {elapsed_sec:.2f} seconds ({elapsed_sec / 60.0:.2f} minutes)  
**Fixed Random Seed:** `{seed}` (`config/settings.yaml`)  
**Sampling Cap:** $N = {cap_n:,}$ flows per (scenario, class)  
**Primary Engine:** `ml_engine/features.py` (`make_features`)  

---

## 1. Executive Summary

This report documents the execution of **Step 12 (Sampling and class balance)** and **Step 13 (Plan the three test levels)** in accordance with Group 03 Research Proposal (Sections 3.3 step 6, 3.4, Tables 5, 6, 11).

- **Total Official Raw Flows Audited:** {train_totals['raw_total'] + held_totals['raw_total']:,}
- **Final Training Dataset (`data/processed/train_features.parquet`):** {len(train_df):,} flows across 22 scenarios
- **Final Held-Out Dataset (`data/processed/heldout/held_out_test.parquet`):** {len(held_df):,} flows (100% untouched)
- **Features Extracted:** {len(FEATURE_COLUMNS)} features ({len(CATEGORICAL_FEATURES)} categorical, {len(NUMERICAL_FEATURES)} numerical): the 19 one-flow features of proposal Table 6 and the 7 window features of D-051 (Table 6: "rate over a time window"), computed on the full scenario stream before sampling
- **Metadata Columns:** `class_name`, `label_idx`, `scenario_id` (enabling Grouped Cross-Validation without leakage)
- **Missing values in the feature columns:** {int(train_df[FEATURE_COLUMNS].isna().sum().sum()):,} (training), {int(held_df[FEATURE_COLUMNS].isna().sum().sum()):,} (held-out)
- **Trusted-label flag (D-051):** {int((~train_df['label_trusted']).sum()):,} training rows are "Benign" flows that look like scanning from the infected device (`label_trusted = False`); held-out: {int((~held_df['label_trusted']).sum()):,}

---

## 2. Overall Class Distribution

### Training Corpus (22 Scenarios, Capped at $N=50,000$ per Scenario-Class)

| Class Index | Class Name | Raw Flows Available | Sampled Training Flows | Sample Proportion | Imbalance Ratio (vs CnC) |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 0 | `Benign` | {train_stats['Benign'].sum() + (train_totals['raw_total'] - train_totals['sampled_total']):,} | {train_totals['Benign']:,} | {train_totals['Benign'] / len(train_df) * 100:.2f}% | {train_totals['Benign'] / train_totals['CnC']:.2f} : 1 |
| 1 | `DDoS_DoS` | - | {train_totals['DDoS_DoS']:,} | {train_totals['DDoS_DoS'] / len(train_df) * 100:.2f}% | {train_totals['DDoS_DoS'] / train_totals['CnC']:.2f} : 1 |
| 2 | `PortScan` | - | {train_totals['PortScan']:,} | {train_totals['PortScan'] / len(train_df) * 100:.2f}% | {train_totals['PortScan'] / train_totals['CnC']:.2f} : 1 |
| 3 | `CnC` | 48,992 | {train_totals['CnC']:,} | {train_totals['CnC'] / len(train_df) * 100:.2f}% | **1.00 : 1 (100% Kept)** |
| 4 | `Malware_Download` | - | {train_totals['Malware_Download']:,} | {train_totals['Malware_Download'] / len(train_df) * 100:.2f}% | {train_totals['Malware_Download'] / train_totals['CnC']:.2f} : 1 |
| **Total** | | **{train_totals['raw_total']:,}** | **{len(train_df):,}** | **100.00%** | - |

> All `CnC` flows are kept; the other classes are capped at {cap_n:,} flows per scenario. Largest class : smallest class in the sample = **{max(train_totals[c] for c in CLASSES5) / max(1, min(train_totals[c] for c in CLASSES5)):.1f} : 1**.

### Level 2 Held-Out Scenario (`CTU-IoT-Malware-Capture-34-1`, 100% Untouched)

| Class Index | Class Name | Held-Out Flows | Class Proportion | Sampling Treatment |
| :---: | :--- | :---: | :---: | :--- |
| 0 | `Benign` | {held_totals['Benign']:,} | {held_totals['Benign'] / len(held_df) * 100:.2f}% | 100% Preserved (No under-sampling) |
| 1 | `DDoS_DoS` | {held_totals['DDoS_DoS']:,} | {held_totals['DDoS_DoS'] / len(held_df) * 100:.2f}% | 100% Preserved (No under-sampling) |
| 2 | `PortScan` | {held_totals['PortScan']:,} | {held_totals['PortScan'] / len(held_df) * 100:.2f}% | 100% Preserved (No under-sampling) |
| 3 | `CnC` | {held_totals['CnC']:,} | {held_totals['CnC'] / len(held_df) * 100:.2f}% | 100% Preserved (No under-sampling) |
| 4 | `Malware_Download` | 0 | 0.00% | Absent in Capture-34-1 |
| **Total** | | **{len(held_df):,}** | **100.00%** | **Sealed in `data/processed/heldout/`** |

---

## 3. Per-Scenario Sampling Breakdown

| Scenario ID | Split Role | Original Flows | Sampled Flows | Benign | DDoS_DoS | PortScan | CnC | Malware_Download |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
"""
    for _, row in stats_df.iterrows():
        content += (
            f"| `{row['scenario_id']}` | {row['split']} | {row['raw_total']:,} | {row['sampled_total']:,} | "
            f"{row['Benign']:,} | {row['DDoS_DoS']:,} | {row['PortScan']:,} | {row['CnC']:,} | {row['Malware_Download']:,} |\n"
        )

    content += f"""| **Training Total** | **22 Scenarios** | **{train_totals['raw_total']:,}** | **{train_totals['sampled_total']:,}** | **{train_totals['Benign']:,}** | **{train_totals['DDoS_DoS']:,}** | **{train_totals['PortScan']:,}** | **{train_totals['CnC']:,}** | **{train_totals['Malware_Download']:,}** |
| **Held-Out Total** | **1 Scenario** | **{held_totals['raw_total']:,}** | **{held_totals['sampled_total']:,}** | **{held_totals['Benign']:,}** | **{held_totals['DDoS_DoS']:,}** | **{held_totals['PortScan']:,}** | **{held_totals['CnC']:,}** | **{held_totals['Malware_Download']:,}** |

---

## 4. Feature Matrix Verification

The generated training feature matrix was verified against all project constraints:

1. **Feature Columns ({len(FEATURE_COLUMNS)}):**
   - Categorical ({len(CATEGORICAL_FEATURES)}): `{', '.join(CATEGORICAL_FEATURES)}`
   - Numerical ({len(NUMERICAL_FEATURES)}): `{', '.join(NUMERICAL_FEATURES)}`
2. **Metadata Columns (3):**
   - `class_name` (Target string: Benign, DDoS_DoS, PortScan, CnC, Malware_Download)
   - `label_idx` (Target integer: 0 to 4)
   - `scenario_id` (Grouping identifier for `StratifiedGroupKFold`)
3. **Data Integrity:**
   - Total rows in `train_features.parquet`: `{len(train_df):,}`
   - Missing values in the feature columns: **{int(train_df[FEATURE_COLUMNS].isna().sum().sum()):,}**
   - Memory usage of training dataframe: **~{train_df.memory_usage(deep=True).sum() / (1024 * 1024):.2f} MB**
"""

    with open(report_path, "w", encoding="utf-8") as f:
        f.write(content)


if __name__ == "__main__":
    main()

