"""Tests for the training variants (D-051, D-052): which rows each variant keeps."""

import sys
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine.training_rows import (  # noqa: E402
    VARIANTS,
    apply_variant,
    label_disputed,
    load_disputed,
    variant_mask,
)

ENTRY = [{"scenario_id": "CTU-IoT-Malware-Capture-42-1", "hosts": ["192.168.1.197", "185.244.25.183"]}]


def frame():
    return pd.DataFrame({
        "scenario_id": ["CTU-IoT-Malware-Capture-42-1"] * 4 + ["CTU-IoT-Malware-Capture-34-1"],
        "id.orig_h": ["192.168.1.197", "185.244.25.183", "192.168.1.197", "192.168.1.197", "192.168.1.197"],
        "id.resp_h": ["185.244.25.183", "192.168.1.197", "104.24.96.120", "185.244.25.183", "185.244.25.183"],
        "label_trusted": [True, True, True, False, True],
        "x": [0, 1, 2, 3, 4],
    })


def test_disputed_matches_both_directions_and_only_its_scenario():
    assert label_disputed(frame(), ENTRY).tolist() == [True, True, False, True, False]


def test_variant_masks():
    df = frame()
    assert variant_mask(df, "W").tolist() == [True] * 5
    assert variant_mask(df, "WC").tolist() == [True, True, True, False, True]
    # WCD uses the real config file; check it lists the 42-1 entry first
    assert load_disputed()[0]["scenario_id"] == "CTU-IoT-Malware-Capture-42-1"
    assert variant_mask(df, "WCD").tolist() == [False, False, True, False, True]
    assert apply_variant(df, "WCD")["x"].tolist() == [2, 4]


def test_unknown_variant_and_missing_column():
    assert VARIANTS == ("W", "WC", "WCD")
    with pytest.raises(ValueError):
        variant_mask(frame(), "XYZ")
    with pytest.raises(ValueError):
        variant_mask(frame().drop(columns="label_trusted"), "WCD")
