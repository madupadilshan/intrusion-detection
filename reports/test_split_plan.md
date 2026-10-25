# Three-Level Model Evaluation & Test Split Plan (Step 13)

**Document Version:** 1.0  
**Date:** 2026-10-25  
**Governing Standard:** Group 03 Research Proposal (Section 3.4, Objective O2, Hypotheses H1 & H2)  
**Related Decisions:** `D-016` (Stratified Sampling Strategy), `D-017` (Three-Level Validation Architecture)  
**Associated Data:**  
- Level 1 & Training Data: `data/processed/train_features.parquet`  
- Level 2 Held-Out Data: `data/processed/heldout/held_out_test.parquet`  
- Level 3 Lab Traffic: `data/interim/lab_camera_baseline.parquet` (to be collected in Step 20)  

---

## 1. Architectural Motivation & Anti-Leakage Rationale

A pervasive flaw in legacy intrusion detection literature is evaluating machine learning models via naive random row-level train-test splits (`train_test_split(test_size=0.2)`). In network security datasets such as IoT-23, multiple consecutive flows originate from the identical attack session or botnet command loop, sharing identical packet timings, connection states, and network artifacts. 

Random row splitting scatters flows from the same capture across both training and testing folds, artificially inflating evaluation accuracy to 99.9%–100.0% while causing catastrophic model failure when deployed against novel network environments or zero-day variants.

To satisfy **Objective O2** ("Achieve ≥ 90% macro-F1 on held-out test scenarios with < 1% false positive rate on legitimate camera streaming"), this project establishes a rigorous, leak-free **Three-Level Evaluation Architecture** fixed prior to model training.

```
+--------------------------------------------------------------------------------------------------+
|                                    OFFICIAL IOT-23 DATASET                                       |
|                                (23 Capture Scenarios, 325M Flows)                                |
+--------------------------------------------------------------------------------------------------+
                                        |
                 +----------------------+----------------------+
                 |                                             |
                 v                                             v
+----------------------------------+          +----------------------------------+
|    22 TRAINING SCENARIOS         |          |    1 HELD-OUT SCENARIO (Level 2) |
|    (Capped N=50k/class)          |          |    CTU-IoT-Malware-Capture-34-1  |
|    Total: 1,384,070 Flows        |          |    Total: 23,145 Flows (100%)    |
+----------------------------------+          +----------------------------------+
                 |                                             |
                 v                                             v
+----------------------------------+          +----------------------------------+
|   LEVEL 1: GROUPED CV            |          |   LEVEL 2: ZERO-DAY TEST         |
|   StratifiedGroupKFold(n=5)      |          |   Sealed in data/processed/heldout|
|   groups = scenario_id           |          |   Opened ONLY in Step 16         |
|   Tuning: RF, XGBoost, Linear    |          |   Tests Scenario Generalization  |
+----------------------------------+          +----------------------------------+
                 |
                 +----------------------+
                                        |
                                        v
                      +----------------------------------+
                      |   LEVEL 3: REAL LAB CAMERA       |
                      |   Physical Tapo C200 Video Stream|
                      |   Baseline (Step 20) + Attacks   |
                      |   Tests FPR < 1% on RTSP/H.264   |
                      +----------------------------------+
```

---

## 2. Level 1: Grouped Cross-Validation (Model Selection & Hyperparameter Tuning)

### 2.1 Specification
- **Algorithm:** `sklearn.model_selection.StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)`
- **Grouping Variable (`groups`):** `scenario_id` (22 unique scenario IDs)
- **Target Variable (`y`):** `label_idx` (5 target classes: 0=Benign, 1=DDoS_DoS, 2=PortScan, 3=CnC, 4=Malware_Download)
- **Features (`X`):** 19 engineered features from `ml_engine.features.FEATURE_COLUMNS`

### 2.2 Guarantees & Constraints
1. **Scenario Integrity:** All flows belonging to any single `scenario_id` are strictly assigned to either the 4 training folds OR the 1 validation fold during each split. Under no circumstances are flows from the same capture split across train and validation folds.
2. **Class Stratification:** `StratifiedGroupKFold` optimizes group assignments such that all 5 classes are represented in both train and validation folds as evenly as possible.
3. **Usage Restriction:** Level 1 CV is used exclusively for:
   - Comparing baseline models (Random Forest, Logistic Regression / SGD, Gradient Boosting) in Step 15.
   - Hyperparameter tuning (`RandomizedSearchCV` / `GridSearchCV`) scored strictly by **Macro-Averaged F1-Score** (`scoring='f1_macro'`).
   - Probability calibration (`CalibratedClassifierCV`) in Step 17.

---

## 3. Level 2: Held-Out Scenario Evaluation (Zero-Day & Unseen Variant Generalization)

### 3.1 Scenario Selection: `CTU-IoT-Malware-Capture-34-1` (`dataset17.csv`)
- **Malware Family:** Mirai (one of the most prevalent IP camera and IoT botnets in existence).
- **Duration / Flow Count:** 23,145 total flows.
- **Class Representation:**
  - `DDoS_DoS`: 14,394 flows (62.20%)
  - `CnC`: 6,706 flows (28.97%)
  - `Benign`: 1,923 flows (8.31%)
  - `PortScan`: 122 flows (0.53%)
  - `Malware_Download`: 0 flows (0.00%)
- **Justification for Selection:**
  1. Contains 4 out of the 5 project classes, providing simultaneous validation of benign traffic, network probing (PortScan), command loops (CnC), and high-volume volumetric flooding (DDoS).
  2. While Capture-34-1 is held out, the remaining 22 training scenarios retain abundant flows for all 5 classes (including over 48,900 CnC flows and 239,000 DDoS flows), guaranteeing that no class is starved during training.
  3. Total volume (23,145 flows) is perfectly sized to evaluate without down-sampling or artificial rebalancing.

### 3.2 Anti-Leakage Protocol (Checkpoint C4)
- **Storage Isolation:** Stored in dedicated sealed path `data/processed/heldout/held_out_test.parquet`.
- **Absolute Lock:** This file MUST NOT be loaded, inspected, or transformed during Steps 14, 15, or 17.
- **Single Evaluation:** Evaluated exactly once in **Step 16** using the final, frozen, calibrated model bundle.
- **Reporting:** Metrics reported include per-class Precision, Recall, F1-Score, Confusion Matrix, and Overall Macro-F1.

---

## 4. Level 3: Local Lab Traffic Evaluation (Operational FPR & RTSP Verification)

### 4.1 Specification
- **Hardware Target:** Physical Tapo C200 1080p IP Camera streaming continuous RTSP / H.264 video traffic across managed switch port mirroring to the Linux sensor.
- **Objective:** Directly test **Hypothesis H1** ("ML detection maintains False Positive Rate < 1% under real-time benign IP camera video streaming").
- **Phase Execution:**
  - **Step 20 (Phase 5):** Collect 24-hour continuous baseline benign traffic from the physical IP camera. Convert Zeek `conn.log` into feature vectors using `ml_engine.features.make_features()`.
  - **Phase 9 (Steps 35–39):** Execute the 6 controlled test attack scenarios (Table 10):
    1. Outside TCP SYN Port Scan (FR-05)
    2. Mirai-style Telnet / SSH brute-force & C&C beaconing
    3. High-rate UDP / ICMP flood targeting camera RTSP port 554
    4. HTTP digest authentication brute-force against camera web portal
    5. Benign RTSP video streaming saturation (high bitrate load test)
    6. Rapid multi-vector composite attack

### 4.2 Acceptance Criteria
- **Benign Camera Stream FPR:** $< 1.0\%$ false alarms over continuous 24-hour operation.
- **Attack Detection Latency:** $\le 1.0$ second from flow termination in Zeek to response rule emission.
- **Zero Allowlist Collisions:** Management IPs (`192.168.50.1`, `192.168.50.5`, `192.168.50.10`, `192.168.50.20`) must never be blocked.

---

## 5. Summary Matrix of Evaluation Levels

| Evaluation Level | Target Dataset | Primary Metric | Purpose | Execution Step |
| :--- | :--- | :--- | :--- | :---: |
| **Level 1** | 22 Scenarios (`StratifiedGroupKFold`) | Macro-F1 Score | Hyperparameter tuning, feature selection, model comparison | Steps 14, 15, 17 |
| **Level 2** | `Capture-34-1` (`data/processed/heldout/`) | Macro-F1, Precision, Recall | Zero-day & cross-scenario botnet generalization | Step 16 |
| **Level 3** | Physical Tapo C200 Lab Traffic | False Positive Rate (FPR), Latency | Real-world IP camera video streaming & active defense verification | Steps 20, 35–39 |

