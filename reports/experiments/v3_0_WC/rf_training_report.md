# Random Forest Model Training & Validation Report (Step 14)

**Generated:** 2026-11-10 22:40:20  
**Execution Runtime:** 1287.19 seconds (21.45 minutes)  
**Governing Standard:** Group 03 Research Proposal (Sections 2.4, 3.3 step 5, 3.4)  
**Trained Model Artifact:** `ml_engine/models/rf_model.joblib` (2.41 MB)  

---

## 1. Executive Summary

This report documents the execution and validation of **Step 14 (Train the Random Forest)**. The classifier was constructed using an integrated scikit-learn `Pipeline` pairing an unknown-resilient `OrdinalEncoder` (`ColumnTransformer`) with a multi-core `RandomForestClassifier`. Hyperparameter tuning and validation were governed strictly by **Level 1 Grouped Cross-Validation** (`StratifiedGroupKFold`, 5 splits) with `groups = scenario_id` across all 22 training scenarios, eliminating intra-session data leakage.

- **Total Training Flows Evaluated:** 1,184,004 flows across 22 IoT-23 scenarios
- **Overall Level 1 Out-of-Fold Macro-F1:** **0.7084** (70.84%)
- **Mean Cross-Validation Macro-F1:** **0.6719 ± 0.2045**
- **Overall Accuracy:** **0.6684** (66.84%)
- **Benign False Positive Rate (FPR):** **4.655%** (6,767 false alarms out of 145,358 benign flows)
- **Inference Latency:** **4.81 µs/flow** (207,902 flows/second)
- **Model Size on Disk:** **2.41 MB** (prevented tree explosion via depth bounding)

---

## 2. Optimal Hyperparameters

Selected through `RandomizedSearchCV` scored on `f1_macro` across 5 grouped folds:

| Hyperparameter | Optimal Selected Value | Candidate Range Explored |
| :--- | :---: | :--- |
| `n_estimators` | **100** | `[100, 150, 200]` |
| `max_depth` | **12** | `[12, 18, 25, 30]` |
| `min_samples_split` | **5** | `[2, 5, 10]` |
| `min_samples_leaf` | **1** | `[1, 2, 4]` |
| `max_features` | **`log2`** | `['sqrt', 'log2']` |
| `class_weight` | **`balanced`** | `['balanced', 'balanced_subsample']` |

---

## 3. Top Hyperparameter Configurations (Search Log)

Extracted from `reports/experiments/rf_search.csv`:

| Rank | Mean Test Macro-F1 | Std Macro-F1 | Mean Train Macro-F1 | n_estimators | max_depth | min_samples_split | min_samples_leaf | max_features | class_weight |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 0.7159 | ±0.1967 | 0.9733 | 100 | 12 | 5 | 1 | `log2` | `balanced` |
| 2 | 0.6974 | ±0.1456 | 0.9740 | 150 | 25 | 5 | 2 | `log2` | `balanced` |
| 3 | 0.6935 | ±0.1627 | 0.9745 | 100 | 30 | 2 | 2 | `log2` | `balanced_subsample` |
| 4 | 0.6864 | ±0.1545 | 0.9744 | 200 | 30 | 5 | 2 | `sqrt` | `balanced_subsample` |
| 5 | 0.6833 | ±0.1403 | 0.9737 | 100 | 30 | 2 | 4 | `sqrt` | `balanced` |
| 6 | 0.6823 | ±0.1466 | 0.9737 | 150 | 18 | 10 | 2 | `sqrt` | `balanced` |
| 7 | 0.6788 | ±0.1500 | 0.9736 | 100 | 25 | 2 | 4 | `log2` | `balanced` |
| 8 | 0.6775 | ±0.1500 | 0.9736 | 150 | 25 | 2 | 4 | `log2` | `balanced` |
| 9 | 0.6718 | ±0.1408 | 0.9737 | 150 | 30 | 2 | 4 | `log2` | `balanced_subsample` |
| 10 | 0.6683 | ±0.1597 | 0.9740 | 200 | 18 | 5 | 1 | `sqrt` | `balanced_subsample` |

---

## 4. Level 1 Grouped Cross-Validation (Per-Fold Performance)

Evaluated with `StratifiedGroupKFold(n_splits=5)` on all 1,384,070 flows:

| Fold # | Val Scenarios | Val Flows | Macro-F1 | Weighted-F1 | Accuracy | Recall: Benign | Recall: DDoS | Recall: PortScan | Recall: CnC | Recall: Malware | Fold Runtime |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 3 | 59,196 | **0.4915** | 0.5664 | 0.4284 | 99.4% | 0.0% | 34.8% | 37.6% | 86.7% | 79.0s |
| 2 | 7 | 436,954 | **0.6063** | 0.5591 | 0.6004 | 99.2% | 41.8% | 25.2% | 89.9% | 100.0% | 48.1s |
| 3 | 2 | 62,200 | **0.9312** | 0.9996 | 0.9997 | 100.0% | 0.0% | 100.0% | 100.0% | 57.1% | 67.8s |
| 4 | 4 | 275,916 | **0.8429** | 0.9158 | 0.9093 | 68.0% | 93.0% | 99.9% | 99.6% | 84.2% | 57.7s |
| 5 | 6 | 349,738 | **0.4874** | 0.5092 | 0.5449 | 90.9% | 50.0% | 63.2% | 99.2% | 0.0% | 52.7s |
| **Mean** | - | - | **0.6719** | 0.7100 | 0.6965 | 91.5% | 37.0% | 64.6% | 85.2% | 65.6% | 305.2s |
| **Std** | - | - | ±0.2045 | ±0.2291 | ±0.2456 | - | - | - | - | - | - |

---

## 5. Out-Of-Fold Classification Performance (Overall 1.38M Flows)

| Target Class | Support Flows | Precision | Recall | F1-Score | Detection Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **0: `Benign`** | 145,358.0 | 0.6314 | 0.9534 | **0.7597** | fair (0.60 <= F1 < 0.85) |
| **1: `DDoS_DoS`** | 239,585.0 | 0.9890 | 0.6658 | **0.7958** | fair (0.60 <= F1 < 0.85) |
| **2: `PortScan`** | 500,000.0 | 0.6853 | 0.5252 | **0.5947** | weak (F1 < 0.60) |
| **3: `CnC`** | 48,992.0 | 0.6594 | 0.9466 | **0.7773** | fair (0.60 <= F1 < 0.85) |
| **4: `Malware_Download`** | 250,069.0 | 0.5269 | 0.7368 | **0.6144** | fair (0.60 <= F1 < 0.85) |
| **Macro Average** | **1,184,004** | **0.6984** | **0.7656** | **0.7084** | (no target for this number) |
| **Weighted Average** | **1,184,004** | **0.7056** | **0.6684** | **0.6674** | - |

---

## 6. Out-Of-Fold Confusion Matrix

Rows represent ground-truth classes; columns represent predicted classes:

| Ground Truth \ Predicted | Benign | DDoS_DoS | PortScan | CnC | Malware_Download | Total Flows | Class Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Benign** | 138,591 | 1,761 | 4,722 | 278 | 6 | 145,358 | **95.34%** |
| **DDoS_DoS** | 30,079 | 159,505 | 49,996 | 5 | 0 | 239,585 | **66.58%** |
| **PortScan** | 48,322 | 3 | 262,619 | 23,641 | 165,415 | 500,000 | **52.52%** |
| **CnC** | 2,442 | 2 | 144 | 46,375 | 29 | 48,992 | **94.66%** |
| **Malware_Download** | 63 | 0 | 65,733 | 25 | 184,248 | 250,069 | **73.68%** |

---

## 7. Verification Against Research Targets

1. **Objective O2:** "Train and test a multi-class Random Forest with no scenario leakage."
   - **Method: done as planned.** `StratifiedGroupKFold` kept every scenario inside one fold, so there is no scenario leakage.
   - **Scores:** mean fold macro-F1 = **0.6719 ± 0.2045**; overall out-of-fold macro-F1 = **0.7084**. These scores are low and vary a lot between folds: a model trained on some IoT-23 scenarios does not transfer well to other scenarios. This is reported as it is (proposal Table 9: "We report all results either way").
2. **Benign False Positive Rate & Hypothesis H1 Context:**
   - **Observation:** In cross-scenario evaluation, the IoT-23 benign flows of the validation scenarios are often predicted as attacks: out-of-fold benign FPR = **4.655%** (argmax prediction, no thresholds).
   - **Context:** The FPR part of Hypothesis H1 (≤ 5%) is measured on **our own local IP-camera traffic** (Level 3, Steps 20 and 35), not on IoT-23 benign flows. This IoT-23 number is reported for information only.
3. **Model inference time (part of RQ4):**
   - Per-flow model inference time is **4.81 µs** (207,902 flows/second). This is the model step only. The proposal's latency target (Table 9: median decision < 2 s, 95th percentile < 5 s) is end-to-end, from capture to decision, and is measured on the sensor in Step 37.
4. **Memory & Footprint Safety:**
   - The saved model is **2.41 MB** (tree depth limited by the chosen `max_depth`); the old 820 MB model is not used.
