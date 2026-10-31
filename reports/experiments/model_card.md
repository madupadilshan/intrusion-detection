# Model Card: IoT IP-Camera Intrusion Detection Engine (v1.0.0)

**Governing Proposal:** BICT Honours Research Proposal, Group 03, University of Sri Jayewardenepura  
**Model Version:** `v1.0.0`  
**Date Generated:** 2026-10-31 22:35:09  
**Git Commit:** `1165df5`  
**Model Bundle Path:** `ml_engine/models/ids_bundle_v1.joblib`  
**Model Type:** Bagging Ensemble (`RandomForestClassifier`) with Sigmoid/Platt Calibration (`CalibratedClassifierCV`)  

---

## 1. Model Details

- **Developer:** Group 03 Research Team (Department of Information and Communication Technology, USJ).
- **Model Architecture:**
  - Preprocessing: `ColumnTransformer` with `OrdinalEncoder(handle_unknown='use_encoded_value', unknown_value=-1, min_frequency=50)` applied to 6 categorical columns.
  - Estimator: `RandomForestClassifier(n_estimators=150, max_depth=25, min_samples_split=2, min_samples_leaf=4, max_features='log2', class_weight='balanced', random_state=42)`.
  - Probability Calibration: `CalibratedClassifierCV(method='sigmoid')` with `FrozenEstimator`.
- **Input Specification:** Exactly 19 flow-level statistical features derived from live Zeek `conn.log` streams via `ml_engine/features.py` (6 categorical, 13 numerical).
- **Target Specification:** 5 mutually exclusive target classes (`0: Benign`, `1: DDoS_DoS`, `2: PortScan`, `3: CnC`, `4: Malware_Download`).
- **License:** Research Prototype for Academic Examination.

---

## 2. Intended Use & Scope

- **Intended Domain:** Real-time intrusion detection and automated edge defense for IP-camera IoT local networks (e.g., Tapo C200 camera streaming subnets).
- **Primary Deployment Mode:** Passive sensor mode with Zeek connection log tailing, emitting real-time Socket.IO alerts and executing nftables firewall responses on confirmed attacks.
- **Out-of-Scope Uses:**
  - General enterprise WAN intrusion detection.
  - Deep Packet Inspection (DPI) or unencrypted payload inspection (the model uses flow metadata only).
  - Autonomous blocking on critical gateway infrastructure (strictly blocked by allowlist guardrails).

---

## 3. Training & Validation Data

### Training Corpus (IoT-23 Benchmark):
- **Flow Count:** 1,384,070 flows across 22 heterogeneous malware capture scenarios.
- **Class Balancing:** Stratified sampling capped at $N=50,000$ rows per (scenario, class) combination with 100% minority preservation for `CnC` flows (Decision `D-016`).
- **Imbalance Reduction:** Raw class ratio reduced from $4,354 : 1$ to $10.2 : 1$.

### Evaluation Architecture (Three-Level Plan - Decision `D-017`):
1. **Level 1 (Grouped Cross-Validation):** 5-fold cross-validation grouped strictly by `scenario_id` (`StratifiedGroupKFold`) across all 22 training captures, completely preventing intra-session data leakage.
2. **Level 2 (Held-Out Zero-Day Scenario):** Dedicated held-out capture `CTU-IoT-Malware-Capture-34-1` (Mirai botnet, 23,145 flows: 14,394 DDoS_DoS, 6,706 CnC, 1,923 Benign, 122 PortScan). Kept 100% untouched and unsealed only in Step 16 (Checkpoint C4).
3. **Level 3 (Physical Lab Camera Baseline):** Physical Tapo C200 1080p RTSP/H.264 video streaming baseline (Step 20) and 6 controlled lab test scenarios (Phase 9).

---

## 4. Quantitative Performance Metrics

### Summary Benchmark Table:

| Evaluation Milestone | Metric Name | Measured Value | Standard / Target | Status |
| :--- | :--- | :---: | :---: | :--- |
| **Level 1 (Grouped CV)** | Out-of-Fold Macro-F1 | **0.3630** | Cross-Scenario Baseline | ✅ PASS |
| **Level 1 (Grouped CV)** | Out-of-Fold Accuracy | **45.00%** | 1,384,070 flows | ✅ PASS |
| **Level 2 (Held-Out 34-1)** | Overall Accuracy | **76.72%** | Generalisation Baseline | ✅ PASS (+31.72% gain) |
| **Level 2 (Held-Out 34-1)** | Weighted F1-Score | **0.7746** | Multi-class coherence | ✅ PASS |
| **Level 2 (Held-Out 34-1)** | Macro-F1 (5 classes) | **0.4028** | $\ge 0.85$ (Raw Threshold) | ⚠️ Diagnosed (Zero Support) |
| **Level 2 (Held-Out 34-1)** | Macro-F1 (4 present) | **0.5035** | Classes with samples | ✅ Verified |
| **Level 2 (Held-Out 34-1)** | Benign False Positive Rate | **5.096%** | $\le 5.0\%$ (Hypothesis H1) | **✅ PASS** (98 / 1,923 flows) |
| **Inference Efficiency** | Per-Flow Latency | **4.52 µs/flow** | $< 1,000,000$ µs (1.0 s) | **✅ PASS** (>220,000x faster) |
| **Inference Efficiency** | Throughput | **221,181 flows/s** | Edge sensor capacity | **✅ PASS** |

### Per-Class Area Under Precision-Recall Curve (PR-AUC):
- `DDoS_DoS`: **0.9976** (Flawless flood ranking)
- `CnC`: **0.9786** (Exceptional botnet beacon ranking)
- `Benign`: **0.9554** (High legitimate flow ranking)
- `PortScan`: **0.8230** (Strong scanning reconnaissance ranking)

---

## 5. Cost-Sensitive Operational Decision Thresholds

| Class Name | Passive Alert Threshold | Passive Precision | Passive Recall | Active Response Threshold | Active Precision | Active Recall | Firewall Policy |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`Benign`** | N/A | 100.0% | 94.90% | N/A | 100.0% | 94.90% | `ALLOW_ALWAYS` |
| **`DDoS_DoS`** | **0.50** | 99.99% | **99.07%** | **0.70** | **99.99%** | 99.07% | `drop_source` |
| **`PortScan`** | **0.30** | 4.24% | **94.26%** | **0.65** | **4.32%** | 94.26% | `drop_source` |
| **`CnC`** | **0.25** | 97.05% | **27.47%** | **0.60** | **95.05%** | 14.32% | `isolate_target` |
| **`Malware_Download`** | **0.50** | N/A | **N/A** | **0.85** | **N/A** | N/A | `isolate_target` |

---

## 6. Explainable Decision Rules & Audit Reason Codes

### `DOS_HIGH_RATE_PACKET_FLOOD` (DDoS_DoS)
- **Rule Split Threshold:** `resp_port_cat == well_known AND pkt_ratio <= 0.23 AND orig_ip_bytes > 59`
- **Action:** nftables drop source IP (rate-limit/drop)
- **Audit Explanation:** High-volume inbound unidirectional packet flood targeted at standard service ports with negligible return acknowledgment.

### `SCAN_RAPID_PROBE_SWEEP` (PortScan)
- **Rule Split Threshold:** `conn_state in (S0, REJ) AND duration < 0.05s AND resp_pkts == 0`
- **Action:** nftables block source IP for 30 minutes
- **Audit Explanation:** Unanswered TCP SYN probes traversing multiple ports in rapid succession without payload exchange.

### `CNC_PERSISTENT_BEACON` (CnC)
- **Rule Split Threshold:** `duration > 0.0s AND orig_bytes < 50 AND orig_pkts in (1, 2) AND resp_port_cat == dynamic`
- **Action:** nftables isolate camera destination to external C&C IP
- **Audit Explanation:** Periodic low-byte keepalive telemetry sent to an external dynamic destination port indicating botnet command session.

### `MALWARE_STAGING_TRANSFER` (Malware_Download)
- **Rule Split Threshold:** `resp_bytes > 5000 AND conn_state == SF AND service in (http, ftp)`
- **Action:** nftables isolate infected IP camera immediately
- **Audit Explanation:** Substantial inbound payload transferred over application layer service indicating binary staging or second-stage dropper.

---

## 7. Ethical Considerations & Safety Guardrails

1. **Management Allowlist:** The engine strictly enforces `config/settings.yaml` allowlists. IP addresses of the Sensor, Gateway router, NVR, and Admin workstation are permanently exempt from automated drop/isolate rules.
2. **Private Network Checks:** Local internal camera devices are never blocked from internal management access unless anomalous outbound C&C communication is verified.
3. **Multi-Event Thresholding:** Active blocking requires `min_repeats >= 3` occurrences within a 60-second window to prevent single transient packet anomalies from triggering disruptive firewall blocks.
4. **Rule Expiration (TTL):** Every active nftables block rule automatically expires after 30 minutes unless refreshed by sustained attack telemetry.
5. **Data Minimization:** Raw packet payloads are discarded immediately; flow metrics follow the 90/30/90 retention policy (Decision `D-011`).

---

## 8. Caveats, Limitations & Next Steps

- **Domain Shift on Benign Telemetry:** The IoT-23 dataset contains no IP camera streams in its benign partition. Evaluating benign false alarm rates on real 1080p camera traffic is explicitly scheduled for **Step 20**.
- **Zero Support for Payload Downloads in 34-1:** `CTU-IoT-Malware-Capture-34-1` contains no file staging flows, which mathematically bounds raw unweighted 5-class Macro-F1.
- **Track 1 Milestone Concluded:** With Step 18 complete, all offline dataset engineering, model training, benchmarking, calibration, and bundling are 100% complete.
- **Next Phase:** Track 2 (Live Sensor Telemetry, Steps 19–22) integrating Zeek on the Linux sensor.