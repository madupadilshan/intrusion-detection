#!/usr/bin/env python3
"""
ml_engine/training_rows.py - Which training rows are used (decisions D-051 and D-052).

Variants (each is compared with a rule fixed before the results):
  - "W"   : all sampled rows.
  - "WC"  : the same, but rows with `label_trusted = False` are left out (IoT-23 "Benign" flows
            that are unanswered outbound connection attempts from the infected device; D-051).
  - "WCD" : WC, and the rows listed in `config/disputed_labels.yaml` are also left out (D-052).
            Labels are never changed; disputed rows are only left out.

`ml_engine/select_variant.py` writes the chosen variant to `reports/experiments/variant_selection.json`.
Every later step (15, 17) reads the training rows through `load_training_frame()`, so all steps
use exactly the same rows, in the same order, as the out-of-fold predictions of Step 14.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional

import numpy as np
import pandas as pd
import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TRAIN_PARQUET = PROJECT_ROOT / "data" / "processed" / "train_features.parquet"
VARIANT_FILE = PROJECT_ROOT / "reports" / "experiments" / "variant_selection.json"
DISPUTED_FILE = PROJECT_ROOT / "config" / "disputed_labels.yaml"
VARIANTS = ("W", "WC", "WCD")
# Columns each variant needs to decide which rows to keep.
VARIANT_COLUMNS = {
    "W": [],
    "WC": ["label_trusted"],
    "WCD": ["label_trusted", "scenario_id", "id.orig_h", "id.resp_h"],
}


def load_disputed(path: Path = DISPUTED_FILE) -> List[dict]:
    """The disputed-label entries (D-052); an empty list if the file is missing."""
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8")) or {}
    except OSError:
        return []
    return list(data.get("disputed") or [])


def label_disputed(df: pd.DataFrame, entries: Optional[List[dict]] = None) -> np.ndarray:
    """True for rows that match an entry of config/disputed_labels.yaml (same scenario, and the
    two addresses are the entry's two hosts, in either direction)."""
    entries = load_disputed() if entries is None else entries
    out = np.zeros(len(df), dtype=bool)
    if not entries or len(df) == 0:
        return out
    sc = df["scenario_id"].astype(str).to_numpy()
    a = df["id.orig_h"].astype(str).to_numpy()
    b = df["id.resp_h"].astype(str).to_numpy()
    for e in entries:
        h1, h2 = (str(x) for x in e["hosts"])
        hit = (sc == str(e["scenario_id"])) & (((a == h1) & (b == h2)) | ((a == h2) & (b == h1)))
        out |= hit
    return out


def variant_mask(df: pd.DataFrame, variant: str) -> np.ndarray:
    """Boolean mask of the rows kept by `variant`."""
    if variant not in VARIANTS:
        raise ValueError(f"Unknown variant {variant!r}; use one of {VARIANTS}")
    keep = np.ones(len(df), dtype=bool)
    if variant in ("WC", "WCD"):
        if "label_trusted" not in df.columns:
            raise ValueError(f"Variant {variant} needs the 'label_trusted' column (re-run Step 12).")
        keep &= df["label_trusted"].astype(bool).to_numpy()
    if variant == "WCD":
        keep &= ~label_disputed(df)
    return keep


def chosen_variant(path: Path = VARIANT_FILE) -> str:
    """The variant chosen by select_variant.py; "W" if no choice has been made yet."""
    try:
        v = json.loads(Path(path).read_text(encoding="utf-8")).get("chosen", "W")
    except (OSError, ValueError):
        return "W"
    return v if v in VARIANTS else "W"


def apply_variant(df: pd.DataFrame, variant: str) -> pd.DataFrame:
    """Keep the rows of the given variant (row order is kept)."""
    return df[variant_mask(df, variant)].reset_index(drop=True)


def load_training_frame(path: Path = TRAIN_PARQUET, columns: Optional[List[str]] = None,
                        variant: Optional[str] = None) -> pd.DataFrame:
    """Read the training parquet and keep the rows of `variant` (default: the chosen one)."""
    v = variant or chosen_variant()
    cols = None
    if columns is not None:
        cols = list(dict.fromkeys(list(columns) + VARIANT_COLUMNS[v]))
    df = pd.read_parquet(path, columns=cols)
    df = apply_variant(df, v)
    if columns is not None:
        df = df[list(columns)]
    return df
