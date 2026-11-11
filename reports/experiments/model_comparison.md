# Machine Learning Model Comparison Report (Step 15)

**Generated:** 2026-11-10 23:12:01  
**Execution Runtime:** 714.17 seconds (11.90 minutes)  
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
- Out-of-fold macro-F1, highest first: Random Forest 0.7084; HistGradientBoosting 0.6947; Logistic Regression 0.6220.
- Highest out-of-fold macro-F1: **Random Forest**.
- Each validation fold contains only scenarios that the model never saw, so these scores show how well a model transfers to new scenarios.

**Model choice:** Random Forest stays the main model of the prototype. The proposal (Section 2.4) keeps it as the main model "because it is easier to look inside its decisions", and asks for this comparison to show whether it gives a good balance between accuracy and speed (Section 1.3). The numbers below are reported as measured, including where another model scores higher.

---

## 2. Comprehensive Model Comparison Matrix

| Evaluation Metric | Random Forest (Bagging) | Logistic Regression (Linear) | HistGradientBoosting (Boosting) | Target / Benchmark |
| :--- | :---: | :---: | :---: | :--- |
| **Out-of-Fold Macro-F1** | **0.7084** | 0.6220 | **0.6947** | reported (no target) |
| **Fold Mean Macro-F1** | **0.6719 ± 0.2045** | 0.5307 ± 0.1936 | 0.6224 ± 0.1885 | reported |
| **Overall Accuracy** | 45.00% | 64.36% | 66.29% | Secondary metric |
| **Recall: `Benign`** | 53.27% | 83.43% | 89.76% | Legitimate flow preservation |
| **Recall: `DDoS_DoS`** | 0.12% | 39.00% | 58.06% | High-rate flood defense |
| **Recall: `PortScan`** | 43.32% | 60.46% | 56.71% | Reconnaissance detection |
| **Recall: `CnC` (Minority)** | **44.89%** | 83.14% | 96.99% | Botnet beacon detection |
| **Recall: `Malware_Download`** | **79.97%** | 81.68% | 73.69% | Payload staging tracking |
| **Benign FPR (IoT-23)** | 4.66% | 16.57% | 10.24% | IoT-23 benign; H1 uses local camera traffic |
| **Inference Latency** | **4.81 µs/flow** | 3.28 µs/flow | 15.19 µs/flow | model step only (end-to-end target: Table 9) |
| **Inference Throughput** | **207,902 flows/s** | 304,945 flows/s | 65,842 flows/s | Higher is better |
| **Final Fit Time (1.38M)** | 115.3 s | 79.2 s | **42.1 s** | Computational footprint |
| **5-Fold CV Time** | 305.2 s | 366.9 s | **213.8 s** | Evaluation efficiency |
| **Model Size on Disk** | 2.41 MB | **0.01 MB** | **0.41 MB** | Embedded edge storage |
| **Interpretability / Audit** | Trees and decision paths can be inspected | Linear weights | Many boosted trees; harder to inspect | Proposal 2.4 |

---

## 3. Notes on each model

- **Random Forest:** main model (proposal 2.4). Its trees can be inspected (Step 17 shows example decision paths). Model size 2.41 MB.
- **Logistic Regression:** linear baseline with one-hot encoding and scaling (scaling only for this model, proposal 3.3). Model size 0.01 MB.
- **HistGradientBoosting:** gradient-boosting comparison model (proposal 1.3). Model size 0.41 MB.
- Inference times are for the model step only on the development PC. The proposal's latency target (Table 9) is end-to-end and is measured in Step 37.

## 4. Next step

All three models are tested once on the held-out scenario `CTU-IoT-Malware-Capture-34-1` in Step 16.
