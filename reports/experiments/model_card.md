# Model Card: IP-Camera IDS Random Forest (v1.2.0)

**Created:** 2026-11-09 10:56:34 · **Git commit:** `94fff92` · **scikit-learn:** 1.7.2  
**Bundle:** `ml_engine/models/ids_bundle_v1.joblib` (pipeline, calibrated model, thresholds and results together; proposal 3.3 step 7)

## 1. Model

- Preprocessing: `OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1, min_frequency=50)` on 6 categorical features; 13 numeric features passed through (no scaling; proposal 3.3).
- Classifier: `RandomForestClassifier(class_weight='balanced', max_depth=18, max_features='sqrt', min_samples_leaf=4, min_samples_split=5, n_estimators=100)`, chosen by random search inside grouped cross-validation (Step 14).
- Calibration: one temperature on the log-probabilities (softmax); keeps the raw top class; fitted on grouped out-of-fold probabilities (method chosen in Step 17a: D-044 rule, D-045 final choice) (Step 17; method chosen in Step 17a, see `calibration_selection.md`, D-044).
- Input: the 19 flow features made by `ml_engine/features.py` (proposal Table 6). Raw IP addresses, UID and file names are never inputs.
- Output: one of 5 classes (Benign, DDoS_DoS, PortScan, CnC, Malware_Download), the confidence and the model version (FR-02).

## 2. Intended use

- Research prototype for a small, separated IP-camera lab network (proposal 1.2).
- Uses connection metadata only; it does not read packet content.
- Not a certified firewall product, and it does not claim to catch every new or zero-day attack (proposal 1.2).

## 3. Data

- Training: 1,384,070 flows sampled from 22 IoT-23 v1.0.0 scenarios (Step 12). The local CSV copy was checked against the official files (`reports/iot23_copy_verification.md`).
- Held-out test (Level 2): `CTU-IoT-Malware-Capture-34-1`, 23,145 flows (no Malware_Download flows).
- Local camera traffic (Level 3): **not yet measured.** The only file so far is synthetic software-test data (decision D-038); the real measurement is Step 20 in the lab.
- No IoT-23 benign device is an IP camera (proposal 2.3), so results on IoT-23 do not show how the model behaves on camera traffic.

## 4. Results

| Level | Measure | Value | Proposal target (Table 9) |
| --- | --- | ---: | --- |
| 1. Grouped CV (22 scenarios) | Out-of-fold macro-F1 | 0.3422 | no target; reported |
| 1. Grouped CV | Mean fold macro-F1 ± std | 0.3353 ± 0.1704 | no target; reported |
| 2. Held-out 34-1 | Macro-F1, 5 classes | 0.4530 | ≥ 0.85 → **not met** |
| 2. Held-out 34-1 | Macro-F1, classes present | 0.5662 | reported |
| 2. Held-out 34-1 | Accuracy / weighted F1 | 0.8063 / 0.8285 | reported (not the main result, proposal 3.4) |
| 2. Held-out 34-1 | IoT-23 benign flows predicted as attack | 5.148% | not the H1 measure (H1 uses local camera traffic) |
| 2. Held-out 34-1 | IoT-23 benign flows reaching a block threshold | 2.236% | reported |
| 3. Local camera traffic | Benign FPR | not measured yet | ≤ 5% |
| Speed | Model inference per flow (PC) | 4.66 µs | end-to-end target: median < 2 s, p95 < 5 s (Step 37) |

### Per-class results on 34-1 (deployed calibrated model, top class)

| Class | Support | Precision | Recall | F1 | PR-AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Benign | 1,923 | 0.4997 | 0.9485 | 0.6546 | 0.9479 |
| DDoS_DoS | 14,394 | 0.9999 | 0.9908 | 0.9953 | 0.9976 |
| PortScan | 122 | 0.0424 | 0.9426 | 0.0812 | 0.8601 |
| CnC | 6,706 | 0.9781 | 0.3671 | 0.5339 | 0.9859 |
| Malware_Download | 0 | 0.0000 | 0.0000 | 0.0000 | — |

## 5. Alert and block thresholds (Step 17; chosen from grouped out-of-fold training data only)

| Class | Alert threshold | Block threshold | Action (Table 5) |
| --- | ---: | ---: | --- |
| DDoS_DoS | 0.33 | none — alert only | drop_source |
| PortScan | 0.30 | 0.30 | drop_source |
| CnC | 0.39 | 0.39 | block_destination_or_isolate |
| Malware_Download | 0.30 | none — alert only | block_by_direction |

A block also needs every safety rule of the response policy (master switch, allowlist, local-network protection, repeats inside the time window, rule expiry). See `docs/response_policy.md`.

## 6. Limits

- Held-out macro-F1 is below the H1 target. Likely reasons named in proposal 1.5: domain shift between scenarios, and too few examples in some classes. The per-class table shows which classes are weak.
- Scenario 34-1 was opened in Step 16 before the Step 17 redo. Nothing in Step 17 was chosen from it, but this is reported as a limitation.
- The model has not yet been tested on our own camera traffic (Level 3).
- One feature-importance value or one decision path is not proof of what caused an attack (proposal 3.4).

