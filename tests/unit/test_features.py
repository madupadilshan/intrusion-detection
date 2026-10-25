#!/usr/bin/env python3
"""
Unit Tests for Shared Feature Extraction Engine (Step 11)
=========================================================

Verifies:
  1. Port categorization (Well-known, Registered, Dynamic, ICMP, Unknown).
  2. Extraction on real IoT-23 interim dataset rows.
  3. Extraction on live streaming Zeek JSON records (with missing fields).
  4. Robustness against zero division (zero packets, zero bytes).
  5. Incomplete connection flag logic (S0, REJ vs SF).
  6. Scikit-learn ColumnTransformer compatibility (fit and transform).
"""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path

from ml_engine.features import (
    port_category,
    make_features,
    build_feature_preprocessor,
    FEATURE_COLUMNS,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)


class TestPortCategory:
    """Test standard IANA port categorization rules."""

    def test_well_known_ports(self):
        assert port_category(80, "tcp") == "well_known"
        assert port_category(443, "tcp") == "well_known"
        assert port_category(53, "udp") == "well_known"
        assert port_category(0, "tcp") == "well_known"
        assert port_category(1023, "tcp") == "well_known"

    def test_registered_ports(self):
        assert port_category(1024, "tcp") == "registered"
        assert port_category(8080, "tcp") == "registered"
        assert port_category(49151, "udp") == "registered"

    def test_dynamic_ports(self):
        assert port_category(49152, "tcp") == "dynamic"
        assert port_category(60000, "udp") == "dynamic"
        assert port_category(65535, "tcp") == "dynamic"

    def test_icmp_override(self):
        # ICMP types (e.g. type 8 echo request) must be classified as 'icmp'
        assert port_category(8, "icmp") == "icmp"
        assert port_category(0, "ICMP") == "icmp"
        assert port_category(None, "icmp") == "icmp"

    def test_unknown_and_invalid_ports(self):
        assert port_category(None, "tcp") == "unknown"
        assert port_category(np.nan, "tcp") == "unknown"
        assert port_category(-1, "tcp") == "unknown"
        assert port_category(70000, "tcp") == "unknown"
        assert port_category("invalid", "tcp") == "unknown"


class TestMakeFeatures:
    """Test feature transformation on real and synthetic network flows."""

    def test_iot23_interim_row(self):
        """Test on actual interim Parquet flow record if available."""
        parquet_path = Path("data/interim/CTU-IoT-Malware-Capture-34-1.parquet")
        if parquet_path.exists():
            df = pd.read_parquet(parquet_path).head(10)
            feats = make_features(df)

            assert list(feats.columns) == FEATURE_COLUMNS
            assert len(feats) == 10
            assert feats.isna().sum().sum() == 0

    def test_zeek_live_json_record(self):
        """Test with realistic Zeek streaming JSON records with missing fields."""
        zeek_json_record = {
            "ts": 1540469302.538640,
            "uid": "CGm6jB4dXK71ZDWUDh",
            "id.orig_h": "192.168.1.132",
            "id.orig_p": 58687,
            "id.resp_h": "216.239.35.4",
            "id.resp_p": 123,
            "proto": "udp",
            "service": "ntp",
            "duration": 0.114184,
            "orig_bytes": 48,
            "resp_bytes": 48,
            "conn_state": "SF",
            "history": "Dd",
            "orig_pkts": 1,
            "orig_ip_bytes": 76,
            "resp_pkts": 1,
            "resp_ip_bytes": 76,
        }

        feats = make_features(zeek_json_record)
        assert list(feats.columns) == FEATURE_COLUMNS
        assert len(feats) == 1
        assert feats.loc[0, "proto"] == "udp"
        assert feats.loc[0, "service"] == "ntp"
        assert feats.loc[0, "conn_state"] == "SF"
        assert feats.loc[0, "orig_port_cat"] == "dynamic"
        assert feats.loc[0, "resp_port_cat"] == "well_known"
        assert feats.loc[0, "is_incomplete_flow"] == 0
        assert feats.loc[0, "byte_ratio"] == 0.5
        assert feats.loc[0, "pkt_ratio"] == 0.5

    def test_safe_division_and_zeros(self):
        """Verify that zero packets or zero bytes do not result in division by zero or NaN."""
        zero_flow = {
            "proto": "tcp",
            "id.orig_p": 44444,
            "id.resp_p": 80,
            "duration": 0.0,
            "orig_bytes": 0,
            "resp_bytes": 0,
            "orig_pkts": 0,
            "resp_pkts": 0,
            "conn_state": "S0",
        }

        feats = make_features(zero_flow)
        assert feats.loc[0, "orig_bytes_per_pkt"] == 0.0
        assert feats.loc[0, "resp_bytes_per_pkt"] == 0.0
        assert feats.loc[0, "byte_ratio"] == 0.0
        assert feats.loc[0, "pkt_ratio"] == 0.0
        assert feats.loc[0, "is_incomplete_flow"] == 1
        assert not feats.isna().any().any()

    def test_incomplete_flow_detection(self):
        """Verify incomplete flow flag identifies scanning and unanswered connections."""
        test_cases = pd.DataFrame([
            {"conn_state": "S0", "duration": 0.0, "orig_bytes": 0, "resp_bytes": 0, "orig_pkts": 1, "resp_pkts": 0, "proto": "tcp"},
            {"conn_state": "REJ", "duration": 0.0, "orig_bytes": 0, "resp_bytes": 0, "orig_pkts": 1, "resp_pkts": 1, "proto": "tcp"},
            {"conn_state": "SF", "duration": 2.5, "orig_bytes": 1000, "resp_bytes": 4000, "orig_pkts": 10, "resp_pkts": 12, "proto": "tcp"},
            {"conn_state": "OTH", "duration": 0.0, "orig_bytes": 200, "resp_bytes": 0, "orig_pkts": 2, "resp_pkts": 0, "proto": "udp"},
        ])

        feats = make_features(test_cases)
        # Cases 0, 1, 3 are incomplete; Case 2 is normal established SF
        assert feats["is_incomplete_flow"].tolist() == [1, 1, 0, 1]


class TestFeaturePreprocessor:
    """Test scikit-learn integration pipeline."""

    def test_preprocessor_fit_transform(self):
        sample_data = pd.DataFrame({
            "proto": ["tcp", "udp", "icmp"],
            "service": ["http", "dns", "unknown"],
            "conn_state": ["SF", "S0", "OTH"],
            "history": ["ShAFf", "S", "unknown"],
            "id.orig_p": [80, 5353, 0],
            "id.resp_p": [8080, 53, 0],
            "duration": [1.2, 0.0, 0.5],
            "orig_bytes": [100, 0, 48],
            "resp_bytes": [200, 0, 48],
            "missed_bytes": [0, 0, 0],
            "orig_pkts": [5, 1, 1],
            "orig_ip_bytes": [250, 40, 76],
            "resp_pkts": [6, 0, 1],
            "resp_ip_bytes": [350, 0, 76],
        })

        features_df = make_features(sample_data)
        preprocessor = build_feature_preprocessor(scaling=False)

        # Fit and transform
        X_trans = preprocessor.fit_transform(features_df)
        assert isinstance(X_trans, np.ndarray)
        assert X_trans.shape[0] == 3
        assert not np.isnan(X_trans).any()

        # Test preprocessor with scaling=True
        preprocessor_scaled = build_feature_preprocessor(scaling=True)
        X_scaled = preprocessor_scaled.fit_transform(features_df)
        assert X_scaled.shape[0] == 3
        assert not np.isnan(X_scaled).any()
