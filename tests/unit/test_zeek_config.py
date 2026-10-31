"""tests/unit/test_zeek_config.py - Unit test suite for Step 19 Zeek sensor integration.

Validates:
1. Zeek configuration script (sensor/local.zeek) syntax and required directives.
2. Sensor execution shell script (sensor/run_zeek.sh) structure and options.
3. Zeek runner and simulation engine (sensor/zeek_runner.py) flow generation.
4. Schema compatibility: verifies Zeek JSON records convert to 19 features with 0 NaNs.
5. End-to-end model inference on simulated Zeek conn.log streams using ids_bundle_v1.joblib.
"""

import json
from pathlib import Path
import joblib
import pandas as pd
import pytest

from ml_engine.features import FEATURE_COLUMNS, make_features
from sensor.zeek_runner import (
    ZEEK_CONN_CORE_FIELDS,
    generate_simulated_conn_log,
    generate_simulated_conn_record,
    verify_conn_log_schema,
)

SENSOR_DIR = Path("sensor")
ZEEK_CONFIG_PATH = SENSOR_DIR / "local.zeek"
ZEEK_SH_PATH = SENSOR_DIR / "run_zeek.sh"
BUNDLE_PATH = Path("ml_engine/models/ids_bundle_v1.joblib")


def test_zeek_local_config_file():
    """Verify local.zeek existence and mandatory streaming JSON directives."""
    assert ZEEK_CONFIG_PATH.exists(), f"Zeek config missing at {ZEEK_CONFIG_PATH}"
    content = ZEEK_CONFIG_PATH.read_text(encoding="utf-8")

    assert "@load policy/tuning/json-logs.zeek" in content, "Must load JSON logging policy"
    assert "redef Log::default_rotation_interval = 0 sec;" in content, "Must disable rotation for continuous tailing"
    assert "redef ignore_checksums = T;" in content, "Must ignore checksums for port mirror traffic"
    assert "@load base/protocols/conn" in content, "Must load base connection protocol"


def test_zeek_run_sh_script():
    """Verify run_zeek.sh structure, bash shebang, and option flags."""
    assert ZEEK_SH_PATH.exists(), f"run_zeek.sh missing at {ZEEK_SH_PATH}"
    content = ZEEK_SH_PATH.read_text(encoding="utf-8")

    assert content.startswith("#!/usr/bin/env bash"), "Script must have bash shebang"
    assert "set -euo pipefail" in content, "Script must use strict error handling"
    for option in ["--interface", "--pcap", "--log-dir", "--daemon", "--stop", "--status"]:
        assert option in content, f"Script missing option flag: {option}"


def test_simulated_conn_records_generation(tmp_path):
    """Verify simulation engine produces valid Zeek conn.log JSON objects."""
    test_log = tmp_path / "conn.log"
    count = generate_simulated_conn_log(test_log, flow_count=30)
    assert count == 30
    assert test_log.exists()

    with open(test_log, "r", encoding="utf-8") as f:
        lines = f.readlines()
    assert len(lines) == 30

    # Parse each record
    for line in lines:
        rec = json.loads(line)
        for field in ["ts", "uid", "id.orig_h", "id.orig_p", "id.resp_h", "id.resp_p", "proto", "conn_state"]:
            assert field in rec, f"Missing required Zeek key '{field}'"


def test_conn_log_schema_verification(tmp_path):
    """Verify that conn.log records convert to 19 features without NaNs."""
    test_log = tmp_path / "conn.log"
    generate_simulated_conn_log(test_log, flow_count=50)

    results = verify_conn_log_schema(test_log)
    assert results["valid_json_count"] == 50
    assert results["feature_row_count"] == 50
    assert results["feature_column_count"] == len(FEATURE_COLUMNS)
    assert results["nan_count"] == 0


def test_live_zeek_records_inference_with_model_bundle(tmp_path):
    """Verify that the production model bundle predicts on live Zeek records."""
    assert BUNDLE_PATH.exists(), "Model bundle ids_bundle_v1.joblib must exist"
    bundle = joblib.load(BUNDLE_PATH)
    pipeline = bundle["pipeline"]
    calibrated = bundle["calibrated_model"]

    # Generate records representing different scenarios
    records = [
        generate_simulated_conn_record("benign_rtsp"),
        generate_simulated_conn_record("benign_dns"),
        generate_simulated_conn_record("ddos_syn"),
        generate_simulated_conn_record("portscan_probe"),
        generate_simulated_conn_record("cnc_beacon"),
    ]

    df_raw = pd.DataFrame(records)
    feat_df = make_features(df_raw)
    assert list(feat_df.columns) == FEATURE_COLUMNS

    # Predict
    preds = pipeline.predict(feat_df)
    assert len(preds) == len(records)
    assert all(p in [0, 1, 2, 3, 4] for p in preds)

    # Probabilities
    probs = calibrated.predict_proba(feat_df)
    assert probs.shape == (len(records), 5)
    assert (probs.sum(axis=1) >= 0.99).all() and (probs.sum(axis=1) <= 1.01).all()

