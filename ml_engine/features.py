#!/usr/bin/env python3
"""
IoT Intrusion Detection Shared Feature Extraction Engine (Step 11)
===================================================================

This module provides the unified feature engineering function `make_features(df)`
matching Research Proposal Section 3.3, Table 6, and Guide Step 11.

Crucial Engineering Principle: Zero Training-Serving Skew
  The EXACT same feature extraction code is used for:
    1. Offline model training and validation (Track 1, Steps 12-18)
    2. Live Zeek streaming detection on sensor PC (Track 2, Step 26)

Candidate Features (Proposal Table 6):
  - Transport (3): proto, orig_port_cat, resp_port_cat (IANA grouped bins)
  - Service & Connection State (3): service, conn_state, history
  - Time & Flow Duration (1): duration (float32)
  - Volume (8): orig_bytes, resp_bytes, missed_bytes, orig_pkts,
               orig_ip_bytes, resp_pkts, resp_ip_bytes, is_incomplete_flow
  - Directional Ratios (4): orig_bytes_per_pkt, resp_bytes_per_pkt,
                           byte_ratio, pkt_ratio (zero-division safe)
  Total: 19 Engineered Features (6 Categorical, 13 Numerical).

Strict Isolation (Golden Rule 5):
  Network identifiers (uid, id.orig_h, id.resp_h, ts, scenario_id) are NEVER
  included in the feature matrix X.
"""

from typing import Union, Dict, List, Any, Optional
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Fixed list of categorical features (Proposal Table 6)
CATEGORICAL_FEATURES: List[str] = [
    "proto",
    "service",
    "conn_state",
    "history",
    "orig_port_cat",
    "resp_port_cat",
]

# Fixed list of numerical features (Proposal Table 6)
NUMERICAL_FEATURES: List[str] = [
    "duration",
    "orig_bytes",
    "resp_bytes",
    "missed_bytes",
    "orig_pkts",
    "orig_ip_bytes",
    "resp_pkts",
    "resp_ip_bytes",
    "orig_bytes_per_pkt",
    "resp_bytes_per_pkt",
    "byte_ratio",
    "pkt_ratio",
    "is_incomplete_flow",
]

# Definitive feature columns list in strictly locked order
FEATURE_COLUMNS: List[str] = CATEGORICAL_FEATURES + NUMERICAL_FEATURES

# Required raw input columns (handling dot and underscore naming)
RAW_REQUIRED_COLUMNS: List[str] = [
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
]


def port_category(port: Any, proto: Any) -> str:
    """
    Categorize a network port into standard IANA bins:
      - 'icmp': When protocol is ICMP (Zeek puts type/code into port fields)
      - 'well_known': System ports (0 - 1023)
      - 'registered': User/Application ports (1024 - 49151)
      - 'dynamic': Dynamic/Private/Ephemeral ports (49152 - 65535)
      - 'unknown': Invalid, missing, or negative values

    Prevents machine learning models from memorizing specific port numbers.
    """
    proto_str = str(proto).strip().lower() if proto is not None else ""
    if proto_str == "icmp":
        return "icmp"

    if pd.isna(port) or port is None:
        return "unknown"

    try:
        p = int(port)
        if 0 <= p < 1024:
            return "well_known"
        elif 1024 <= p < 49152:
            return "registered"
        elif 49152 <= p <= 65535:
            return "dynamic"
        else:
            return "unknown"
    except (ValueError, TypeError):
        return "unknown"


def _vectorized_port_category(ports: pd.Series, protos: pd.Series) -> pd.Series:
    """Fast vectorized port categorization using NumPy."""
    p_num = pd.to_numeric(ports, errors="coerce").fillna(-1).astype(int)
    pr_str = protos.fillna("unknown").astype(str).str.lower()

    conditions = [
        (pr_str == "icmp"),
        (p_num >= 0) & (p_num < 1024),
        (p_num >= 1024) & (p_num < 49152),
        (p_num >= 49152) & (p_num <= 65535),
    ]
    choices = ["icmp", "well_known", "registered", "dynamic"]
    return pd.Series(np.select(conditions, choices, default="unknown"), index=ports.index, dtype=str)


def normalize_input_dataframe(data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]) -> pd.DataFrame:
    """
    Standardize input data into a clean DataFrame with expected column names,
    accommodating live Zeek JSON variations (dot notation vs underscore notation).
    """
    if isinstance(data, dict):
        df = pd.DataFrame([data])
    elif isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, pd.DataFrame):
        df = data.copy()
    else:
        raise TypeError(f"Unsupported data type for feature extraction: {type(data)}")

    # Handle underscore alternative column names from JSON parsers
    aliases = {
        "id_orig_p": "id.orig_p",
        "id_resp_p": "id.resp_p",
        "id_orig_h": "id.orig_h",
        "id_resp_h": "id.resp_h",
    }
    for old_col, new_col in aliases.items():
        if old_col in df.columns and new_col not in df.columns:
            df.rename(columns={old_col: new_col}, inplace=True)

    # Reindex missing required fields with safe nulls for live streaming robustness
    for col in RAW_REQUIRED_COLUMNS:
        if col not in df.columns:
            df[col] = np.nan

    return df


def make_features(
    data: Union[pd.DataFrame, Dict[str, Any], List[Dict[str, Any]]]
) -> pd.DataFrame:
    """
    Extract the standardized 19 features from network flow records.

    Input:
      - DataFrame, dictionary, or list of dictionaries containing raw Zeek flow metrics.

    Output:
      - DataFrame with exactly the 19 columns in `FEATURE_COLUMNS` order, with
        zero NaN values and typed appropriately.
    """
    df = normalize_input_dataframe(data)
    out = pd.DataFrame(index=df.index)

    # 1. Categorical features
    for c in ["proto", "service", "conn_state", "history"]:
        out[c] = (
            df[c]
            .fillna("unknown")
            .replace(["-", "(empty)", ""], "unknown")
            .astype(str)
            .str.lower()
        )

    # Restore uppercase for conn_state & history if needed for standard conventions
    out["conn_state"] = df["conn_state"].fillna("unknown").replace(["-", "(empty)", ""], "unknown").astype(str)
    out["history"] = df["history"].fillna("unknown").replace(["-", "(empty)", ""], "unknown").astype(str)

    # Vectorized port categorization
    out["orig_port_cat"] = _vectorized_port_category(df["id.orig_p"], df["proto"])
    out["resp_port_cat"] = _vectorized_port_category(df["id.resp_p"], df["proto"])

    # 2. Numerical base features
    nums = [
        "duration", "orig_bytes", "resp_bytes", "missed_bytes",
        "orig_pkts", "orig_ip_bytes", "resp_pkts", "resp_ip_bytes"
    ]
    for n in nums:
        out[n] = pd.to_numeric(df[n], errors="coerce").fillna(0.0).astype(np.float32)

    # Non-negative clipping for safety
    for n in nums:
        out[n] = np.maximum(out[n], 0.0)

    # 3. Directional Ratios (Safe Division)
    orig_pkts = out["orig_pkts"].values
    resp_pkts = out["resp_pkts"].values
    orig_bytes = out["orig_bytes"].values
    resp_bytes = out["resp_bytes"].values

    out["orig_bytes_per_pkt"] = np.divide(
        orig_bytes, orig_pkts, out=np.zeros(len(out), dtype=np.float32), where=(orig_pkts > 0)
    )
    out["resp_bytes_per_pkt"] = np.divide(
        resp_bytes, resp_pkts, out=np.zeros(len(out), dtype=np.float32), where=(resp_pkts > 0)
    )

    total_bytes = orig_bytes + resp_bytes
    total_pkts = orig_pkts + resp_pkts

    out["byte_ratio"] = np.divide(
        orig_bytes, total_bytes, out=np.zeros(len(out), dtype=np.float32), where=(total_bytes > 0)
    )
    out["pkt_ratio"] = np.divide(
        orig_pkts, total_pkts, out=np.zeros(len(out), dtype=np.float32), where=(total_pkts > 0)
    )

    # 4. Incomplete connection quality flag (PortScan & SYN flood indicator)
    # Detects: Unanswered SYN (S0), rejected (REJ), reset without data, or zero duration and zero payload
    incomplete_states = {"S0", "REJ", "RSTOS0", "RSTRH", "SH", "SHR"}
    is_inc_state = out["conn_state"].isin(incomplete_states).values
    zero_transfer = (out["duration"].values == 0.0) & ((orig_bytes == 0) | (resp_bytes == 0))
    no_reply = resp_pkts == 0

    out["is_incomplete_flow"] = (is_inc_state | zero_transfer | no_reply).astype(np.int8)

    # 5. Enforce definitive locked column order
    return out[FEATURE_COLUMNS]


def build_feature_preprocessor(scaling: bool = False) -> ColumnTransformer:
    """
    Construct a scikit-learn ColumnTransformer compatible with `FEATURE_COLUMNS`:
      - OneHotEncodes categorical features (handling unseen categories safely).
      - StandardScales numerical features if scaling=True (for Logistic Regression / SVM).
      - Passthrough numerical features if scaling=False (for Random Forest / Gradient Boosting).
    """
    transformers = [
        (
            "cat",
            OneHotEncoder(handle_unknown="ignore", sparse_output=False),
            CATEGORICAL_FEATURES,
        ),
    ]

    if scaling:
        transformers.append(("num", StandardScaler(), NUMERICAL_FEATURES))
    else:
        transformers.append(("num", "passthrough", NUMERICAL_FEATURES))

    return ColumnTransformer(transformers=transformers, remainder="drop")


if __name__ == "__main__":
    print(f"Features Engine Module loaded successfully.")
    print(f"Total Features: {len(FEATURE_COLUMNS)} ({len(CATEGORICAL_FEATURES)} Categorical, {len(NUMERICAL_FEATURES)} Numerical)")
    print(f"Feature Columns: {FEATURE_COLUMNS}")
