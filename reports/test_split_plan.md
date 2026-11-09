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

Random row splitting scatters flows from the same capture across both training and testing folds, which makes the test score look much better than the real ability of the model to generalise (proposal 2.2; the old prototype reached accuracy 1.00 this way).

To test **Objective O2** ("Train and test a multi-class Random Forest with no scenario leakage") and **Hypothesis H1** (macro-F1 ≥ 0.85 on the held-out scenarios; benign FPR ≤ 5% on the local IP-camera traffic we control — proposal Section 1.5), together with the Table 9 latency target (median decision < 2 s, 95th percentile < 5 s), this project uses a rigorous, leak-free **Three-Level Evaluation Architecture** fixed prior to model training.

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
|   groups = scenario_id           |          |   Never used to choose anything  |
|   Tuning: RF; compare LR, HGB    |          |   Tests Scenario Generalization  |
+----------------------------------+          +----------------------------------+
                 |
                 +----------------------+
                                        |
                                        v
                      +----------------------------------+
                      |   LEVEL 3: REAL LAB CAMERA       |
                      |   Lab camera or simulator stream |
                      |   Baseline (Step 20) + Attacks   |
                      |   Tests benign FPR <= 5% (H1)    |
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
   - Probability calibration and the alert/block thresholds in Step 17 (fitted on the grouped out-of-fold predictions).

---

## 3. Level 2: Held-Out Scenario Evaluation (a malicious scenario the model never saw)

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
- **Rule:** This file is never used to choose anything: not the preprocessing, the hyperparameters, the calibration or the thresholds (proposal 3.4).
- **Use:** Step 16 tests the three raw models on it once. Step 17 reports the final deployed model (calibrated, with the fixed thresholds) on it once, and computes permutation importance on it (proposal 2.4: "on held-out data").
- **Note (8 Nov 2026):** the first version of Step 17 chose thresholds after looking at 34-1 results. That was corrected (decision D-040); because the team had already seen 34-1 results, this is reported as a limitation.
- **Reporting:** Metrics reported include per-class Precision, Recall, F1-Score, Confusion Matrix, and Overall Macro-F1.

---

## 4. Level 3: Local Lab Traffic Evaluation (Operational FPR & RTSP Verification)

### 4.1 Specification
- **Target:** an IP camera, or a camera simulator agreed with the supervisor (proposal 5.1: "at least one IP camera or an approved camera simulator"; decision D-038).
- **Objective:** Directly test **Hypothesis H1** ("ML detection maintains False Positive Rate $\le 5.0\%$ under real-time benign IP camera video streaming").
- **Phase Execution:**
  - **Step 20:** capture benign camera traffic with Zeek on the sensor (normal streaming, admin login, video playback, device discovery — proposal 5.1). The file made so far is synthetic test data only (D-038); it is not a Level 3 result.
  - **Step 35:** run the 6 controlled test scenarios of proposal **Table 10**:
    1. Normal live streaming and playback → most flows benign; no automatic block.
    2. Authorised Nmap horizontal scan → PortScan class or scan alert; scanner blocked only after the threshold; allowlisted admin can still connect.
    3. Rate-limited DDoS-like lab traffic → DDoS/DoS prediction; source blocked or rate-limited; camera service comes back.
    4. C&C-like periodic outbound simulation → C&C or heartbeat evidence from a local device to the outside; destination blocked or device isolated, following the policy.
    5. Controlled file-transfer pattern → download/malware prediction if the features can show it; alert and evidence kept; nothing claimed if the model cannot generalise.
    6. Manual block and unblock → rule change visible in the dashboard and database; connection comes back; full audit record kept.
  - Attack tests are only controlled scans, rate-limited flooding or replay, and approved simulations of C&C-like or file-transfer behaviour. No live malware (proposal 5.1).

### 4.2 Acceptance Criteria
- **Benign camera traffic FPR:** ≤ 5% (Hypothesis H1), and no blocks on the management computer or the NVR (Table 9).
- **Attack Detection & Decision Latency:** Median $< 2.0$ seconds, 95th percentile $< 5.0$ seconds (Proposal Table 9).
- **Allowlist:** Management IPs (`192.168.50.1`, `192.168.50.5`, `192.168.50.10`, `192.168.50.20`) must never be blocked.

---

## 5. Summary Matrix of Evaluation Levels

| Evaluation Level | Target Dataset | Primary Metric | Purpose | Execution Step |
| :--- | :--- | :--- | :--- | :---: |
| **Level 1** | 22 Scenarios (`StratifiedGroupKFold`) | Macro-F1 Score | Hyperparameter tuning, feature selection, model comparison | Steps 14, 15, 17 |
| **Level 2** | `Capture-34-1` (`data/processed/heldout/`) | Macro-F1, Precision, Recall | Generalisation to an unseen malicious scenario (results: `reports/experiments/evaluation_iot23.md`, final model: `thresholds_and_explanation.md`) | Steps 16, 17 |
| **Level 3** | Lab camera or approved simulator traffic (Zeek capture) | Benign FPR, latency, safe response | Behaviour on the camera network we control (not measured yet) | Steps 20, 35–39 |

