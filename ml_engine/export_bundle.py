"""ml_engine/export_bundle.py - Step 18: save the model bundle and write the model card.

Proposal links: Section 3.3 step 7 ("Save the whole preprocessing pipeline together with the
trained model"), Sections 2.4 and 3.4, Table 9.

Inputs (all written by earlier steps; nothing is typed in by hand):
    ml_engine/models/rf_model.joblib                 Step 14 (pipeline, best parameters, CV scores)
    ml_engine/models/calibrated_rf_model.joblib      Step 17 (calibration fitted on grouped OOF data)
    reports/experiments/operational_thresholds.json  Step 17 (thresholds from OOF data)
    reports/experiments/step17_results.json          Step 17 (final held-out check)
    reports/experiments/evaluation_iot23.csv         Step 16 (raw model comparison on 34-1)
Outputs:
    ml_engine/models/ids_bundle_v3.joblib
    reports/experiments/model_card.md
"""

from __future__ import annotations

import argparse
import datetime
import json
import logging
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import joblib
import numpy as np
import pandas as pd
import sklearn

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine.features import CATEGORICAL_FEATURES, FEATURE_COLUMNS, NUMERICAL_FEATURES, make_features
from ml_engine.training_rows import VARIANT_FILE
from ml_engine.window_features import WINDOW_FEATURES

TARGET_CLASSES = [0, 1, 2, 3, 4]
CLASS_NAMES = ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]
CLASS_TO_NAME = dict(zip(TARGET_CLASSES, CLASS_NAMES))

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s",
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger("export_bundle")


def get_git_commit_hash() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=str(PROJECT_ROOT)).decode().strip()
    except Exception:
        return "unknown"


def build_production_bundle(rf_model_path: Path, calibrated_model_path: Path, thresholds_json_path: Path,
                            step17_results_path: Path, bundle_version: str = "v3.0.0") -> Dict[str, Any]:
    """Put the pipeline, the calibrated model, the thresholds and the measured results in one bundle."""
    base = joblib.load(rf_model_path)
    cal = joblib.load(calibrated_model_path)
    thresholds_cfg = json.loads(thresholds_json_path.read_text(encoding="utf-8"))
    step17 = json.loads(step17_results_path.read_text(encoding="utf-8"))
    ho = step17["heldout_final_check"]
    variant = {}
    if VARIANT_FILE.exists():
        variant = json.loads(VARIANT_FILE.read_text(encoding="utf-8"))

    return {
        "pipeline": base["pipeline"],
        "calibrated_model": cal["calibrated_pipeline"],
        "feature_columns": base.get("feature_columns", FEATURE_COLUMNS),
        "categorical_features": CATEGORICAL_FEATURES,
        "numerical_features": NUMERICAL_FEATURES,
        "window_features": WINDOW_FEATURES,
        "classes": TARGET_CLASSES,
        "class_names": CLASS_NAMES,
        "class_to_name": CLASS_TO_NAME,
        "operational_thresholds": thresholds_cfg["classes"],
        "threshold_rules": thresholds_cfg.get("metadata", {}).get("rules", {}),
        "example_decision_paths": step17.get("example_decision_paths", []),
        "metadata": {
            "bundle_name": "iot_camera_ids_bundle",
            "bundle_version": bundle_version,
            "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "git_commit": get_git_commit_hash(),
            "scikit_learn_version": sklearn.__version__,
            "calibration_method": cal.get("calibration_method"),
            "calibration_method_id": cal.get("calibration_method_id"),
            "hyperparameters": base.get("best_params", {}),
            "random_seed": base.get("random_seed"),
            "training_samples_count": base.get("training_samples_count"),
            "training_variant": base.get("training_variant", variant.get("chosen", "W")),
            "variant_selection": variant,
            "level_1_oof_macro_f1": base.get("overall_macro_f1"),
            "level_1_mean_fold_macro_f1": base.get("mean_fold_macro_f1"),
            "level_1_std_fold_macro_f1": base.get("std_fold_macro_f1"),
            "level_1_oof_benign_fpr": base.get("benign_fpr"),
            "level_2_heldout_scenario": step17["meta"]["heldout_scenario"],
            "level_2_heldout_flows": ho["flows"],
            "level_2_accuracy": ho["accuracy"],
            "level_2_macro_f1_5class": ho["macro_f1_5class"],
            "level_2_macro_f1_present": ho["macro_f1_present_classes"],
            "level_2_weighted_f1": ho["weighted_f1"],
            "level_2_benign_fpr_argmax": ho["benign_fpr_argmax"],
            "level_2_benign_alert_rate": ho["benign_alert_rate"],
            "level_2_benign_block_candidate_rate": ho["benign_block_candidate_rate"],
            "inference_latency_us_flow": base.get("inference_latency_us"),
            "inference_throughput_fps": base.get("throughput_fps"),
        },
    }


def verify_bundle_integrity(bundle: Dict[str, Any]) -> None:
    """Check the bundle has every part and gives valid probabilities on example Zeek records.

    The three records below are hand-made software test inputs, not measured traffic.
    """
    for k in ["pipeline", "calibrated_model", "feature_columns", "classes", "class_names",
              "operational_thresholds", "metadata"]:
        if k not in bundle:
            raise KeyError(f"Bundle is missing '{k}'")
    records = [
        {"proto": "udp", "service": "dns", "conn_state": "SF", "history": "Dd", "id.orig_p": 54123, "id.resp_p": 53,
         "duration": 0.02, "orig_bytes": 48, "resp_bytes": 128, "missed_bytes": 0, "orig_pkts": 1,
         "orig_ip_bytes": 76, "resp_pkts": 1, "resp_ip_bytes": 156},
        {"proto": "tcp", "service": "-", "conn_state": "S0", "history": "S", "id.orig_p": 44321, "id.resp_p": 80,
         "duration": 0.0, "orig_bytes": 0, "resp_bytes": 0, "missed_bytes": 0, "orig_pkts": 1,
         "orig_ip_bytes": 40, "resp_pkts": 0, "resp_ip_bytes": 0},
        {"proto": "tcp", "service": "-", "conn_state": "OTH", "history": "C", "id.orig_p": 50123, "id.resp_p": 49160,
         "duration": 0.01, "orig_bytes": 12, "resp_bytes": 0, "missed_bytes": 0, "orig_pkts": 1,
         "orig_ip_bytes": 52, "resp_pkts": 0, "resp_ip_bytes": 0},
    ]
    feats = make_features(pd.DataFrame(records))
    probs = bundle["calibrated_model"].predict_proba(feats)
    assert probs.shape == (len(records), 5), "probability matrix has the wrong shape"
    assert np.allclose(probs.sum(axis=1), 1.0, atol=1e-3), "probabilities do not add up to 1"
    logger.info("Bundle self-test passed (valid probabilities for %d example records).", len(records))


def _pct(v, d=2):
    return "—" if v is None else f"{float(v) * 100:.{d}f}%"


def _num(v, d=4):
    return "—" if v is None else f"{float(v):.{d}f}"


def generate_model_card(bundle: Dict[str, Any], step17: Dict[str, Any], output_path: Path) -> None:
    m = bundle["metadata"]
    th = bundle["operational_thresholds"]
    ho = step17["heldout_final_check"]
    hp = {k.replace("model__", ""): v for k, v in (m.get("hyperparameters") or {}).items()}
    hp_text = ", ".join(f"{k}={v!r}" for k, v in sorted(hp.items())) or "see rf_model.joblib"
    met = m["level_2_macro_f1_5class"] >= 0.85

    L: List[str] = [
        f"# Model Card: IP-Camera IDS Random Forest ({m['bundle_version']})",
        "",
        f"**Created:** {m['created_at']} · **Git commit:** `{m['git_commit']}` · **scikit-learn:** {m['scikit_learn_version']}  ",
        "**Bundle:** `ml_engine/models/ids_bundle_v3.joblib` (pipeline, calibrated model, thresholds and results together; proposal 3.3 step 7)",
        "",
        "## 1. Model",
        "",
        f"- Preprocessing: `OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1, min_frequency=50)` on {len(CATEGORICAL_FEATURES)} categorical features; {len(NUMERICAL_FEATURES)} numeric features passed through (no scaling; proposal 3.3).",
        f"- Classifier: `RandomForestClassifier({hp_text})`, chosen by random search inside grouped cross-validation (Step 14).",
        f"- Calibration: {m['calibration_method']} (Step 17; method chosen in Step 17a, see `calibration_selection.md`, D-044).",
        f"- Input: {len(bundle['feature_columns'])} features made by `ml_engine/features.py`: the 19 one-flow features of proposal Table 6, and {len(bundle['feature_columns']) - 19} **window features** (D-051, D-052; Table 6: \"rate over a time window\") made by `ml_engine/window_features.py`: what the same source did in the current 60 s (connections, distinct destinations, distinct ports, share of distinct destinations, connections to the same destination), how regularly it contacts the same destination (time since the last contact, and its change), and how many failed TCP tries it made to the same destination in the last 50–60 minutes (`pair_fail_1h`, D-052: a C&C conversation usually follows many failed tries). The same code runs in training and in the live Zeek adapter, on flows in the order Zeek writes them. Raw IP addresses, UID and file names are never inputs; IPs are only used to group flows.",
        f"- Training rows: variant **{m.get('training_variant', 'W')}** (D-051, D-052; W = all sampled rows, WC = without the `label_trusted = False` rows, WCD = WC and without the disputed rows of `config/disputed_labels.yaml`). See `variant_selection.md`.",
        "- Output: one of 5 classes (Benign, DDoS_DoS, PortScan, CnC, Malware_Download), the confidence and the model version (FR-02).",
        "",
        "## 2. Intended use",
        "",
        "- Research prototype for a small, separated IP-camera lab network (proposal 1.2).",
        "- Uses connection metadata only; it does not read packet content.",
        "- Not a certified firewall product, and it does not claim to catch every new or zero-day attack (proposal 1.2).",
        "",
        "## 3. Data",
        "",
        f"- Training: {m['training_samples_count']:,} flows sampled from 22 IoT-23 v1.0.0 scenarios (Step 12). The window features were computed on the full scenario streams (325 million flows) before sampling. The local CSV copy was checked against the official files (`reports/iot23_copy_verification.md`).",
        f"- Held-out test (Level 2): `{m['level_2_heldout_scenario']}`, {m['level_2_heldout_flows']:,} flows (no Malware_Download flows).",
        "- Local camera traffic (Level 3): **not yet measured.** The only file so far is synthetic software-test data (decision D-038); the real measurement is Step 20 in the lab.",
        "- No IoT-23 benign device is an IP camera (proposal 2.3), so results on IoT-23 do not show how the model behaves on camera traffic.",
        "",
        "## 4. Results",
        "",
        "| Level | Measure | Value | Proposal target (Table 9) |",
        "| --- | --- | ---: | --- |",
        f"| 1. Grouped CV (22 scenarios) | Out-of-fold macro-F1 | {_num(m['level_1_oof_macro_f1'])} | no target; reported |",
        f"| 1. Grouped CV | Mean fold macro-F1 ± std | {_num(m['level_1_mean_fold_macro_f1'])} ± {_num(m['level_1_std_fold_macro_f1'])} | no target; reported |",
        f"| 2. Held-out 34-1 | Macro-F1, 5 classes | {_num(m['level_2_macro_f1_5class'])} | ≥ 0.85 → **{'met' if met else 'not met'}** (34-1 has no Malware_Download flows, so this is at most 0.80) |",
        f"| 2. Held-out 34-1 | Macro-F1, classes present | {_num(m['level_2_macro_f1_present'])} | reported |",
        f"| 2. Held-out 34-1 | Accuracy / weighted F1 | {_num(m['level_2_accuracy'])} / {_num(m['level_2_weighted_f1'])} | reported (not the main result, proposal 3.4) |",
        f"| 2. Held-out 34-1 | IoT-23 benign flows predicted as attack | {_pct(m['level_2_benign_fpr_argmax'], 3)} | not the H1 measure (H1 uses local camera traffic) |",
        f"| 2. Held-out 34-1 | IoT-23 benign flows reaching a block threshold | {_pct(m['level_2_benign_block_candidate_rate'], 3)} | reported |",
        "| 3. Local camera traffic | Benign FPR | not measured yet | ≤ 5% |",
        f"| Speed | Model inference per flow (PC) | {_num(m['inference_latency_us_flow'], 2)} µs | end-to-end target: median < 2 s, p95 < 5 s (Step 37) |",
        "",
        "### Per-class results on 34-1 (deployed calibrated model, top class)",
        "",
        "| Class | Support | Precision | Recall | F1 | PR-AUC |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for n in CLASS_NAMES:
        c = ho["per_class"][n]
        L.append(f"| {n} | {c['support']:,} | {c['precision']:.4f} | {c['recall']:.4f} | {c['f1']:.4f} | {_num(c['pr_auc'])} |")
    vs = (m.get("variant_selection") or {}).get("results", {})
    if vs:
        L += [
            "",
            f"### Training variants and older models (grouped out-of-fold, {(m.get('variant_selection') or {}).get('decision', '')}; compared on the same rows)",
            "",
            "| Model | Rows | Macro-F1 | " + " | ".join(CLASS_NAMES) + " |",
            "| --- | ---: | ---: | " + " | ".join("---:" for _ in CLASS_NAMES) + " |",
        ]
        for key, r in vs.items():
            label = key.replace("compare: ", "").replace("_compared_rows", ", compared rows").replace("_own_rows", ", all its own rows")
            if isinstance(r, dict) and "macro_f1" in r:
                L.append(f"| {label} | {r['rows']:,} | {r['macro_f1']:.4f} | " + " | ".join(f"{r['f1_' + c]:.3f}" for c in CLASS_NAMES) + " |")
    L += [
        "",
        "## 5. Alert and block thresholds (Step 17; chosen from grouped out-of-fold training data only)",
        "",
        "| Class | Alert threshold | Block threshold | Action (Table 5) |",
        "| --- | ---: | ---: | --- |",
    ]
    for n in CLASS_NAMES[1:]:
        c = th[n]
        bt = "none — alert only" if c.get("active_response_threshold") is None else f"{c['active_response_threshold']:.2f}"
        L.append(f"| {n} | {c['passive_alert_threshold']:.2f} | {bt} | {c.get('action', '')} |")
    L += [
        "",
        "A block also needs every safety rule of the response policy (master switch, allowlist, local-network protection, repeats inside the time window, rule expiry). See `docs/response_policy.md`.",
        "",
        "## 6. Limits",
        "",
        "- Held-out macro-F1 is below the H1 target. Likely reasons named in proposal 1.5: domain shift between scenarios, and too few examples in some classes. The per-class table shows which classes are weak.",
        "- **Scenario 34-1 is no longer a clean test.** It was opened in Step 16 for v1 and v2, used in the PC demonstrations, and studied in progress entry 3.71 (which led to D-052). The D-052 changes were justified with training data (all 23 scenarios were counted in the study, 34-1 included), so the 34-1 score below is reported as **measured after the scenario had been seen and studied**. The clean test is the lab (Steps 20 and 35).",
        "- **File downloads: too little data for the model.** In the whole IoT-23 dataset only about 84 flows are real file downloads (`C&C-FileDownload` 53, `FileDownload` 18, `C&C-HeartBeat-FileDownload` 11, `C&C-Mirai` 2); the training sample has 67, and only 36 benign flows of the same shape. The `Malware_Download` group is almost all `Okiru` traffic (unanswered connection attempts to port 37215). So the model's Malware_Download class mostly finds Okiru-like exploit attempts. Downloads of programs are covered by a separate **rule** on Zeek's `files.log` (`core_engine/file_check.py`, D-052; alert only), which is not part of these model scores and is tested in the lab (Table 10 row 5).",
        "- The window features describe IoT-23 capture traffic. A camera that is cut off from its cloud server retries the same server at regular times, which can look like C&C. This must be checked on our own camera traffic (Step 20).",
        "- \"Benign\" in the IoT-23 malware captures means \"not labelled as an attack\". Many such flows are unanswered outbound connection attempts from the infected device (D-051, `label_trusted`).",
        "- The model has not yet been tested on our own camera traffic (Level 3).",
        "- One feature-importance value or one decision path is not proof of what caused an attack (proposal 3.4).",
        "",
    ]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(L) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser(description="Step 18: save the model bundle and write the model card.")
    ap.add_argument("--rf-model-path", type=Path, default=PROJECT_ROOT / "ml_engine/models/rf_model.joblib")
    ap.add_argument("--calibrated-model-path", type=Path, default=PROJECT_ROOT / "ml_engine/models/calibrated_rf_model.joblib")
    ap.add_argument("--thresholds-json-path", type=Path, default=PROJECT_ROOT / "reports/experiments/operational_thresholds.json")
    ap.add_argument("--step17-results-path", type=Path, default=PROJECT_ROOT / "reports/experiments/step17_results.json")
    ap.add_argument("--output-bundle-path", type=Path, default=PROJECT_ROOT / "ml_engine/models/ids_bundle_v3.joblib")
    ap.add_argument("--output-model-card-path", type=Path, default=PROJECT_ROOT / "reports/experiments/model_card.md")
    args = ap.parse_args()

    t0 = time.perf_counter()
    bundle = build_production_bundle(args.rf_model_path, args.calibrated_model_path, args.thresholds_json_path,
                                     args.step17_results_path)
    verify_bundle_integrity(bundle)
    args.output_bundle_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, args.output_bundle_path, compress=3)
    step17 = json.loads(args.step17_results_path.read_text(encoding="utf-8"))
    generate_model_card(bundle, step17, args.output_model_card_path)
    logger.info("Step 18 finished in %.1f s (bundle %.1f MB).", time.perf_counter() - t0,
                args.output_bundle_path.stat().st_size / 1e6)


if __name__ == "__main__":
    main()
