"""
tests/unit/test_detector.py - Unit Tests for Intrusion Detector (Step 26).
"""

import pytest
import numpy as np
from pathlib import Path
from unittest.mock import MagicMock

from core_engine.detector import Detector, DetectionResult, DEFAULT_BUNDLE_PATH


def test_detector_initialization_default():
    """Verify detector loads the default production bundle correctly."""
    detector = Detector()
    info = detector.get_model_info()

    assert str(info["model_version"]).startswith("v1.")
    assert "Benign" in info["classes"]
    assert "DDoS_DoS" in info["classes"]
    assert "PortScan" in info["classes"]
    assert "CnC" in info["classes"]
    assert "Malware_Download" in info["classes"]
    assert info["features_count"] == 19
    assert info["is_calibrated"] is True


def test_detector_missing_bundle_raises_error():
    """Verify detector raises FileNotFoundError when bundle does not exist."""
    fake_path = Path("ml_engine/models/non_existent_bundle.joblib")
    with pytest.raises(FileNotFoundError) as exc_info:
        Detector(bundle_path=fake_path)
    assert "Model bundle not found" in str(exc_info.value)


def test_detector_empty_flow_list():
    """Verify passing empty list returns empty list immediately."""
    detector = Detector()
    results = detector.detect_flows([])
    assert results == []


def test_detector_benign_inference():
    """Verify inference on a typical benign HTTP flow returns calibrated probabilities."""
    detector = Detector()

    benign_flow = {
        "ts": 1700000000.123,
        "uid": "CHttpFlow01",
        "proto": "tcp",
        "service": "http",
        "conn_state": "SF",
        "history": "ShADadfF",
        "id.orig_h": "192.168.50.88",
        "id.orig_p": 49152,
        "id.resp_h": "192.168.50.10",
        "id.resp_p": 80,
        "duration": 1.25,
        "orig_bytes": 240,
        "resp_bytes": 1600,
        "missed_bytes": 0,
        "orig_pkts": 6,
        "orig_ip_bytes": 480,
        "resp_pkts": 8,
        "resp_ip_bytes": 1920,
        "traffic_direction": "inbound",
    }

    result = detector.detect_single(benign_flow)

    assert isinstance(result, DetectionResult)
    assert result.flow_id == "CHttpFlow01"
    assert result.predicted_class == "Benign"
    # Confidence is the calibrated top-class probability. Its size depends on the trained model,
    # so the test checks that it is valid and equals the largest probability (not a fixed value).
    assert 0.0 < result.confidence <= 1.0
    assert result.confidence == pytest.approx(max(result.probabilities.values()), abs=1e-6)
    assert str(result.model_version).startswith("v1.")

    # Probabilities must sum to ~1.0
    prob_sum = sum(result.probabilities.values())
    assert pytest.approx(prob_sum, abs=1e-4) == 1.0

    # Features must contain 19 keys
    assert len(result.features) == 19
    assert "duration" in result.features
    assert "orig_port_cat" in result.features
    assert "resp_port_cat" in result.features


def test_detector_scan_inference():
    """Verify inference on a classic PortScan probe flow."""
    detector = Detector()

    scan_flow = {
        "ts": 1700000005.456,
        "uid": "CScanFlow01",
        "proto": "tcp",
        "service": "-",
        "conn_state": "S0",
        "history": "S",
        "id.orig_h": "10.10.10.99",
        "id.orig_p": 60123,
        "id.resp_h": "192.168.50.15",
        "id.resp_p": 23,
        "duration": 0.001,
        "orig_bytes": 0,
        "resp_bytes": 0,
        "missed_bytes": 0,
        "orig_pkts": 1,
        "orig_ip_bytes": 40,
        "resp_pkts": 0,
        "resp_ip_bytes": 0,
        "traffic_direction": "inbound",
    }

    result = detector.detect_single(scan_flow)

    assert result.flow_id == "CScanFlow01"
    assert result.predicted_class == "PortScan"
    # The confidence size depends on the trained model and its calibration; check it is the top probability.
    assert result.confidence == pytest.approx(max(result.probabilities.values()), abs=1e-6)
    assert "PortScan" in result.probabilities


def test_detector_batch_processing():
    """Verify detector processes multiple flows in a single vectorized micro-batch."""
    detector = Detector()

    flows = [
        {
            "uid": f"CFlow_{i}",
            "proto": "tcp",
            "service": "http" if i % 2 == 0 else "-",
            "conn_state": "SF" if i % 2 == 0 else "S0",
            "history": "ShADadfF" if i % 2 == 0 else "S",
            "id.orig_h": "192.168.50.88",
            "id.orig_p": 49000 + i,
            "id.resp_h": "192.168.50.10",
            "id.resp_p": 80 if i % 2 == 0 else 22,
            "duration": 1.0 if i % 2 == 0 else 0.002,
            "orig_bytes": 100 if i % 2 == 0 else 0,
            "resp_bytes": 500 if i % 2 == 0 else 0,
            "missed_bytes": 0,
            "orig_pkts": 4 if i % 2 == 0 else 1,
            "orig_ip_bytes": 200 if i % 2 == 0 else 40,
            "resp_pkts": 4 if i % 2 == 0 else 0,
            "resp_ip_bytes": 600 if i % 2 == 0 else 0,
        }
        for i in range(5)
    ]

    results = detector.detect_flows(flows)
    assert len(results) == 5
    for idx, r in enumerate(results):
        assert r.flow_id == f"CFlow_{idx}"
        assert r.detect_ts > 0
        assert len(r.probabilities) == 5


def test_detector_with_mock_bundle():
    """Verify detector operates properly when initialized with an in-memory mock bundle."""
    mock_pipeline = MagicMock()
    mock_pipeline.predict_proba.return_value = np.array([[0.1, 0.8, 0.05, 0.03, 0.02]])

    mock_bundle = {
        "calibrated_model": mock_pipeline,
        "class_names": ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"],
        "feature_columns": ["proto", "duration"],
        "metadata": {"bundle_version": "v9.9.9"},
    }

    det = Detector(bundle_dict=mock_bundle)
    assert det.model_version == "v9.9.9"

    res = det.detect_single({"proto": "tcp", "duration": 0.5})
    assert res.predicted_class == "DDoS_DoS"
    assert res.confidence == 0.8
    assert res.model_version == "v9.9.9"

