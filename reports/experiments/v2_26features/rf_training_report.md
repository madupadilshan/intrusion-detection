# Random Forest Model Training & Validation Report (Step 14)

**Generated:** 2026-11-10 18:00:41  
**Execution Runtime:** 1085.52 seconds (18.09 minutes)  
**Governing Standard:** Group 03 Research Proposal (Sections 2.4, 3.3 step 5, 3.4)  
**Trained Model Artifact:** `ml_engine/models/rf_model.joblib` (2.64 MB)  

---

## 1. Executive Summary

This report documents the execution and validation of **Step 14 (Train the Random Forest)**. The classifier was constructed using an integrated scikit-learn `Pipeline` pairing an unknown-resilient `OrdinalEncoder` (`ColumnTransformer`) with a multi-core `RandomForestClassifier`. Hyperparameter tuning and validation were governed strictly by **Level 1 Grouped Cross-Validation** (`StratifiedGroupKFold`, 5 splits) with `groups = scenario_id` across all 22 training scenarios, eliminating intra-session data leakage.

- **Total Training Flows Evaluated:** 1,184,004 flows across 22 IoT-23 scenarios
- **Overall Level 1 Out-of-Fold Macro-F1:** **0.7009** (70.09%)
- **Mean Cross-Validation Macro-F1:** **0.6734 ± 0.2114**
- **Overall Accuracy:** **0.6668** (66.68%)
- **Benign False Positive Rate (FPR):** **4.393%** (6,385 false alarms out of 145,358 benign flows)
- **Inference Latency:** **6.19 µs/flow** (161,461 flows/second)
- **Model Size on Disk:** **2.64 MB** (prevented tree explosion via depth bounding)

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
| 1 | 0.6985 | ±0.1872 | 0.9733 | 100 | 12 | 5 | 1 | `log2` | `balanced` |
| 2 | 0.6936 | ±0.1660 | 0.9745 | 100 | 30 | 2 | 2 | `log2` | `balanced_subsample` |
| 3 | 0.6867 | ±0.1539 | 0.9745 | 200 | 30 | 5 | 2 | `sqrt` | `balanced_subsample` |
| 4 | 0.6802 | ±0.1483 | 0.9740 | 200 | 18 | 5 | 1 | `sqrt` | `balanced_subsample` |
| 5 | 0.6756 | ±0.1627 | 0.9736 | 100 | 25 | 2 | 4 | `log2` | `balanced` |
| 6 | 0.6742 | ±0.1398 | 0.9740 | 150 | 25 | 5 | 2 | `log2` | `balanced` |
| 7 | 0.6740 | ±0.1477 | 0.9737 | 150 | 18 | 10 | 2 | `sqrt` | `balanced` |
| 8 | 0.6712 | ±0.1506 | 0.9736 | 100 | 18 | 5 | 4 | `sqrt` | `balanced` |
| 9 | 0.6679 | ±0.1424 | 0.9746 | 100 | 30 | 10 | 1 | `log2` | `balanced` |
| 10 | 0.6647 | ±0.1561 | 0.9736 | 150 | 30 | 2 | 4 | `log2` | `balanced_subsample` |

---

## 4. Level 1 Grouped Cross-Validation (Per-Fold Performance)

Evaluated with `StratifiedGroupKFold(n_splits=5)` on all 1,384,070 flows:

| Fold # | Val Scenarios | Val Flows | Macro-F1 | Weighted-F1 | Accuracy | Recall: Benign | Recall: DDoS | Recall: PortScan | Recall: CnC | Recall: Malware | Fold Runtime |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 3 | 59,196 | **0.5161** | 0.6647 | 0.5255 | 98.6% | 0.0% | 46.5% | 37.6% | 86.7% | 56.4s |
| 2 | 7 | 436,954 | **0.5712** | 0.5433 | 0.5880 | 99.1% | 33.2% | 24.9% | 78.9% | 99.9% | 41.1s |
| 3 | 2 | 62,200 | **0.9571** | 0.9991 | 0.9991 | 100.0% | 0.0% | 100.0% | 99.5% | 71.4% | 60.1s |
| 4 | 4 | 275,916 | **0.8386** | 0.9140 | 0.9072 | 67.6% | 92.9% | 100.0% | 97.0% | 84.2% | 50.7s |
| 5 | 6 | 349,738 | **0.4839** | 0.5056 | 0.5405 | 92.1% | 50.0% | 61.8% | 99.1% | 0.0% | 45.8s |
| **Mean** | - | - | **0.6734** | 0.7253 | 0.7121 | 91.5% | 35.2% | 66.6% | 82.4% | 68.5% | 254.2s |
| **Std** | - | - | ±0.2114 | ±0.2212 | ±0.2237 | - | - | - | - | - | - |

---

## 5. Out-Of-Fold Classification Performance (Overall 1.38M Flows)

| Target Class | Support Flows | Precision | Recall | F1-Score | Detection Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **0: `Benign`** | 145,358.0 | 0.6133 | 0.9561 | **0.7473** | fair (0.60 <= F1 < 0.85) |
| **1: `DDoS_DoS`** | 239,585.0 | 0.9907 | 0.6514 | **0.7860** | fair (0.60 <= F1 < 0.85) |
| **2: `PortScan`** | 500,000.0 | 0.6874 | 0.5316 | **0.5996** | weak (F1 < 0.60) |
| **3: `CnC`** | 48,992.0 | 0.6409 | 0.9071 | **0.7511** | fair (0.60 <= F1 < 0.85) |
| **4: `Malware_Download`** | 250,069.0 | 0.5358 | 0.7367 | **0.6204** | fair (0.60 <= F1 < 0.85) |
| **Macro Average** | **1,184,004** | **0.6936** | **0.7566** | **0.7009** | (no target for this number) |
| **Weighted Average** | **1,184,004** | **0.7057** | **0.6668** | **0.6661** | - |

---

## 6. Out-Of-Fold Confusion Matrix

Rows represent ground-truth classes; columns represent predicted classes:

| Ground Truth \ Predicted | Benign | DDoS_DoS | PortScan | CnC | Malware_Download | Total Flows | Class Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Benign** | 138,973 | 1,464 | 4,535 | 381 | 5 | 145,358 | **95.61%** |
| **DDoS_DoS** | 33,516 | 156,068 | 49,994 | 7 | 0 | 239,585 | **65.14%** |
| **PortScan** | 50,109 | 3 | 265,811 | 24,488 | 159,589 | 500,000 | **53.16%** |
| **CnC** | 3,924 | 1 | 612 | 44,441 | 14 | 48,992 | **90.71%** |
| **Malware_Download** | 67 | 0 | 65,742 | 27 | 184,233 | 250,069 | **73.67%** |

---

## 7. Verification Against Research Targets

1. **Objective O2:** "Train and test a multi-class Random Forest with no scenario leakage."
   - **Method: done as planned.** `StratifiedGroupKFold` kept every scenario inside one fold, so there is no scenario leakage.
   - **Scores:** mean fold macro-F1 = **0.6734 ± 0.2114**; overall out-of-fold macro-F1 = **0.7009**. These scores are low and vary a lot between folds: a model trained on some IoT-23 scenarios does not transfer well to other scenarios. This is reported as it is (proposal Table 9: "We report all results either way").
2. **Benign False Positive Rate & Hypothesis H1 Context:**
   - **Observation:** In cross-scenario evaluation, the IoT-23 benign flows of the validation scenarios are often predicted as attacks: out-of-fold benign FPR = **4.393%** (argmax prediction, no thresholds).
   - **Context:** The FPR part of Hypothesis H1 (≤ 5%) is measured on **our own local IP-camera traffic** (Level 3, Steps 20 and 35), not on IoT-23 benign flows. This IoT-23 number is reported for information only.
3. **Model inference time (part of RQ4):**
   - Per-flow model inference time is **6.19 µs** (161,461 flows/second). This is the model step only. The proposal's latency target (Table 9: median decision < 2 s, 95th percentile < 5 s) is end-to-end, from capture to decision, and is measured on the sensor in Step 37.
4. **Memory & Footprint Safety:**
   - The saved model is **2.64 MB** (tree depth limited by the chosen `max_depth`); the old 820 MB model is not used.
