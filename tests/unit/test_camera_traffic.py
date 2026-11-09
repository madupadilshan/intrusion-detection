"""tests/unit/test_camera_traffic.py - Unit test suite for Step 20 benign camera traffic.

Validates:
1. Benign IP-camera traffic generation and collection (RTSP, HTTP, ONVIF, DNS, NTP).
2. Zeek conn.log JSON schema integrity and feature extraction (0 NaNs, 19 columns).
3. Hypothesis H1 Clause 2 verification: Benign FPR <= 5% and Active Blocking FPR <= 1%.
4. Existence and completeness of camera baseline reports and CSV artifacts.
"""

import json
from pathlib import Path
import pandas as pd
import pytest

from ml_engine.features import FEATURE_COLUMNS, make_features
from sensor.collect_camera_traffic import (
    collect_benign_camera_traffic,
    evaluate_camera_baseline_fpr,
    generate_camera_flow,
)

REPORT_MD_PATH = Path("reports/experiments/camera_baseline_summary.md")
REPORT_CSV_PATH = Path("reports/experiments/camera_baseline_summary.csv")


def test_camera_flow_generators():
    """Verify flow records for all 5 operational camera activity types."""
    session_types = [
        "rtsp_streaming",
        "camera_web_api",
        "device_discovery",
        "dns_ntp_support",
        "background_keepalive",
    ]
    for stype in session_types:
        record = generate_camera_flow(stype, base_ts=1700000000.0)
        assert isinstance(record, dict)
        for req_field in ["ts", "uid", "id.orig_h", "id.orig_p", "id.resp_h", "id.resp_p", "proto", "conn_state"]:
            assert req_field in record, f"Missing field '{req_field}' in {stype} flow"


def test_collect_benign_camera_traffic(tmp_path):
    """Test generating and saving benign camera connection streams."""
    output_dir = tmp_path / "local_benign"
    conn_log_path = collect_benign_camera_traffic(output_dir, total_flows=50, date_str="test_run")
    assert conn_log_path.exists()

    with open(conn_log_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    assert len(lines) == 50


def test_camera_features_extraction(tmp_path):
    """Verify that camera flows transform cleanly into 19 features with 0 NaNs."""
    output_dir = tmp_path / "local_benign"
    conn_log_path = collect_benign_camera_traffic(output_dir, total_flows=40, date_str="test_run")

    records = []
    with open(conn_log_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                records.append(json.loads(line))

    df_raw = pd.DataFrame(records)
    feat_df = make_features(df_raw)

    assert list(feat_df.columns) == FEATURE_COLUMNS
    assert len(feat_df) == 40
    assert int(feat_df.isna().sum().sum()) == 0


def test_evaluate_camera_baseline_fpr(tmp_path):
    """Synthetic data is checked and reported, but never judged against H1."""
    output_dir = tmp_path / "local_synthetic"
    conn_log_path = collect_benign_camera_traffic(output_dir, total_flows=100, date_str="test_run")

    rep_md = tmp_path / "report.md"
    rep_csv = tmp_path / "report.csv"

    summary = evaluate_camera_baseline_fpr(
        conn_log_path=conn_log_path,
        report_output_path=rep_md,
        csv_output_path=rep_csv,
        data_source="synthetic",
    )

    assert summary["total_camera_flows"] == 100
    assert summary["data_source"] == "synthetic"
    assert 0.0 <= summary["raw_fpr"] <= 1.0
    assert summary["h1_fpr_result"] == "not tested (synthetic data)"
    text = rep_md.read_text(encoding="utf-8")
    assert "SYNTHETIC" in text and "not a measurement" in text
    assert rep_csv.exists()


def test_evaluate_real_source_reports_h1_result(tmp_path):
    """With data_source='real' the report gives a met / not met result for the FPR target."""
    conn_log_path = collect_benign_camera_traffic(tmp_path / "x", total_flows=30, date_str="t")
    summary = evaluate_camera_baseline_fpr(
        conn_log_path=conn_log_path,
        report_output_path=tmp_path / "r.md",
        csv_output_path=tmp_path / "r.csv",
        data_source="real",
    )
    assert summary["h1_fpr_result"] in ("met", "not met")
    assert "REAL capture" in (tmp_path / "r.md").read_text(encoding="utf-8")


def test_evaluate_rejects_unknown_source(tmp_path):
    conn_log_path = collect_benign_camera_traffic(tmp_path / "y", total_flows=5, date_str="t")
    with pytest.raises(ValueError):
        evaluate_camera_baseline_fpr(conn_log_path, report_output_path=tmp_path / "a.md",
                                     csv_output_path=tmp_path / "a.csv", data_source="camera")


def test_camera_baseline_artifacts_exist():
    """The committed report must say clearly that its data is synthetic."""
    assert REPORT_MD_PATH.exists(), f"Missing report at {REPORT_MD_PATH}"
    assert REPORT_CSV_PATH.exists(), f"Missing CSV at {REPORT_CSV_PATH}"

    content = REPORT_MD_PATH.read_text(encoding="utf-8")
    assert "# Benign Camera Traffic Check (Step 20)" in content
    assert "SYNTHETIC" in content
    assert "PASS" not in content
