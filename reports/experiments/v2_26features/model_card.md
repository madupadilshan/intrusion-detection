# Model Card: IP-Camera IDS Random Forest (v2.0.0)

**Created:** 2026-11-10 18:16:28 · **Git commit:** `bce3faa` · **scikit-learn:** 1.7.2  
**Bundle:** `ml_engine/models/ids_bundle_v2.joblib` (pipeline, calibrated model, thresholds and results together; proposal 3.3 step 7)

## 1. Model

- Preprocessing: `OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1, min_frequency=50)` on 6 categorical features; 20 numeric features passed through (no scaling; proposal 3.3).
- Classifier: `RandomForestClassifier(class_weight='balanced', max_depth=12, max_features='log2', min_samples_leaf=1, min_samples_split=5, n_estimators=100)`, chosen by random search inside grouped cross-validation (Step 14).
- Calibration: raw Random Forest probabilities (no calibration); fitted on grouped out-of-fold probabilities (method chosen in Step 17a: D-044 rule, D-045 final choice) (Step 17; method chosen in Step 17a, see `calibration_selection.md`, D-044).
- Input: 26 features made by `ml_engine/features.py`: the 19 one-flow features of proposal Table 6, and 7 **window features** (D-051; Table 6: "rate over a time window") made by `ml_engine/window_features.py`: what the same source did in the current 60 s (connections, distinct destinations, distinct ports, share of distinct destinations, connections to the same destination) and how regularly it contacts the same destination (time since the last contact, and its change). The same code runs in training and in the live Zeek adapter, on flows in the order Zeek writes them. Raw IP addresses, UID and file names are never inputs; IPs are only used to group flows.
- Training rows: variant **WC** (D-051; W = all sampled rows, WC = without the `label_trusted = False` rows). See `variant_selection.md`.
- Output: one of 5 classes (Benign, DDoS_DoS, PortScan, CnC, Malware_Download), the confidence and the model version (FR-02).

## 2. Intended use

- Research prototype for a small, separated IP-camera lab network (proposal 1.2).
- Uses connection metadata only; it does not read packet content.
- Not a certified firewall product, and it does not claim to catch every new or zero-day attack (proposal 1.2).

## 3. Data

- Training: 1,184,004 flows sampled from 22 IoT-23 v1.0.0 scenarios (Step 12). The window features were computed on the full scenario streams (325 million flows) before sampling. The local CSV copy was checked against the official files (`reports/iot23_copy_verification.md`).
- Held-out test (Level 2): `CTU-IoT-Malware-Capture-34-1`, 23,145 flows (no Malware_Download flows).
- Local camera traffic (Level 3): **not yet measured.** The only file so far is synthetic software-test data (decision D-038); the real measurement is Step 20 in the lab.
- No IoT-23 benign device is an IP camera (proposal 2.3), so results on IoT-23 do not show how the model behaves on camera traffic.

## 4. Results

| Level | Measure | Value | Proposal target (Table 9) |
| --- | --- | ---: | --- |
| 1. Grouped CV (22 scenarios) | Out-of-fold macro-F1 | 0.7009 | no target; reported |
| 1. Grouped CV | Mean fold macro-F1 ± std | 0.6734 ± 0.2114 | no target; reported |
| 2. Held-out 34-1 | Macro-F1, 5 classes | 0.6337 | ≥ 0.85 → **not met** (34-1 has no Malware_Download flows, so this is at most 0.80) |
| 2. Held-out 34-1 | Macro-F1, classes present | 0.7921 | reported |
| 2. Held-out 34-1 | Accuracy / weighted F1 | 0.9148 / 0.9215 | reported (not the main result, proposal 3.4) |
| 2. Held-out 34-1 | IoT-23 benign flows predicted as attack | 5.564% | not the H1 measure (H1 uses local camera traffic) |
| 2. Held-out 34-1 | IoT-23 benign flows reaching a block threshold | 4.264% | reported |
| 3. Local camera traffic | Benign FPR | not measured yet | ≤ 5% |
| Speed | Model inference per flow (PC) | 6.19 µs | end-to-end target: median < 2 s, p95 < 5 s (Step 37) |

### Per-class results on 34-1 (deployed calibrated model, top class)

| Class | Support | Precision | Recall | F1 | PR-AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Benign | 1,923 | 0.5224 | 0.9444 | 0.6727 | 0.9037 |
| DDoS_DoS | 14,394 | 0.9999 | 0.9901 | 0.9949 | 0.9999 |
| PortScan | 122 | 0.5066 | 0.9508 | 0.6610 | 0.3239 |
| CnC | 6,706 | 0.9637 | 0.7441 | 0.8398 | 0.9669 |
| Malware_Download | 0 | 0.0000 | 0.0000 | 0.0000 | — |

### Old model (v1, 19 features) compared with this model (training scenarios, grouped out-of-fold)

| Model | Rows | Macro-F1 | Benign | DDoS_DoS | PortScan | CnC | Malware_Download |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| v1, 19 features, all rows | 1,384,070 | 0.3422 | 0.447 | 0.003 | 0.464 | 0.167 | 0.629 |
| W, 26 features, all rows | 1,384,070 | 0.6041 | 0.518 | 0.773 | 0.502 | 0.509 | 0.719 |
| v1, 19 features, trusted rows | 1,184,004 | 0.3730 | 0.474 | 0.003 | 0.495 | 0.206 | 0.687 |
| W, 26 features, trusted rows | 1,184,004 | 0.6465 | 0.588 | 0.773 | 0.561 | 0.515 | 0.795 |
| WC, 26 features, trusted rows | 1,184,004 | 0.7009 | 0.747 | 0.786 | 0.600 | 0.751 | 0.620 |

## 5. Alert and block thresholds (Step 17; chosen from grouped out-of-fold training data only)

| Class | Alert threshold | Block threshold | Action (Table 5) |
| --- | ---: | ---: | --- |
| DDoS_DoS | 0.30 | none — alert only | drop_source |
| PortScan | 0.30 | 0.95 | drop_source |
| CnC | 0.30 | 0.30 | block_destination_or_isolate |
| Malware_Download | 0.30 | none — alert only | block_by_direction |

A block also needs every safety rule of the response policy (master switch, allowlist, local-network protection, repeats inside the time window, rule expiry). See `docs/response_policy.md`.

## 6. Limits

- Held-out macro-F1 is below the H1 target. Likely reasons named in proposal 1.5: domain shift between scenarios, and too few examples in some classes. The per-class table shows which classes are weak.
- Scenario 34-1 was first opened in Step 16 for the v1 model. For this model (D-051) nothing was chosen from it: the features, the variant and the thresholds were chosen from training data only, and 34-1 was used once at the end. Its score is still reported as measured after the scenario had been seen once.
- **File downloads are not learned.** In the whole IoT-23 dataset only about 84 flows are real file downloads (`C&C-FileDownload` 53, `FileDownload` 18, `C&C-HeartBeat-FileDownload` 11, `C&C-Mirai` 2). The `Malware_Download` group is almost all `Okiru` traffic: unanswered connection attempts to port 37215. So this class finds Okiru-like exploit attempts, not file transfers (proposal Table 10, row 5: "we claim nothing if the model cannot generalise").
- The window features describe IoT-23 capture traffic. A camera that is cut off from its cloud server retries the same server at regular times, which can look like C&C. This must be checked on our own camera traffic (Step 20).
- "Benign" in the IoT-23 malware captures means "not labelled as an attack". Many such flows are unanswered outbound connection attempts from the infected device (D-051, `label_trusted`).
- The model has not yet been tested on our own camera traffic (Level 3).
- One feature-importance value or one decision path is not proof of what caused an attack (proposal 3.4).

