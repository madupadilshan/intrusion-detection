# Machine Learning Model Comparison Report (Step 15)

**Generated:** 2026-11-11 09:46:06  
**Execution Runtime:** 701.05 seconds (11.68 minutes)  
**Governing Standard:** Group 03 Research Proposal (Sections 1.3, 2.4, Table 9)  
**Evaluated Data:** `data/processed/train_features.parquet` (1,182,984 flows across 22 scenarios; training variant WCD)  
**Cross-Validation:** 5-Fold `StratifiedGroupKFold(random_state=42, groups=scenario_id)`  

---

## 1. Executive Summary & Model Selection Justification

This report presents the empirical comparison of three distinct machine learning algorithmic families for real-time IP-camera IoT network intrusion detection:

1. **Random Forest Classifier (Ensemble - Bagging):** Main prototype model.
2. **Linear Baseline Classifier (Logistic Regression):** Classical linear model with One-Hot categorical encoding and feature standardisation (`StandardScaler`).
3. **Gradient Boosting Classifier (`HistGradientBoostingClassifier`):** State-of-the-art sequential gradient-boosted decision trees.

### Main finding (Level 1, grouped out-of-fold):
- Out-of-fold macro-F1, highest first: HistGradientBoosting 0.7391; Random Forest 0.7097; Logistic Regression 0.6257.
- Highest out-of-fold macro-F1: **HistGradientBoosting**.
- Each validation fold contains only scenarios that the model never saw, so these scores show how well a model transfers to new scenarios.

**Model choice:** Random Forest stays the main model of the prototype. The proposal (Section 2.4) keeps it as the main model "because it is easier to look inside its decisions", and asks for this comparison to show whether it gives a good balance between accuracy and speed (Section 1.3). The numbers below are reported as measured, including where another model scores higher.

---

## 2. Comprehensive Model Comparison Matrix

| Evaluation Metric | Random Forest (Bagging) | Logistic Regression (Linear) | HistGradientBoosting (Boosting) | Target / Benchmark |
| :--- | :---: | :---: | :---: | :--- |
| **Out-of-Fold Macro-F1** | **0.7097** | 0.6257 | **0.7391** | reported (no target) |
| **Fold Mean Macro-F1** | **0.6674 ± 0.2119** | 0.5340 ± 0.1935 | 0.6938 ± 0.1549 | reported |
| **Overall Accuracy** | 68.05% | 64.57% | 70.26% | Secondary metric |
| **Recall: `Benign`** | 96.33% | 83.94% | 89.19% | Legitimate flow preservation |
| **Recall: `DDoS_DoS`** | 62.24% | 39.94% | 78.91% | High-rate flood defense |
| **Recall: `PortScan`** | 57.07% | 60.33% | 56.28% | Reconnaissance detection |
| **Recall: `CnC` (Minority)** | **96.42%** | 83.74% | 97.41% | Botnet beacon detection |
| **Recall: `Malware_Download`** | **73.70%** | 81.68% | 73.69% | Payload staging tracking |
| **Benign FPR (IoT-23)** | 3.67% | 16.06% | 10.81% | IoT-23 benign; H1 uses local camera traffic |
| **Inference Latency** | **7.96 µs/flow** | 3.74 µs/flow | 15.85 µs/flow | model step only (end-to-end target: Table 9) |
| **Inference Throughput** | **125,599 flows/s** | 267,511 flows/s | 63,094 flows/s | Higher is better |
| **Final Fit Time (all rows)** | nan s | 98.0 s | **53.9 s** | Computational footprint |
| **5-Fold CV Time** | 283.6 s | 317.8 s | **218.2 s** | Evaluation efficiency |
| **Model Size on Disk** | 8.31 MB | **0.01 MB** | **0.62 MB** | Embedded edge storage |
| **Interpretability / Audit** | Trees and decision paths can be inspected | Linear weights | Many boosted trees; harder to inspect | Proposal 2.4 |

---

## 3. Notes on each model

- **Random Forest:** main model (proposal 2.4). Its trees can be inspected (Step 17 shows example decision paths). Model size 8.31 MB.
- **Logistic Regression:** linear baseline with one-hot encoding and scaling (scaling only for this model, proposal 3.3). Model size 0.01 MB.
- **HistGradientBoosting:** gradient-boosting comparison model (proposal 1.3). Model size 0.62 MB.
- Inference times are for the model step only on the development PC. The proposal's latency target (Table 9) is end-to-end and is measured in Step 37.

## 4. Next step

All three models are tested once on the held-out scenario `CTU-IoT-Malware-Capture-34-1` in Step 16.
