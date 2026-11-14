"""ml_engine/retrain_with_lab.py - model v3.2.0: the v3.1.0 Random Forest retrained with lab rows.

Why: IoT-23 has only about 84 real file-download flows (model card section 6), so v3.1.0 predicts
"Benign" for a program download in the lab. This script adds labelled rows captured in the lab:
  - Malware_Download: connections whose Zeek uid is in files.log with a program file type
    (made by data/local/lab_training/, see build step in the progress notes)
  - Benign: normal lab traffic (camera <-> cloud, NVR stream, admin page, DNS/NTP)
and fits the SAME pipeline (same encoder, same Random Forest hyperparameters, same seed) on the
v3.1.0 training rows (variant of variant_selection.json) plus these rows.

What it keeps from v3.1.0: features, hyperparameters, thresholds (operational_thresholds), the
"no calibration" choice. What it measures again: the held-out scenario 34-1 (Level 2).
The lab rows are a new data source; the downloads used for training must not be reused as test
data (test with new download runs).

Output: ml_engine/models/ids_bundle_v3_2.joblib (v3.1.0 stays in ml_engine/models/ids_bundle_v3.joblib).
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.base import clone
from sklearn.metrics import accuracy_score, f1_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine.calibration import OOFCalibratedClassifier  # noqa: E402
from ml_engine.features import FEATURE_COLUMNS  # noqa: E402
from ml_engine.training_rows import chosen_variant, load_training_frame  # noqa: E402

MODELS = PROJECT_ROOT / "ml_engine" / "models"
CLASS_NAMES = ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]


def heldout_scores(model, path: Path) -> dict:
    ho = pd.read_parquet(path)
    y = ho["label_idx"].to_numpy()
    pred = np.argmax(model.predict_proba(ho[FEATURE_COLUMNS]), axis=1)
    present = sorted(set(y.tolist()))
    per = f1_score(y, pred, labels=list(range(5)), average=None, zero_division=0)
    benign = y == 0
    return {
        "flows": int(len(y)),
        "accuracy": float(accuracy_score(y, pred)),
        "macro_f1_5class": float(f1_score(y, pred, labels=list(range(5)), average="macro", zero_division=0)),
        "macro_f1_present_classes": float(f1_score(y, pred, labels=present, average="macro", zero_division=0)),
        "weighted_f1": float(f1_score(y, pred, average="weighted", zero_division=0)),
        "benign_fpr_argmax": float(np.mean(pred[benign] != 0)) if benign.any() else None,
        "per_class_f1": {CLASS_NAMES[i]: round(float(per[i]), 4) for i in range(5)},
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base-bundle", type=Path, default=MODELS / "ids_bundle_v3.joblib")
    ap.add_argument("--lab-rows", type=Path, nargs="+",
                    default=[PROJECT_ROOT / "data" / "local" / "lab_training" / "lab_rows_v3_2.parquet"])
    ap.add_argument("--heldout", type=Path, default=PROJECT_ROOT / "data" / "processed" / "heldout" / "held_out_test.parquet")
    ap.add_argument("--weight-lab-download", type=float, default=100.0)
    ap.add_argument("--weight-lab-benign", type=float, default=20.0)
    ap.add_argument("--weight-lab-portscan", type=float, default=40.0)
    ap.add_argument("--out", type=Path, default=MODELS / "ids_bundle_v3_2.joblib")
    ap.add_argument("--version", default="v3.2.0")
    args = ap.parse_args()

    base = joblib.load(args.base_bundle)
    variant = chosen_variant()
    train = load_training_frame(columns=FEATURE_COLUMNS + ["label_idx"])
    lab = pd.concat([pd.read_parquet(p) for p in args.lab_rows], ignore_index=True)
    X = pd.concat([train[FEATURE_COLUMNS], lab[FEATURE_COLUMNS]], ignore_index=True)
    y = np.concatenate([train["label_idx"].to_numpy(), lab["label_idx"].to_numpy()]).astype(int)
    # per-class weight for the lab rows (label_idx -> weight); other classes default to benign weight
    lab_weight = {4: args.weight_lab_download, 0: args.weight_lab_benign, 2: args.weight_lab_portscan}
    lab_idx = lab["label_idx"].to_numpy()
    w = np.concatenate([
        np.ones(len(train)),
        np.array([lab_weight.get(int(i), args.weight_lab_benign) for i in lab_idx], dtype=float),
    ])
    lab_counts = lab["class_name"].value_counts().to_dict()
    print(f"training rows: IoT-23 {len(train):,} (variant {variant}) + lab {len(lab):,} {lab_counts}", flush=True)

    pipe = clone(base["calibrated_model"].base_pipeline)
    t = time.perf_counter()
    pipe.fit(X, y, model__sample_weight=w)
    print(f"fitted in {time.perf_counter() - t:.0f} s", flush=True)
    cal = base["calibrated_model"]
    model = OOFCalibratedClassifier(pipe, cal.method, cal.params, cal.classes_)

    ho = heldout_scores(model, args.heldout)
    ho_old = heldout_scores(base["calibrated_model"], args.heldout)
    print("held-out 34-1  v3.1.0:", json.dumps({k: ho_old[k] for k in ("macro_f1_present_classes", "macro_f1_5class", "accuracy")}))
    print("held-out 34-1 ", args.version + ":", json.dumps({k: ho[k] for k in ("macro_f1_present_classes", "macro_f1_5class", "accuracy")}))
    print("per-class F1", args.version + ":", ho["per_class_f1"])

    bundle = dict(base)
    bundle["pipeline"] = pipe
    bundle["calibrated_model"] = model
    m = dict(base["metadata"])
    m.update({
        "bundle_version": args.version,
        "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "based_on": base["metadata"].get("bundle_version"),
        "training_extra_lab_rows": {k: int(v) for k, v in lab_counts.items()},
        "training_extra_lab_weights": {"Malware_Download": args.weight_lab_download, "Benign": args.weight_lab_benign},
        "training_samples_count": int(len(X)),
        "level_2_accuracy": ho["accuracy"],
        "level_2_macro_f1_5class": ho["macro_f1_5class"],
        "level_2_macro_f1_present": ho["macro_f1_present_classes"],
        "level_2_weighted_f1": ho["weighted_f1"],
        "level_2_benign_fpr_argmax": ho["benign_fpr_argmax"],
        "level_2_per_class_f1": ho["per_class_f1"],
        "level_1_note": "level_1_* values are from the v3.1.0 grouped cross-validation (not re-run for this version)",
        "thresholds_note": "operational_thresholds copied from v3.1.0 (not re-derived)",
    })
    bundle["metadata"] = m
    joblib.dump(bundle, args.out, compress=3)
    print(f"saved {args.out} ({args.out.stat().st_size / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
