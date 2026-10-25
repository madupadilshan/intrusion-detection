#!/usr/bin/env python3
"""
Unit and Integration Tests for Step 12 & Step 13:
Dataset Sampling, Feature Parquets, and Three-Level Evaluation Plan
===================================================================
"""

from pathlib import Path
import pytest
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
from sklearn.model_selection import StratifiedGroupKFold

from ml_engine.features import FEATURE_COLUMNS, CATEGORICAL_FEATURES, NUMERICAL_FEATURES

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
TRAIN_PARQUET = PROJECT_ROOT / "data" / "processed" / "train_features.parquet"
HELDOUT_PARQUET = PROJECT_ROOT / "data" / "processed" / "heldout" / "held_out_test.parquet"
HELDOUT_SECONDARY = PROJECT_ROOT / "data" / "processed" / "held_out_test.parquet"
REPORTS_DIR = PROJECT_ROOT / "reports"
TEST_SPLIT_PLAN = REPORTS_DIR / "test_split_plan.md"
SAMPLING_REPORT = REPORTS_DIR / "sampling_report.md"
SAMPLING_CSV = REPORTS_DIR / "sampling_summary.csv"

EXPECTED_METADATA_COLS = ["class_name", "label_idx", "scenario_id"]
ALL_EXPECTED_COLS = FEATURE_COLUMNS + EXPECTED_METADATA_COLS
HELD_OUT_SCENARIO_ID = "CTU-IoT-Malware-Capture-34-1"


def test_files_exist():
    """Verify all expected parquets and reports exist on disk."""
    assert TRAIN_PARQUET.exists(), f"Missing {TRAIN_PARQUET}"
    assert HELDOUT_PARQUET.exists(), f"Missing {HELDOUT_PARQUET}"
    assert HELDOUT_SECONDARY.exists(), f"Missing {HELDOUT_SECONDARY}"
    assert TEST_SPLIT_PLAN.exists(), f"Missing {TEST_SPLIT_PLAN}"
    assert SAMPLING_REPORT.exists(), f"Missing {SAMPLING_REPORT}"
    assert SAMPLING_CSV.exists(), f"Missing {SAMPLING_CSV}"


def test_train_parquet_schema_and_integrity():
    """Verify train_features.parquet has exact row count, schema, zero NaNs, and correct types."""
    pf = pq.ParquetFile(TRAIN_PARQUET)
    assert pf.metadata.num_rows == 1384070, f"Expected 1,384,070 rows, got {pf.metadata.num_rows}"
    assert pf.metadata.num_columns == 22, f"Expected 22 columns, got {pf.metadata.num_columns}"

    # Check columns
    col_names = pf.schema.names
    for col in ALL_EXPECTED_COLS:
        assert col in col_names, f"Missing column {col} in train_features.parquet"

    # Read small sample to verify no NaN
    df_sample = pf.read_row_group(0).to_pandas()
    assert df_sample.isna().sum().sum() == 0, "Found NaN values in train_features row group 0"


def test_held_out_parquet_schema_and_isolation():
    """Verify held_out_test.parquet has exact 23,145 rows, zero NaNs, and complete scenario isolation."""
    table = pq.read_table(HELDOUT_PARQUET)
    assert table.num_rows == 23145, f"Expected 23,145 rows, got {table.num_rows}"
    assert table.num_columns == 22, f"Expected 22 columns, got {table.num_columns}"

    df_held = table.to_pandas()
    assert df_held.isna().sum().sum() == 0, "Found NaN values in held_out_test.parquet"
    
    unique_scenarios = df_held["scenario_id"].unique().tolist()
    assert unique_scenarios == [HELD_OUT_SCENARIO_ID], f"Unexpected scenarios in held-out: {unique_scenarios}"

    # Verify class distribution in held-out
    vc = df_held["class_name"].value_counts().to_dict()
    assert vc.get("DDoS_DoS", 0) == 14394
    assert vc.get("CnC", 0) == 6706
    assert vc.get("Benign", 0) == 1923
    assert vc.get("PortScan", 0) == 122


def test_no_scenario_leakage_between_train_and_heldout():
    """Verify held-out scenario is strictly absent from the training set."""
    # Read only scenario_id column from train_features
    table = pq.read_table(TRAIN_PARQUET, columns=["scenario_id"])
    train_scenarios = set(table["scenario_id"].to_pandas().unique())

    assert HELD_OUT_SCENARIO_ID not in train_scenarios, (
        f"DATA LEAKAGE DETECTED! {HELD_OUT_SCENARIO_ID} found in train_features.parquet"
    )
    assert len(train_scenarios) == 22, f"Expected 22 training scenarios, got {len(train_scenarios)}"


def test_class_balance_and_extreme_minority_preservation():
    """Verify training dataset class distribution and 100% preservation of CnC."""
    table = pq.read_table(TRAIN_PARQUET, columns=["class_name"])
    vc = table["class_name"].to_pandas().value_counts().to_dict()

    assert vc["PortScan"] == 500000
    assert vc["Benign"] == 345424
    assert vc["Malware_Download"] == 250069
    assert vc["DDoS_DoS"] == 239585
    assert vc["CnC"] == 48992, f"Expected all 48,992 CnC flows preserved, got {vc['CnC']}"


def test_level_1_stratified_group_kfold_feasibility():
    """Verify that Level 1 StratifiedGroupKFold splits cleanly without scenario leakage across folds."""
    # Read metadata columns
    table = pq.read_table(TRAIN_PARQUET, columns=["scenario_id", "label_idx"])
    meta_df = table.to_pandas()

    sgkf = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)
    X_dummy = np.zeros(len(meta_df))
    y = meta_df["label_idx"].values
    groups = meta_df["scenario_id"].values

    for fold, (train_idx, val_idx) in enumerate(sgkf.split(X_dummy, y, groups=groups)):
        train_groups = set(groups[train_idx])
        val_groups = set(groups[val_idx])

        # Overlap must be empty set (zero leakage)
        overlap = train_groups.intersection(val_groups)
        assert len(overlap) == 0, f"Fold {fold} has leaking scenario groups: {overlap}"

        # Train fold MUST have all 5 classes to properly fit multi-class classifiers
        train_classes = set(y[train_idx])
        assert len(train_classes) == 5, f"Fold {fold} training set missing classes: {train_classes}"

        # Validation fold must have at least 3 classes
        val_classes = set(y[val_idx])
        assert len(val_classes) >= 3, f"Fold {fold} validation fold missing too many classes: {val_classes}"
