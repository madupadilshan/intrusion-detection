#!/usr/bin/env python3
"""
core_engine/detector.py - Real-Time Machine Learning Intrusion Detector (Step 26).
===================================================================================

Governing Standards & Requirements:
- Group 03 Research Proposal: Figures 2 & 3 ("Intrusion Detection Pipeline");
  Sections 3.4, 3.6; Requirements Table 7: FR-01, FR-02.
- Step-by-Step Guide: Step 26 ("Build the detector and decision engine").
- Key Principles:
  1. Load model bundle ONCE at initialization (low memory footprint, fast startup).
  2. Zero Training-Serving Skew: Extracts identical 19 features via `ml_engine.features.make_features()`.
  3. Batch and single-flow inference producing calibrated probability distributions.
  4. Returns standardized `DetectionResult` with predicted class, confidence, and model metadata.
"""

from __future__ import annotations

import logging
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import joblib
import numpy as np
import pandas as pd

from ml_engine.features import FEATURE_COLUMNS, make_features

logger = logging.getLogger("core_engine.detector")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_BUNDLE_PATH = PROJECT_ROOT / "ml_engine" / "models" / "ids_bundle_v1.joblib"


@dataclass
class DetectionResult:
    """Standardized detection result container for a single network flow."""

    flow_id: Optional[str] = None
    predicted_class: str = "Benign"
    predicted_class_idx: int = 0
    confidence: float = 0.0
    probabilities: Dict[str, float] = field(default_factory=dict)
    model_version: str = "v1.0.0"
    raw_flow: Dict[str, Any] = field(default_factory=dict)
    features: Dict[str, Any] = field(default_factory=dict)
    detect_ts: float = field(default_factory=time.time)

    def to_dict(self) -> Dict[str, Any]:
        """Convert detection result to serializable dictionary."""
        d = asdict(self)
        return d


class Detector:
    """
    Real-Time Machine Learning Intrusion Detector.

    Caches the unified production model bundle (`ids_bundle_v1.joblib`) and executes
    calibrated inference across streaming flow micro-batches.
    """

    def __init__(
        self,
        bundle_path: Optional[Union[str, Path]] = None,
        bundle_dict: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the detector.

        Args:
            bundle_path: Path to serialized `ids_bundle_v1.joblib`. If None, uses default.
            bundle_dict: Pre-loaded bundle dictionary (used for unit testing with mocks).
        """
        self.bundle_path = Path(bundle_path) if bundle_path else DEFAULT_BUNDLE_PATH
        self._bundle: Dict[str, Any] = {}
        self.model: Any = None
        self.class_names: List[str] = []
        self.feature_columns: List[str] = []
        self.operational_thresholds: Dict[str, Any] = {}
        self.decision_rules: List[Dict[str, Any]] = []
        self.model_version: str = "v1.0.0"

        if bundle_dict is not None:
            self._load_from_dict(bundle_dict)
        else:
            self._load_from_path(self.bundle_path)

    def _load_from_path(self, path: Path) -> None:
        """Load and unpack the model bundle from disk."""
        if not path.is_file():
            raise FileNotFoundError(
                f"Model bundle not found at: {path}. "
                "Ensure Step 18 export_bundle.py has executed successfully."
            )
        logger.info("Loading production model bundle from: %s", path)
        bundle = joblib.load(path)
        if not isinstance(bundle, dict):
            raise TypeError(f"Invalid bundle format at {path}: expected dict, got {type(bundle)}.")
        self._load_from_dict(bundle)

    def _load_from_dict(self, bundle: Dict[str, Any]) -> None:
        """Unpack components from bundle dictionary."""
        self._bundle = bundle

        # Preferred model: calibrated_model wrapper; fallback: base pipeline
        if "calibrated_model" in bundle and bundle["calibrated_model"] is not None:
            self.model = bundle["calibrated_model"]
        elif "pipeline" in bundle and bundle["pipeline"] is not None:
            self.model = bundle["pipeline"]
        else:
            raise KeyError("Bundle does not contain 'calibrated_model' or 'pipeline'.")

        self.class_names = bundle.get(
            "class_names", ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]
        )
        self.feature_columns = bundle.get("feature_columns", FEATURE_COLUMNS)
        self.operational_thresholds = bundle.get("operational_thresholds", {})
        self.decision_rules = bundle.get("decision_rules", [])

        metadata = bundle.get("metadata", {})
        self.model_version = metadata.get("bundle_version", "v1.0.0")

        logger.info(
            "Detector loaded successfully. Model version: %s, Classes: %s, Features: %d",
            self.model_version,
            self.class_names,
            len(self.feature_columns),
        )

    def detect_flows(self, flows: List[Dict[str, Any]]) -> List[DetectionResult]:
        """
        Execute intrusion detection across a batch of raw or enriched Zeek flows.

        Args:
            flows: List of Zeek connection flow records (dictionaries).

        Returns:
            List of `DetectionResult` objects corresponding to each input flow.
        """
        if not flows:
            return []

        detect_ts = time.time()

        # Step 1: Zero training-serving skew feature extraction (Table 6)
        features_df = make_features(flows)

        # Step 2: Calibrated probability inference
        # model.predict_proba returns ndarray of shape (n_samples, n_classes)
        try:
            proba_matrix = self.model.predict_proba(features_df)
        except Exception as e:
            logger.error("Inference failed on flow batch: %s", e)
            raise RuntimeError(f"Detector inference error: {e}") from e

        results: List[DetectionResult] = []
        n_classes = len(self.class_names)

        for idx, flow in enumerate(flows):
            probs_row = proba_matrix[idx]
            max_idx = int(np.argmax(probs_row))
            confidence = float(probs_row[max_idx])
            pred_class = (
                self.class_names[max_idx] if max_idx < n_classes else f"Class_{max_idx}"
            )

            # Map class names to individual probabilities
            probs_dict: Dict[str, float] = {}
            for c_idx, c_name in enumerate(self.class_names):
                if c_idx < len(probs_row):
                    probs_dict[c_name] = float(round(probs_row[c_idx], 6))

            # Extract flow UID if available
            flow_id = str(flow.get("uid") or flow.get("flow_id") or f"flow_{int(detect_ts * 1000)}_{idx}")

            # Extract features row as clean dict
            features_dict = features_df.iloc[idx].to_dict()

            res = DetectionResult(
                flow_id=flow_id,
                predicted_class=pred_class,
                predicted_class_idx=max_idx,
                confidence=float(round(confidence, 6)),
                probabilities=probs_dict,
                model_version=self.model_version,
                raw_flow=flow,
                features=features_dict,
                detect_ts=detect_ts,
            )
            results.append(res)

        return results

    def detect_single(self, flow: Dict[str, Any]) -> DetectionResult:
        """
        Convenience method to execute detection on a single flow.

        Args:
            flow: Single Zeek flow dictionary.

        Returns:
            `DetectionResult` for the flow.
        """
        results = self.detect_flows([flow])
        if not results:
            raise ValueError("Failed to evaluate single flow.")
        return results[0]

    def get_model_info(self) -> Dict[str, Any]:
        """Return diagnostic metadata about the loaded detector."""
        return {
            "model_version": self.model_version,
            "classes": self.class_names,
            "features_count": len(self.feature_columns),
            "bundle_path": str(self.bundle_path),
            "is_calibrated": hasattr(self.model, "calibrated_classifiers_") or "Calibrated" in type(self.model).__name__,
            "operational_thresholds_count": len(self.operational_thresholds),
        }

