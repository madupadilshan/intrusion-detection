# Random Forest Model Training & Validation Report (Step 14)

**Generated:** 2026-11-10 17:42:13  
**Execution Runtime:** 1410.86 seconds (23.51 minutes)  
**Governing Standard:** Group 03 Research Proposal (Sections 2.4, 3.3 step 5, 3.4)  
**Trained Model Artifact:** `ml_engine/models/rf_model.joblib` (3.21 MB)  

---

## 1. Executive Summary

This report documents the execution and validation of **Step 14 (Train the Random Forest)**. The classifier was constructed using an integrated scikit-learn `Pipeline` pairing an unknown-resilient `OrdinalEncoder` (`ColumnTransformer`) with a multi-core `RandomForestClassifier`. Hyperparameter tuning and validation were governed strictly by **Level 1 Grouped Cross-Validation** (`StratifiedGroupKFold`, 5 splits) with `groups = scenario_id` across all 22 training scenarios, eliminating intra-session data leakage.

- **Total Training Flows Evaluated:** 1,384,070 flows across 22 IoT-23 scenarios
- **Overall Level 1 Out-of-Fold Macro-F1:** **0.6041** (60.41%)
- **Mean Cross-Validation Macro-F1:** **0.5645 ± 0.1890**
- **Overall Accuracy:** **0.5852** (58.52%)
- **Benign False Positive Rate (FPR):** **45.869%** (158,442 false alarms out of 345,424 benign flows)
- **Inference Latency:** **6.23 µs/flow** (160,525 flows/second)
- **Model Size on Disk:** **3.21 MB** (prevented tree explosion via depth bounding)

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
| 1 | 0.6003 | ±0.1431 | 0.9416 | 100 | 12 | 5 | 1 | `log2` | `balanced` |
| 2 | 0.5967 | ±0.1435 | 0.9496 | 100 | 30 | 2 | 2 | `log2` | `balanced_subsample` |
| 3 | 0.5919 | ±0.1450 | 0.9502 | 200 | 30 | 5 | 2 | `sqrt` | `balanced_subsample` |
| 4 | 0.5916 | ±0.1459 | 0.9424 | 100 | 18 | 5 | 4 | `sqrt` | `balanced` |
| 5 | 0.5910 | ±0.1468 | 0.9450 | 100 | 30 | 2 | 4 | `sqrt` | `balanced` |
| 6 | 0.5872 | ±0.1458 | 0.9455 | 150 | 25 | 5 | 2 | `log2` | `balanced` |
| 7 | 0.5841 | ±0.1388 | 0.9437 | 200 | 18 | 5 | 1 | `sqrt` | `balanced_subsample` |
| 8 | 0.5830 | ±0.1428 | 0.9449 | 150 | 30 | 2 | 4 | `log2` | `balanced_subsample` |
| 9 | 0.5808 | ±0.1514 | 0.9430 | 150 | 18 | 10 | 2 | `sqrt` | `balanced` |
| 10 | 0.5750 | ±0.1566 | 0.9433 | 100 | 25 | 2 | 4 | `log2` | `balanced` |

---

## 4. Level 1 Grouped Cross-Validation (Per-Fold Performance)

Evaluated with `StratifiedGroupKFold(n_splits=5)` on all 1,384,070 flows:

| Fold # | Val Scenarios | Val Flows | Macro-F1 | Weighted-F1 | Accuracy | Recall: Benign | Recall: DDoS | Recall: PortScan | Recall: CnC | Recall: Malware | Fold Runtime |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 3 | 360,150 | **0.4179** | 0.3831 | 0.4454 | 2.1% | 99.2% | 15.8% | 98.3% | 84.2% | 60.5s |
| 2 | 4 | 299,847 | **0.3543** | 0.3701 | 0.4666 | 94.8% | 0.0% | 61.5% | 99.9% | 0.0% | 74.4s |
| 3 | 2 | 100,223 | **0.5312** | 0.5029 | 0.5011 | 0.4% | 99.9% | 0.0% | 87.7% | 91.7% | 89.1s |
| 4 | 3 | 207,579 | **0.7593** | 0.7580 | 0.8138 | 100.0% | 5.7% | 100.0% | 91.0% | 99.9% | 74.4s |
| 5 | 10 | 416,271 | **0.7598** | 0.6913 | 0.6979 | 92.8% | 100.0% | 41.9% | 87.2% | 100.0% | 59.3s |
| **Mean** | - | - | **0.5645** | 0.5411 | 0.5850 | 58.0% | 61.0% | 43.8% | 92.8% | 75.2% | 357.8s |
| **Std** | - | - | ±0.1890 | ±0.1770 | ±0.1625 | - | - | - | - | - | - |

---

## 5. Out-Of-Fold Classification Performance (Overall 1.38M Flows)

| Target Class | Support Flows | Precision | Recall | F1-Score | Detection Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **0: `Benign`** | 345,424.0 | 0.4959 | 0.5413 | **0.5176** | weak (F1 < 0.60) |
| **1: `DDoS_DoS`** | 239,585.0 | 0.9903 | 0.6336 | **0.7728** | fair (0.60 <= F1 < 0.85) |
| **2: `PortScan`** | 500,000.0 | 0.5223 | 0.4837 | **0.5023** | weak (F1 < 0.60) |
| **3: `CnC`** | 48,992.0 | 0.3515 | 0.9206 | **0.5088** | weak (F1 < 0.60) |
| **4: `Malware_Download`** | 250,069.0 | 0.7023 | 0.7367 | **0.7191** | fair (0.60 <= F1 < 0.85) |
| **Macro Average** | **1,384,070** | **0.6125** | **0.6632** | **0.6041** | (no target for this number) |
| **Weighted Average** | **1,384,070** | **0.6232** | **0.5852** | **0.5923** | - |

---

## 6. Out-Of-Fold Confusion Matrix

Rows represent ground-truth classes; columns represent predicted classes:

| Ground Truth \ Predicted | Benign | DDoS_DoS | PortScan | CnC | Malware_Download | Total Flows | Class Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Benign** | 186,982 | 1,460 | 105,449 | 2,344 | 49,189 | 345,424 | **54.13%** |
| **DDoS_DoS** | 37,778 | 151,806 | 49,997 | 4 | 0 | 239,585 | **63.36%** |
| **PortScan** | 148,434 | 33 | 241,870 | 80,783 | 28,880 | 500,000 | **48.37%** |
| **CnC** | 3,778 | 1 | 94 | 45,102 | 17 | 48,992 | **92.06%** |
| **Malware_Download** | 70 | 0 | 65,698 | 63 | 184,238 | 250,069 | **73.67%** |

---

## 7. Verification Against Research Targets

1. **Objective O2:** "Train and test a multi-class Random Forest with no scenario leakage."
   - **Method: done as planned.** `StratifiedGroupKFold` kept every scenario inside one fold, so there is no scenario leakage.
   - **Scores:** mean fold macro-F1 = **0.5645 ± 0.1890**; overall out-of-fold macro-F1 = **0.6041**. These scores are low and vary a lot between folds: a model trained on some IoT-23 scenarios does not transfer well to other scenarios. This is reported as it is (proposal Table 9: "We report all results either way").
2. **Benign False Positive Rate & Hypothesis H1 Context:**
   - **Observation:** In cross-scenario evaluation, the IoT-23 benign flows of the validation scenarios are often predicted as attacks: out-of-fold benign FPR = **45.869%** (argmax prediction, no thresholds).
   - **Context:** The FPR part of Hypothesis H1 (≤ 5%) is measured on **our own local IP-camera traffic** (Level 3, Steps 20 and 35), not on IoT-23 benign flows. This IoT-23 number is reported for information only.
3. **Model inference time (part of RQ4):**
   - Per-flow model inference time is **6.23 µs** (160,525 flows/second). This is the model step only. The proposal's latency target (Table 9: median decision < 2 s, 95th percentile < 5 s) is end-to-end, from capture to decision, and is measured on the sensor in Step 37.
4. **Memory & Footprint Safety:**
   - The saved model is **3.21 MB** (tree depth limited by the chosen `max_depth`); the old 820 MB model is not used.
