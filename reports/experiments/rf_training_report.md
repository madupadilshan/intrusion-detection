# Random Forest Model Training & Validation Report (Step 14)

**Generated:** 2026-11-08 23:43:48  
**Execution Runtime:** 972.58 seconds (16.21 minutes)  
**Governing Standard:** Group 03 Research Proposal (Sections 2.4, 3.3 step 5, 3.4)  
**Trained Model Artifact:** `ml_engine/models/rf_model.joblib` (4.30 MB)  

---

## 1. Executive Summary

This report documents the execution and validation of **Step 14 (Train the Random Forest)**. The classifier was constructed using an integrated scikit-learn `Pipeline` pairing an unknown-resilient `OrdinalEncoder` (`ColumnTransformer`) with a multi-core `RandomForestClassifier`. Hyperparameter tuning and validation were governed strictly by **Level 1 Grouped Cross-Validation** (`StratifiedGroupKFold`, 5 splits) with `groups = scenario_id` across all 22 training scenarios, eliminating intra-session data leakage.

- **Total Training Flows Evaluated:** 1,384,070 flows across 22 IoT-23 scenarios
- **Overall Level 1 Out-of-Fold Macro-F1:** **0.3422** (34.22%)
- **Mean Cross-Validation Macro-F1:** **0.3353 ± 0.1704**
- **Overall Accuracy:** **0.4240** (42.40%)
- **Benign False Positive Rate (FPR):** **45.737%** (157,985 false alarms out of 345,424 benign flows)
- **Inference Latency:** **4.66 µs/flow** (214,454 flows/second)
- **Model Size on Disk:** **4.30 MB** (prevented tree explosion via depth bounding)

---

## 2. Optimal Hyperparameters

Selected through `RandomizedSearchCV` scored on `f1_macro` across 5 grouped folds:

| Hyperparameter | Optimal Selected Value | Candidate Range Explored |
| :--- | :---: | :--- |
| `n_estimators` | **100** | `[100, 150, 200]` |
| `max_depth` | **18** | `[12, 18, 25, 30]` |
| `min_samples_split` | **5** | `[2, 5, 10]` |
| `min_samples_leaf` | **4** | `[1, 2, 4]` |
| `max_features` | **`sqrt`** | `['sqrt', 'log2']` |
| `class_weight` | **`balanced`** | `['balanced', 'balanced_subsample']` |

---

## 3. Top Hyperparameter Configurations (Search Log)

Extracted from `reports/experiments/rf_search.csv`:

| Rank | Mean Test Macro-F1 | Std Macro-F1 | Mean Train Macro-F1 | n_estimators | max_depth | min_samples_split | min_samples_leaf | max_features | class_weight |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 0.3591 | ±0.1455 | 0.7852 | 100 | 18 | 5 | 4 | `sqrt` | `balanced` |
| 2 | 0.3521 | ±0.1361 | 0.7929 | 100 | 25 | 2 | 4 | `log2` | `balanced` |
| 3 | 0.3506 | ±0.1318 | 0.7942 | 150 | 30 | 2 | 4 | `log2` | `balanced_subsample` |
| 4 | 0.3433 | ±0.1437 | 0.7939 | 100 | 30 | 2 | 4 | `sqrt` | `balanced` |
| 5 | 0.3403 | ±0.1222 | 0.7771 | 100 | 12 | 5 | 1 | `log2` | `balanced` |
| 6 | 0.3401 | ±0.1432 | 0.8005 | 100 | 30 | 2 | 2 | `log2` | `balanced_subsample` |
| 7 | 0.3400 | ±0.1258 | 0.7876 | 150 | 18 | 10 | 2 | `sqrt` | `balanced` |
| 8 | 0.3252 | ±0.1315 | 0.7926 | 150 | 25 | 2 | 4 | `log2` | `balanced` |
| 9 | 0.3251 | ±0.1569 | 0.8001 | 100 | 30 | 10 | 1 | `log2` | `balanced` |
| 10 | 0.3238 | ±0.1307 | 0.7983 | 150 | 25 | 5 | 2 | `log2` | `balanced` |

---

## 4. Level 1 Grouped Cross-Validation (Per-Fold Performance)

Evaluated with `StratifiedGroupKFold(n_splits=5)` on all 1,384,070 flows:

| Fold # | Val Scenarios | Val Flows | Macro-F1 | Weighted-F1 | Accuracy | Recall: Benign | Recall: DDoS | Recall: PortScan | Recall: CnC | Recall: Malware | Fold Runtime |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 3 | 360,150 | **0.1675** | 0.2102 | 0.2853 | 1.9% | 0.0% | 15.5% | 13.1% | 84.2% | 54.3s |
| 2 | 4 | 299,847 | **0.3225** | 0.4498 | 0.4621 | 95.0% | 0.0% | 63.2% | 42.8% | 0.0% | 52.3s |
| 3 | 2 | 100,223 | **0.1957** | 0.0095 | 0.0065 | 0.4% | 0.8% | 0.0% | 98.8% | 91.7% | 66.2s |
| 4 | 3 | 207,579 | **0.5880** | 0.6678 | 0.7464 | 100.0% | 0.0% | 96.2% | 20.8% | 99.9% | 65.6s |
| 5 | 10 | 416,271 | **0.4025** | 0.3700 | 0.4562 | 93.4% | 0.0% | 16.6% | 83.9% | 100.0% | 47.6s |
| **Mean** | - | - | **0.3353** | 0.3415 | 0.3913 | 58.1% | 0.2% | 38.3% | 51.9% | 75.1% | 286.1s |
| **Std** | - | - | ±0.1704 | ±0.2482 | ±0.2714 | - | - | - | - | - | - |

---

## 5. Out-Of-Fold Classification Performance (Overall 1.38M Flows)

| Target Class | Support Flows | Precision | Recall | F1-Score | Detection Assessment |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **0: `Benign`** | 345,424.0 | 0.3803 | 0.5426 | **0.4472** | weak (F1 < 0.60) |
| **1: `DDoS_DoS`** | 239,585.0 | 0.3311 | 0.0016 | **0.0032** | weak (F1 < 0.60) |
| **2: `PortScan`** | 500,000.0 | 0.5881 | 0.3831 | **0.4640** | weak (F1 < 0.60) |
| **3: `CnC`** | 48,992.0 | 0.1017 | 0.4747 | **0.1674** | weak (F1 < 0.60) |
| **4: `Malware_Download`** | 250,069.0 | 0.5490 | 0.7365 | **0.6291** | fair (0.60 <= F1 < 0.85) |
| **Macro Average** | **1,384,070** | **0.3900** | **0.4277** | **0.3422** | (no target for this number) |
| **Weighted Average** | **1,384,070** | **0.4675** | **0.4240** | **0.3994** | - |

---

## 6. Out-Of-Fold Confusion Matrix

Rows represent ground-truth classes; columns represent predicted classes:

| Ground Truth \ Predicted | Benign | DDoS_DoS | PortScan | CnC | Malware_Download | Total Flows | Class Recall |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Benign** | 187,439 | 781 | 53,675 | 54,192 | 49,337 | 345,424 | **54.26%** |
| **DDoS_DoS** | 189,195 | 387 | 0 | 50,003 | 0 | 239,585 | **0.16%** |
| **PortScan** | 105,157 | 1 | 191,556 | 101,331 | 101,955 | 500,000 | **38.31%** |
| **CnC** | 11,054 | 0 | 14,681 | 23,257 | 0 | 48,992 | **47.47%** |
| **Malware_Download** | 68 | 0 | 65,810 | 6 | 184,185 | 250,069 | **73.65%** |

---

## 7. Verification Against Research Targets

1. **Objective O2:** "Train and test a multi-class Random Forest with no scenario leakage."
   - **Method: done as planned.** `StratifiedGroupKFold` kept every scenario inside one fold, so there is no scenario leakage.
   - **Scores:** mean fold macro-F1 = **0.3353 ± 0.1704**; overall out-of-fold macro-F1 = **0.3422**. These scores are low and vary a lot between folds: a model trained on some IoT-23 scenarios does not transfer well to other scenarios. This is reported as it is (proposal Table 9: "We report all results either way").
2. **Benign False Positive Rate & Hypothesis H1 Context:**
   - **Observation:** In cross-scenario evaluation, the IoT-23 benign flows of the validation scenarios are often predicted as attacks: out-of-fold benign FPR = **45.737%** (argmax prediction, no thresholds).
   - **Context:** The FPR part of Hypothesis H1 (≤ 5%) is measured on **our own local IP-camera traffic** (Level 3, Steps 20 and 35), not on IoT-23 benign flows. This IoT-23 number is reported for information only.
3. **Model inference time (part of RQ4):**
   - Per-flow model inference time is **4.66 µs** (214,454 flows/second). This is the model step only. The proposal's latency target (Table 9: median decision < 2 s, 95th percentile < 5 s) is end-to-end, from capture to decision, and is measured on the sensor in Step 37.
4. **Memory & Footprint Safety:**
   - The saved model is **4.30 MB** (tree depth limited by the chosen `max_depth`); the old 820 MB model is not used.
