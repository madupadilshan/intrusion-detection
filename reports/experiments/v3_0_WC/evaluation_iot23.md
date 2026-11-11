# Level 2 Held-Out Scenario Evaluation Report (Step 16)

**Generated:** 2026-11-10 23:12:36  
**Governing Standards:** Group 03 Research Proposal (Sections 1.3, 2.4, 3.4; Table 9; Hypothesis H1; RQ1, RQ2)  
**Evaluated Dataset:** `data/processed/heldout/held_out_test.parquet`  
**Held-out scenario:** `CTU-IoT-Malware-Capture-34-1` (Mirai, 23,145 flows)  
**Use of this scenario:** used only here and in the Step 17 final check, after all choices were made from training data (proposal 3.4). It was first opened in November 2026 for the v1 model (19 features); this model (D-051) was not tuned on it, but its score is reported as measured after the scenario had been seen once. Raw models, top class, no thresholds.  

---

## 1. Summary and Hypothesis H1

> **Hypothesis H1 (proposal Section 1.5):** *"If the IoT-23 flow features are mapped carefully and the Random Forest is trained in a scenario-aware way, then the model will reach a macro-F1 score of at least 0.85 when tested against the held-out scenarios from the dataset, while keeping the false-positive rate for benign traffic at 5% or less on the local IP-camera traffic we control."*

| H1 part | Target | Measured (Random Forest) | Result |
| :--- | :---: | :---: | :--- |
| Macro-F1 on the held-out scenario (5 classes) | >= 0.85 | **0.6596** (classes present: 0.8244) | **not met** |
| Benign FPR on **local IP-camera traffic** | <= 5% | not measured in this step | measured in the lab (Steps 20 and 35) |

For information only (not part of H1): IoT-23 benign flows in 34-1 predicted as an attack = **5.668%** (109 / 1,923). The model inference time is 3.67 µs per flow on the development PC; this is not the end-to-end latency in Table 9 (median < 2 s, p95 < 5 s), which is measured in Step 37.

### Why the macro-F1 is below the target
1. 34-1 has **no Malware_Download flows**. Any Malware_Download prediction is then a false positive, so this class gets F1 = 0 and the 5-class macro-F1 cannot be higher than 0.80. The score over the classes that are present is also reported.
2. Even over the present classes the score is below 0.85. Weak classes (F1 < 0.60): none.
3. The proposal (Section 1.5) names the likely reasons: domain shift between scenarios, feature mismatch, or too few examples in some classes. The per-class table and the confusion matrix below show where the errors are.
4. No label, split or test file was changed after seeing these results. The D-051 changes (window features, trusted-label flag) were decided from the training scenarios only.

---

## 2. Multi-Model Performance Comparison Matrix

| Evaluation Metric | Random Forest (Bagging) | Logistic Regression (Linear) | HistGradientBoosting (Boosting) | Target / Ideal |
| :--- | :---: | :---: | :---: | :--- |
| **Macro-F1 (All 5 Target Classes)** | 0.6596 | 0.5924 | 0.6018 | Benchmark |
| **Macro-F1 (4 Classes Present)** | 0.8244 | 0.7404 | 0.7522 | Benchmark |
| **Overall Accuracy** | 91.58% | 93.80% | 90.48% | Benchmark |
| **Weighted F1-Score** | 0.9222 | 0.9483 | 0.9111 | Benchmark |
| **Macro Precision** | 0.6372 | 0.5700 | 0.5698 | Benchmark |
| **Macro Recall** | 0.7153 | 0.7312 | 0.7091 | Benchmark |
| **Benign FPR (Capture-34-1)** | 5.668% | 5.304% | 5.824% | Benchmark |
| **Inference Latency per Flow** | 3.67 µs | 5.32 µs | 8.18 µs | Benchmark |
| **Inference Throughput** | 272,674 flows/s | 187,993 flows/s | 122,276 flows/s | Benchmark |
| **Level 1 Grouped CV Macro-F1** | 0.7084 | N/A | N/A | Benchmark |
| **Generalisation Gap (L2 - L1)** | -0.0488 | N/A | N/A | Benchmark |

---

## 3. Per-Class Detailed Performance (Random Forest Primary Prototype)

| Class Name | Target Class ID | Support (Flows) | Precision | Recall | F1-Score | PR-AUC | Primary Flow Pattern |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`Benign`** | 0 | 1,923 | 0.5229 | 0.9433 | 0.6728 | 0.9590 | DNS queries, NTP sync, legitimate IoT chatter |
| **`DDoS_DoS`** | 1 | 14,394 | 0.9999 | 0.9895 | 0.9947 | 0.9999 | High-rate UDP/TCP flooding (Mirai attack engine) |
| **`PortScan`** | 2 | 122 | 0.7078 | 0.8934 | 0.7899 | 0.4414 | Reconnaissance SYN sweeps across ports |
| **`CnC`** | 3 | 6,706 | 0.9552 | 0.7502 | 0.8404 | 0.9675 | Periodic botnet beaconing & telemetry |
| **`Malware_Download`** | 4 | 0 | 0.0000 | 0.0000 | 0.0000 | N/A (0 Support) | Payload staging & binary fetches (Absent in 34-1) |

---

## 4. Multi-Class Confusion Matrix (Random Forest)

```
Total Held-Out Flows: 23,145 (Scenario: CTU-IoT-Malware-Capture-34-1)

True \ Pred         Benign    DDoS_DoS    PortScan         CnC    Malware_Download    Total
------------------------------------------------------------------------------------------
Benign               1814           0           5          93                  11     1923
DDoS_DoS               18       14243           2         131                   0    14394
PortScan                0           1         109          12                   0      122
CnC                  1637           0          38        5031                   0     6706
Malware_Download        0           0           0           0                   0        0
------------------------------------------------------------------------------------------

```

Confusion matrix visualization saved to: `reports/experiments/confusion_matrix_heldout.png`.

---

## 5. Level 1 (grouped CV) compared with Level 2 (held-out scenario)

- Level 1 out-of-fold macro-F1 (22 training scenarios): `0.7084`.
- Level 2 macro-F1 on `CTU-IoT-Malware-Capture-34-1`: `0.6596`.
- One held-out scenario is a small test. A score on one scenario does not show how the model works on other scenarios or on camera traffic.

---

## 6. Next step

Step 17 checks the probability calibration and chooses the alert and block thresholds. It uses only the grouped out-of-fold predictions of the training scenarios, never this held-out scenario.