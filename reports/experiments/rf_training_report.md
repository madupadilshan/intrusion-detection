# Random Forest Model Training & Validation Report (Step 14)

**Generated:** 2026-11-10 22:59:40  
**Execution Runtime:** 1140.15 seconds (19.00 minutes)  
**Governing Standard:** Group 03 Research Proposal (Sections 2.4, 3.3 step 5, 3.4)  
**Trained Model Artifact:** `ml_engine/models/rf_model.joblib` (8.31 MB)  

---

## 1. Executive Summary

This report documents the execution and validation of **Step 14 (Train the Random Forest)**. The classifier was constructed using an integrated scikit-learn `Pipeline` pairing an unknown-resilient `OrdinalEncoder` (`ColumnTransformer`) with a multi-core `RandomForestClassifier`. Hyperparameter tuning and validation were governed strictly by **Level 1 Grouped Cross-Validation** (`StratifiedGroupKFold`, 5 splits) with `groups = scenario_id` across all 22 training scenarios, eliminating intra-session data leakage.

- **Total Training Flows Evaluated:** 1,182,984 flows across 22 IoT-23 scenarios
- **Overall Level 1 Out-of-Fold Macro-F1:** **0.7097** (70.97%)
- **Mean Cross-Validation Macro-F1:** **0.6674 ± 0.2119**
- **Overall Accuracy:** **0.6805** (68.05%)
- **Benign False Positive Rate (FPR):** **3.668%** (5,295 false alarms out of 144,338 benign flows)
- **Inference Latency:** **7.96 µs/flow** (125,599 flows/second)
- **Model Size on Disk:** **8.31 MB** (prevented tree explosion via depth bounding)

---

## 2. Optimal Hyperparameters

Selected through `RandomizedSearchCV` scored on `f1_macro` across 5 grouped folds:

| Hyperparameter | Optimal Selected Value | Candidate Range Explored |
| :--- | :---: | :--- |
| `n_estimators` | **100** | `[100, 150, 200]` |
| `max_depth` | **25** | `[12, 18, 25, 30]` |
| `min_samples_split` | **2** | `[2, 5, 10]` |
| `min_samples_leaf` | **4** | `[1, 2, 4]` |
| `max_features` | **`log2`** | `['sqrt', 'log2']` |
| `class_weight` | **`balanced`** | `['balanced', 'balanced_subsample']` |

---

## 3. Top Hyperparameter Configurations (Search Log)

Extracted from `reports/experiments/rf_search.csv`:

| Rank | Mean Test Macro-F1 | Std Macro-F1 | Mean Train Macro-F1 | n_estimators | max_depth | min_samples_split | min_samples_leaf | max_features | class_weight |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 0.6786 | ±0.1424 | 0.9736 | 100 | 25 | 2 | 4 | `log2` | `balanced` |
| 2 | 0.6739 | ±0.1787 | 0.9745 | 200 | 30 | 5 | 2 | `sqrt` | `balanced_subsample` |
| 3 | 0.6657 | ±0.1553 | 0.9746 | 100 | 30 | 2 | 2 | `log2` | `balanced_subsample` |
| 4 | 0.6643 | ±0.1662 | 0.9740 | 150 | 25 | 5 | 2 | `log2` | `balanced` |
| 5 | 0.6613 | ±0.1977 | 0.9736 | 100 | 12 | 5 | 1 | `log2` | `balanced` |
| 6 | 0.6594 | ±0.1582 | 0.9736 | 100 | 18 | 5 | 4 | `sqrt` | `balanced` |
| 7 | 0.6593 | ±0.1427 | 0.9737 | 150 | 30 | 2 | 4 | `log2` | `balanced_subsample` |
| 8 | 0.6588 | ±0.1682 | 0.9740 | 200 | 18 | 5 | 1 | `sqrt` | `balanced_subsample` |
| 9 | 0.6585 | ±0.1653 | 0.9737 | 100 | 30 | 2 | 4 | `sqrt` | `balanced` |
| 10 | 0.6485 | ±0.1622 | 0.9736 | 150 | 25 | 2 | 4 | `log2` | `balanced` |

---

## 4. Level 1 Grouped Cross-Validation (Per-Fold Performance)

Evaluated with `StratifiedGroupKFold(n_splits=5)` on all 1,384,070 flows:

| Fold # | Val Scenarios | Val Flows | Macro-F1 | Weighted-F1 | Accuracy | Recall: Benign | Recall: DDoS | Recall: PortScan | Recall: CnC | Recall: Malware | Fold Runtime |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 3 | 59,196 | **0.5840** | 0.9024 | 0.8537 | 99.5% | 0.0% | 83.5% | 80.7% | 86.7% | 65.4s |
| 2 | 8 | 437,119 | **0.4763** | 0.4918 | 0.5630 | 100.0% | 0.0% | 24.9% | 89.9% | 99.9% | 44.6s |
| 3 | 2 | 62,200 | **0.8942** | 0.9996 | 0.9995 | 100.0% | 0.0% | 100.0% | 100.0% | 78.6% | 66.7s |
| 4 | 4 | 274,896 | **0.8957** | 0.9342 | 0.9323 | 65.3% | 99.1% | 100.0% | 99.7% | 84.3% | 57.0s |
| 5 | 5 | 349,573 | **0.4868** | 0.5079 | 0.5435 | 92.3% | 50.0% | 62.5% | 99.2% | 0.0% | 49.8s |
| **Mean** | - | - | **0.6674** | 0.7671 | 0.7784 | 91.4% | 29.8% | 74.2% | 93.9% | 69.9% | 283.6s |
| **Std** | - | - | ±0.2119 | ±0.2466 | ±0.2121 | - | - | - | - | - | - |

---

## 5. Out-Of-Fold Classification Performance (Overall 1.38M Flows)

| Target Class | Support Flows | Precision | Recall | F1-Score | Detection Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **0: `Benign`** | 144,338.0 | 0.6002 | 0.9633 | **0.7396** | fair (0.60 <= F1 < 0.85) |
| **1: `DDoS_DoS`** | 239,585.0 | 0.9899 | 0.6224 | **0.7643** | fair (0.60 <= F1 < 0.85) |
| **2: `PortScan`** | 500,000.0 | 0.7049 | 0.5707 | **0.6307** | fair (0.60 <= F1 < 0.85) |
| **3: `CnC`** | 48,992.0 | 0.6402 | 0.9642 | **0.7695** | fair (0.60 <= F1 < 0.85) |
| **4: `Malware_Download`** | 250,069.0 | 0.5722 | 0.7370 | **0.6442** | fair (0.60 <= F1 < 0.85) |
| **Macro Average** | **1,182,984** | **0.7015** | **0.7715** | **0.7097** | (no target for this number) |
| **Weighted Average** | **1,182,984** | **0.7191** | **0.6805** | **0.6797** | - |

---

## 6. Out-Of-Fold Confusion Matrix

Rows represent ground-truth classes; columns represent predicted classes:

| Ground Truth \ Predicted | Benign | DDoS_DoS | PortScan | CnC | Malware_Download | Total Flows | Class Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Benign** | 139,043 | 1,515 | 3,668 | 108 | 4 | 144,338 | **96.33%** |
| **DDoS_DoS** | 40,442 | 149,128 | 49,993 | 22 | 0 | 239,585 | **62.24%** |
| **PortScan** | 50,534 | 5 | 285,359 | 26,395 | 137,707 | 500,000 | **57.07%** |
| **CnC** | 1,559 | 2 | 148 | 47,240 | 43 | 48,992 | **96.42%** |
| **Malware_Download** | 73 | 0 | 65,681 | 26 | 184,289 | 250,069 | **73.70%** |

---

## 7. Verification Against Research Targets

1. **Objective O2:** "Train and test a multi-class Random Forest with no scenario leakage."
   - **Method: done as planned.** `StratifiedGroupKFold` kept every scenario inside one fold, so there is no scenario leakage.
   - **Scores:** mean fold macro-F1 = **0.6674 ± 0.2119**; overall out-of-fold macro-F1 = **0.7097**. These scores are low and vary a lot between folds: a model trained on some IoT-23 scenarios does not transfer well to other scenarios. This is reported as it is (proposal Table 9: "We report all results either way").
2. **Benign False Positive Rate & Hypothesis H1 Context:**
   - **Observation:** In cross-scenario evaluation, the IoT-23 benign flows of the validation scenarios are often predicted as attacks: out-of-fold benign FPR = **3.668%** (argmax prediction, no thresholds).
   - **Context:** The FPR part of Hypothesis H1 (≤ 5%) is measured on **our own local IP-camera traffic** (Level 3, Steps 20 and 35), not on IoT-23 benign flows. This IoT-23 number is reported for information only.
3. **Model inference time (part of RQ4):**
   - Per-flow model inference time is **7.96 µs** (125,599 flows/second). This is the model step only. The proposal's latency target (Table 9: median decision < 2 s, 95th percentile < 5 s) is end-to-end, from capture to decision, and is measured on the sensor in Step 37.
4. **Memory & Footprint Safety:**
   - The saved model is **8.31 MB** (tree depth limited by the chosen `max_depth`); the old 820 MB model is not used.
