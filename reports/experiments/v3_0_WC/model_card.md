# Model Card: IP-Camera IDS Random Forest (v3.0.0)

**Created:** 2026-11-10 23:24:48 · **Git commit:** `bce3faa` · **scikit-learn:** 1.7.2  
**Bundle:** `ml_engine/models/ids_bundle_v3.joblib` (pipeline, calibrated model, thresholds and results together; proposal 3.3 step 7)

## 1. Model

- Preprocessing: `OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1, min_frequency=50)` on 6 categorical features; 21 numeric features passed through (no scaling; proposal 3.3).
- Classifier: `RandomForestClassifier(class_weight='balanced', max_depth=12, max_features='log2', min_samples_leaf=1, min_samples_split=5, n_estimators=100)`, chosen by random search inside grouped cross-validation (Step 14).
- Calibration: raw Random Forest probabilities (no calibration); fitted on grouped out-of-fold probabilities (method chosen in Step 17a: D-044 rule, D-045 final choice) (Step 17; method chosen in Step 17a, see `calibration_selection.md`, D-044).
- Input: 27 features made by `ml_engine/features.py`: the 19 one-flow features of proposal Table 6, and 8 **window features** (D-051, D-052; Table 6: "rate over a time window") made by `ml_engine/window_features.py`: what the same source did in the current 60 s (connections, distinct destinations, distinct ports, share of distinct destinations, connections to the same destination), how regularly it contacts the same destination (time since the last contact, and its change), and how many failed TCP tries it made to the same destination in the last 50–60 minutes (`pair_fail_1h`, D-052: a C&C conversation usually follows many failed tries). The same code runs in training and in the live Zeek adapter, on flows in the order Zeek writes them. Raw IP addresses, UID and file names are never inputs; IPs are only used to group flows.
- Training rows: variant **WC** (D-051, D-052; W = all sampled rows, WC = without the `label_trusted = False` rows, WCD = WC and without the disputed rows of `config/disputed_labels.yaml`). See `variant_selection.md`.
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
| 1. Grouped CV (22 scenarios) | Out-of-fold macro-F1 | 0.7084 | no target; reported |
| 1. Grouped CV | Mean fold macro-F1 ± std | 0.6719 ± 0.2045 | no target; reported |
| 2. Held-out 34-1 | Macro-F1, 5 classes | 0.6596 | ≥ 0.85 → **not met** (34-1 has no Malware_Download flows, so this is at most 0.80) |
| 2. Held-out 34-1 | Macro-F1, classes present | 0.8244 | reported |
| 2. Held-out 34-1 | Accuracy / weighted F1 | 0.9158 / 0.9222 | reported (not the main result, proposal 3.4) |
| 2. Held-out 34-1 | IoT-23 benign flows predicted as attack | 5.668% | not the H1 measure (H1 uses local camera traffic) |
| 2. Held-out 34-1 | IoT-23 benign flows reaching a block threshold | 4.836% | reported |
| 3. Local camera traffic | Benign FPR | not measured yet | ≤ 5% |
| Speed | Model inference per flow (PC) | 4.81 µs | end-to-end target: median < 2 s, p95 < 5 s (Step 37) |

### Per-class results on 34-1 (deployed calibrated model, top class)

| Class | Support | Precision | Recall | F1 | PR-AUC |
| --- | ---: | ---: | ---: | ---: | ---: |
| Benign | 1,923 | 0.5229 | 0.9433 | 0.6728 | 0.9590 |
| DDoS_DoS | 14,394 | 0.9999 | 0.9895 | 0.9947 | 0.9999 |
| PortScan | 122 | 0.7078 | 0.8934 | 0.7899 | 0.4396 |
| CnC | 6,706 | 0.9552 | 0.7502 | 0.8404 | 0.9675 |
| Malware_Download | 0 | 0.0000 | 0.0000 | 0.0000 | — |

### Training variants and older models (grouped out-of-fold, D-052; compared on the same rows)

| Model | Rows | Macro-F1 | Benign | DDoS_DoS | PortScan | CnC | Malware_Download |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| WC, compared rows | 1,182,984 | 0.7085 | 0.759 | 0.796 | 0.595 | 0.778 | 0.614 |
| WCD, compared rows | 1,182,984 | 0.7097 | 0.740 | 0.764 | 0.631 | 0.769 | 0.644 |
| WC, all its own rows | 1,184,004 | 0.7084 | 0.760 | 0.796 | 0.595 | 0.777 | 0.614 |
| v2.0.0 (26 features, WC) | 1,182,984 | 0.7010 | 0.747 | 0.786 | 0.600 | 0.752 | 0.620 |
| v1 (19 features, W) | 1,182,984 | 0.3726 | 0.472 | 0.003 | 0.495 | 0.206 | 0.687 |

## 5. Alert and block thresholds (Step 17; chosen from grouped out-of-fold training data only)

| Class | Alert threshold | Block threshold | Action (Table 5) |
| --- | ---: | ---: | --- |
| DDoS_DoS | 0.30 | none — alert only | drop_source |
| PortScan | 0.30 | 0.91 | drop_source |
| CnC | 0.30 | 0.30 | block_destination_or_isolate |
| Malware_Download | 0.30 | none — alert only | block_by_direction |

A block also needs every safety rule of the response policy (master switch, allowlist, local-network protection, repeats inside the time window, rule expiry). See `docs/response_policy.md`.

## 6. Limits

- Held-out macro-F1 is below the H1 target. Likely reasons named in proposal 1.5: domain shift between scenarios, and too few examples in some classes. The per-class table shows which classes are weak.
- **Scenario 34-1 is no longer a clean test.** It was opened in Step 16 for v1 and v2, used in the PC demonstrations, and studied in progress entry 3.71 (which led to D-052). The D-052 changes were justified with training data (all 23 scenarios were counted in the study, 34-1 included), so the 34-1 score below is reported as **measured after the scenario had been seen and studied**. The clean test is the lab (Steps 20 and 35).
- **File downloads: too little data for the model.** In the whole IoT-23 dataset only about 84 flows are real file downloads (`C&C-FileDownload` 53, `FileDownload` 18, `C&C-HeartBeat-FileDownload` 11, `C&C-Mirai` 2); the training sample has 67, and only 36 benign flows of the same shape. The `Malware_Download` group is almost all `Okiru` traffic (unanswered connection attempts to port 37215). So the model's Malware_Download class mostly finds Okiru-like exploit attempts. Downloads of programs are covered by a separate **rule** on Zeek's `files.log` (`core_engine/file_check.py`, D-052; alert only), which is not part of these model scores and is tested in the lab (Table 10 row 5).
- The window features describe IoT-23 capture traffic. A camera that is cut off from its cloud server retries the same server at regular times, which can look like C&C. This must be checked on our own camera traffic (Step 20).
- "Benign" in the IoT-23 malware captures means "not labelled as an attack". Many such flows are unanswered outbound connection attempts from the infected device (D-051, `label_trusted`).
- The model has not yet been tested on our own camera traffic (Level 3).
- One feature-importance value or one decision path is not proof of what caused an attack (proposal 3.4).

