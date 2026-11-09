# Machine Learning Model Comparison Report (Step 15)

**Generated:** 2026-11-09 08:32:32  
**Execution Runtime:** 662.38 seconds (11.04 minutes)  
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
- Out-of-fold macro-F1, highest first: HistGradientBoosting 0.4331; Random Forest 0.3422; Logistic Regression 0.2722.
- Highest out-of-fold macro-F1: **HistGradientBoosting**.
- Each validation fold contains only scenarios that the model never saw, so these scores show how well a model transfers to new scenarios.

**Model choice:** Random Forest stays the main model of the prototype. The proposal (Section 2.4) keeps it as the main model "because it is easier to look inside its decisions", and asks for this comparison to show whether it gives a good balance between accuracy and speed (Section 1.3). The numbers below are reported as measured, including where another model scores higher.

---

## 2. Comprehensive Model Comparison Matrix

| Evaluation Metric | Random Forest (Bagging) | Logistic Regression (Linear) | HistGradientBoosting (Boosting) | Target / Benchmark |
| :--- | :---: | :---: | :---: | :--- |
| **Out-of-Fold Macro-F1** | **0.3422** | 0.2722 | **0.4331** | reported (no target) |
| **Fold Mean Macro-F1** | **0.3353 ± 0.1704** | 0.2723 ± 0.1048 | 0.4160 ± 0.1102 | reported |
| **Overall Accuracy** | 45.00% | 33.09% | 49.50% | Secondary metric |
| **Recall: `Benign`** | 53.27% | 38.13% | 51.73% | Legitimate flow preservation |
| **Recall: `DDoS_DoS`** | 0.12% | 0.63% | 14.46% | High-rate flood defense |
| **Recall: `PortScan`** | 43.32% | 16.88% | 49.90% | Reconnaissance detection |
| **Recall: `CnC` (Minority)** | **44.89%** | 12.81% | 45.47% | Botnet beacon detection |
| **Recall: `Malware_Download`** | **79.97%** | 93.64% | 79.98% | Payload staging tracking |
| **Benign FPR (IoT-23)** | 45.74% | 61.87% | 48.27% | IoT-23 benign; H1 uses local camera traffic |
| **Inference Latency** | **4.66 µs/flow** | 1.52 µs/flow | 17.12 µs/flow | model step only (end-to-end target: Table 9) |
| **Inference Throughput** | **214,454 flows/s** | 658,735 flows/s | 58,414 flows/s | Higher is better |
| **Final Fit Time (1.38M)** | 115.3 s | 67.5 s | **52.8 s** | Computational footprint |
| **5-Fold CV Time** | 286.1 s | 299.4 s | **231.1 s** | Evaluation efficiency |
| **Model Size on Disk** | 4.30 MB | **0.01 MB** | **0.68 MB** | Embedded edge storage |
| **Interpretability / Audit** | Trees and decision paths can be inspected | Linear weights | Many boosted trees; harder to inspect | Proposal 2.4 |

---

## 3. Notes on each model

- **Random Forest:** main model (proposal 2.4). Its trees can be inspected (Step 17 shows example decision paths). Model size 4.30 MB.
- **Logistic Regression:** linear baseline with one-hot encoding and scaling (scaling only for this model, proposal 3.3). Model size 0.01 MB.
- **HistGradientBoosting:** gradient-boosting comparison model (proposal 1.3). Model size 0.68 MB.
- Inference times are for the model step only on the development PC. The proposal's latency target (Table 9) is end-to-end and is measured in Step 37.

## 4. Next step

All three models are tested once on the held-out scenario `CTU-IoT-Malware-Capture-34-1` in Step 16.
