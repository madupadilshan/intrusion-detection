# Machine Learning Model Comparison Report (Step 15)

**Generated:** 2026-11-10 18:11:28  
**Execution Runtime:** 639.56 seconds (10.66 minutes)  
**Governing Standard:** Group 03 Research Proposal (Sections 1.3, 2.4, Table 9)  
**Evaluated Data:** `data/processed/train_features.parquet` (1,384,070 flows across 22 scenarios)  
**Cross-Validation:** 5-Fold `StratifiedGroupKFold(random_state=42, groups=scenario_id)`  

---

## 1. Executive Summary & Model Selection Justification

This report presents the empirical comparison of three distinct machine learning algorithmic families for real-time IP-camera IoT network intrusion detection:

1. **Random Forest Classifier (Ensemble - Bagging):** Main prototype model.
2. **Linear Baseline Classifier (Logistic Regression):** Classical linear model with One-Hot categorical encoding and feature standardisation (`StandardScaler`).
3. **Gradient Boosting Classifier (`HistGradientBoostingClassifier`):** State-of-the-art sequential gradient-boosted decision trees.

### Main finding (Level 1, grouped out-of-fold):
- Out-of-fold macro-F1, highest first: Random Forest 0.7009; HistGradientBoosting 0.6746; Logistic Regression 0.6161.
- Highest out-of-fold macro-F1: **Random Forest**.
- Each validation fold contains only scenarios that the model never saw, so these scores show how well a model transfers to new scenarios.

**Model choice:** Random Forest stays the main model of the prototype. The proposal (Section 2.4) keeps it as the main model "because it is easier to look inside its decisions", and asks for this comparison to show whether it gives a good balance between accuracy and speed (Section 1.3). The numbers below are reported as measured, including where another model scores higher.

---

## 2. Comprehensive Model Comparison Matrix

| Evaluation Metric | Random Forest (Bagging) | Logistic Regression (Linear) | HistGradientBoosting (Boosting) | Target / Benchmark |
| :--- | :---: | :---: | :---: | :--- |
| **Out-of-Fold Macro-F1** | **0.7009** | 0.6161 | **0.6746** | reported (no target) |
| **Fold Mean Macro-F1** | **0.6734 ± 0.2114** | 0.5329 ± 0.1975 | 0.5901 ± 0.0972 | reported |
| **Overall Accuracy** | 45.00% | 63.80% | 66.24% | Secondary metric |
| **Recall: `Benign`** | 53.27% | 83.72% | 88.67% | Legitimate flow preservation |
| **Recall: `DDoS_DoS`** | 0.12% | 35.56% | 74.98% | High-rate flood defense |
| **Recall: `PortScan`** | 43.32% | 60.81% | 53.25% | Reconnaissance detection |
| **Recall: `CnC` (Minority)** | **44.89%** | 82.41% | 88.80% | Botnet beacon detection |
| **Recall: `Malware_Download`** | **79.97%** | 81.63% | 66.40% | Payload staging tracking |
| **Benign FPR (IoT-23)** | 4.39% | 16.28% | 11.33% | IoT-23 benign; H1 uses local camera traffic |
| **Inference Latency** | **6.19 µs/flow** | 2.29 µs/flow | 10.39 µs/flow | model step only (end-to-end target: Table 9) |
| **Inference Throughput** | **161,461 flows/s** | 436,150 flows/s | 96,227 flows/s | Higher is better |
| **Final Fit Time (1.38M)** | 115.3 s | 77.1 s | **37.0 s** | Computational footprint |
| **5-Fold CV Time** | 254.2 s | 327.9 s | **188.1 s** | Evaluation efficiency |
| **Model Size on Disk** | 2.64 MB | **0.01 MB** | **0.43 MB** | Embedded edge storage |
| **Interpretability / Audit** | Trees and decision paths can be inspected | Linear weights | Many boosted trees; harder to inspect | Proposal 2.4 |

---

## 3. Notes on each model

- **Random Forest:** main model (proposal 2.4). Its trees can be inspected (Step 17 shows example decision paths). Model size 2.64 MB.
- **Logistic Regression:** linear baseline with one-hot encoding and scaling (scaling only for this model, proposal 3.3). Model size 0.01 MB.
- **HistGradientBoosting:** gradient-boosting comparison model (proposal 1.3). Model size 0.43 MB.
- Inference times are for the model step only on the development PC. The proposal's latency target (Table 9) is end-to-end and is measured in Step 37.

## 4. Next step

All three models are tested once on the held-out scenario `CTU-IoT-Malware-Capture-34-1` in Step 16.
