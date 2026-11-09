# Step 17: Calibration, Explanation and Final Thresholds

**Generated:** 2026-11-09 10:56:30  
**Proposal:** Sections 2.4, 3.4; Table 9; Table 11  
**Model:** Random Forest from Step 14 + calibration `temperature` (one temperature on the log-probabilities (softmax); keeps the raw top class), fitted on grouped out-of-fold data (1,384,070 training flows, 22 scenarios). The method was chosen in Step 17a by the D-044 rule, from out-of-fold data only (`calibration_selection.md`).  
**Held-out scenario (used once, for the final check only):** `CTU-IoT-Malware-Capture-34-1` (23,145 flows)

## 1. What data was used for what

| Part | Data |
| --- | --- |
| Calibration fit | Grouped OOF probabilities from Step 14 (each flow scored by a model that did not see its scenario) |
| Alert thresholds | Calibrated OOF probabilities only |
| Block thresholds | Calibrated OOF probabilities, with the live repeat rule replayed on the flows' time and IPs (D-046) |
| Final check of the deployed model | Held-out 34-1, once, with the fixed thresholds |
| Permutation importance | Held-out 34-1 (proposal 2.4) |

Note: scenario 34-1 was already opened once in Step 16 (raw Random Forest). In this version of Step 17 nothing was chosen from 34-1. Because the team has seen 34-1 results before, this is written down as a limitation.

## 2. Calibration (reliability and Brier score)

Lower Brier score is better. The calibration curve plot uses the OOF data (`calibration_curve.png`).

| Class | OOF raw Brier | OOF calibrated Brier | 34-1 raw Brier | 34-1 calibrated Brier |
| --- | ---: | ---: | ---: | ---: |
| Benign | 0.2580 | 0.1814 | 0.1520 | 0.1166 |
| DDoS_DoS | 0.1480 | 0.1283 | 0.0875 | 0.2282 |
| PortScan | 0.2677 | 0.2319 | 0.0454 | 0.0257 |
| CnC | 0.0885 | 0.0616 | 0.1520 | 0.1520 |
| Malware_Download | 0.1175 | 0.1078 | — | — |

## 3. Thresholds (chosen from calibrated OOF data only)

Rules fixed before looking at any result:
- **Alert threshold (D-040):** lowest value in 0.30–0.99 where OOF alert precision ≥ 0.50.
- **Block threshold (D-046, proposal 3.4: a confidence threshold *and* repeats inside a time window):** the live response rule is replayed on the OOF flows. A block fires when the same target has 3 block candidates of the class within 60 s and is not already blocked (a block lasts 30 min). The block threshold is the lowest value where at least 10 blocks happen, at least 95% of them are fired by a truly malicious flow, and at most 1% of the benign targets are blocked. Otherwise the class is alert only.
- A flow is flagged for class *k* when the model's top class is *k* and its calibrated probability is at least the threshold (the same rule the decision engine uses).
- An automatic block also needs the other safety rules (repeats in the time window, allowlist, local-network protection, maximum rule time, master switch) — see `docs/response_policy.md`.

| Class | Alert threshold | OOF alert precision | OOF alert recall | Block threshold | OOF replay: blocks | fired by malicious flows | benign targets blocked |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DDoS_DoS | 0.33 | 33.56% | 0.16% | none (alert only) | — | — | — |
| PortScan | 0.30 | 57.99% | 30.69% | 0.30 | 413 | 96.61% | 0.010% |
| CnC | 0.39 | 24.28% | 18.85% | 0.39 | 142 | 100.00% | 0.000% |
| Malware_Download | 0.30 | 64.83% | 73.65% | none (alert only) | — | — | — |

Replay of the repeat rule on the OOF data at each threshold (until no block happens):

**DDoS_DoS**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.33 | 25 | 24 | 1 | 4.00% | 1 of 28594 | 2 |
| 0.34 | 24 | 23 | 1 | 4.17% | 1 of 28594 | 2 |
| 0.35 | 22 | 22 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.36 | 20 | 20 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.37 | 20 | 20 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.38 | 20 | 20 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.39 | 20 | 20 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.40 | 20 | 20 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.41 | 17 | 17 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.42 | 16 | 16 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.43 | 16 | 16 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.44 | 16 | 16 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.45 | 16 | 16 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.46 | 16 | 16 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.47 | 8 | 8 | 0 | 0.00% | 1 of 28594 | 1 |
| 0.48 | 0 | 0 | 0 | — | 0 of 28594 | 0 |

**PortScan**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.30 | 413 | 14 | 349 | 96.61% | 3 of 28594 | 8 |
| 0.31 | 395 | 12 | 336 | 96.96% | 3 of 28594 | 8 |
| 0.32 | 355 | 12 | 305 | 96.62% | 3 of 28594 | 7 |
| 0.33 | 355 | 13 | 318 | 96.34% | 3 of 28594 | 7 |
| 0.34 | 355 | 13 | 318 | 96.34% | 3 of 28594 | 7 |
| 0.35 | 355 | 13 | 318 | 96.34% | 3 of 28594 | 7 |
| 0.36 | 335 | 13 | 296 | 96.12% | 3 of 28594 | 6 |
| 0.37 | 335 | 13 | 296 | 96.12% | 3 of 28594 | 6 |
| 0.38 | 333 | 10 | 298 | 97.00% | 3 of 28594 | 5 |
| 0.39 | 333 | 10 | 298 | 97.00% | 3 of 28594 | 5 |
| 0.40 | 332 | 5 | 302 | 98.49% | 2 of 28594 | 5 |
| 0.41 | 332 | 4 | 295 | 98.80% | 2 of 28594 | 5 |
| 0.42 | 301 | 3 | 265 | 99.00% | 1 of 28594 | 5 |
| 0.43 | 135 | 4 | 98 | 97.04% | 2 of 28594 | 4 |
| 0.44 | 135 | 5 | 97 | 96.30% | 2 of 28594 | 4 |
| 0.45 | 87 | 3 | 51 | 96.55% | 1 of 28594 | 3 |
| 0.46 | 87 | 3 | 51 | 96.55% | 1 of 28594 | 3 |
| 0.47 | 84 | 0 | 51 | 100.00% | 0 of 28594 | 2 |
| 0.48 | 48 | 0 | 15 | 100.00% | 0 of 28594 | 1 |
| 0.49 | 48 | 0 | 15 | 100.00% | 0 of 28594 | 1 |
| 0.50 | 0 | 0 | 0 | — | 0 of 28594 | 0 |

**CnC**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.39 | 142 | 0 | 72 | 100.00% | 0 of 260152 | 4 |
| 0.40 | 142 | 0 | 72 | 100.00% | 0 of 260152 | 4 |
| 0.41 | 142 | 0 | 72 | 100.00% | 0 of 260152 | 4 |
| 0.42 | 115 | 0 | 45 | 100.00% | 0 of 260152 | 4 |
| 0.43 | 76 | 0 | 45 | 100.00% | 0 of 260152 | 4 |
| 0.44 | 52 | 0 | 21 | 100.00% | 0 of 260152 | 3 |
| 0.45 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.46 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.47 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.48 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.49 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.50 | 0 | 0 | 0 | — | 0 of 260152 | 0 |

**Malware_Download**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.30 | 5 | 0 | 5 | 100.00% | 0 of 260152 | 5 |
| 0.31 | 5 | 0 | 5 | 100.00% | 0 of 260152 | 5 |
| 0.32 | 5 | 0 | 5 | 100.00% | 0 of 260152 | 5 |
| 0.33 | 5 | 0 | 5 | 100.00% | 0 of 260152 | 5 |
| 0.34 | 5 | 0 | 5 | 100.00% | 0 of 260152 | 5 |
| 0.35 | 5 | 0 | 5 | 100.00% | 0 of 260152 | 5 |
| 0.36 | 5 | 0 | 5 | 100.00% | 0 of 260152 | 5 |
| 0.37 | 5 | 0 | 5 | 100.00% | 0 of 260152 | 5 |
| 0.38 | 5 | 0 | 5 | 100.00% | 0 of 260152 | 5 |
| 0.39 | 5 | 0 | 5 | 100.00% | 0 of 260152 | 5 |
| 0.40 | 5 | 0 | 5 | 100.00% | 0 of 260152 | 5 |
| 0.41 | 4 | 0 | 4 | 100.00% | 0 of 260152 | 4 |
| 0.42 | 4 | 0 | 4 | 100.00% | 0 of 260152 | 4 |
| 0.43 | 4 | 0 | 4 | 100.00% | 0 of 260152 | 4 |
| 0.44 | 4 | 0 | 4 | 100.00% | 0 of 260152 | 4 |
| 0.45 | 4 | 0 | 4 | 100.00% | 0 of 260152 | 4 |
| 0.46 | 4 | 0 | 4 | 100.00% | 0 of 260152 | 4 |
| 0.47 | 3 | 0 | 3 | 100.00% | 0 of 260152 | 3 |
| 0.48 | 3 | 0 | 3 | 100.00% | 0 of 260152 | 3 |
| 0.49 | 3 | 0 | 3 | 100.00% | 0 of 260152 | 3 |
| 0.50 | 3 | 0 | 3 | 100.00% | 0 of 260152 | 3 |
| 0.51 | 3 | 0 | 3 | 100.00% | 0 of 260152 | 3 |
| 0.52 | 2 | 0 | 2 | 100.00% | 0 of 260152 | 2 |
| 0.53 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.54 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.55 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.56 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.57 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.58 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.59 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.60 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.61 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.62 | 1 | 0 | 1 | 100.00% | 0 of 260152 | 1 |
| 0.63 | 0 | 0 | 0 | — | 0 of 260152 | 0 |

Limit: the training data is a sample (at most 50,000 flows per class and scenario), so repeats are rarer than in full traffic. Large attack classes were cut the most, so correct blocks are likely under-counted.


## 4. Final check on the held-out scenario 34-1 (deployed model, fixed thresholds)

- Accuracy: **0.8063**
- Macro-F1 over all 5 classes: **0.4530** (proposal target ≥ 0.85: **not met**)
- Macro-F1 over the classes present in 34-1: **0.5662** (34-1 has no Malware_Download flows)
- Weighted F1: 0.8285
- IoT-23 benign flows predicted as an attack (top class): 5.148%; raising an alert: 2.496%; reaching a block threshold: 2.236%. These are IoT-23 benign flows, **not** the local camera traffic named in Hypothesis H1.

| Class | Support | Precision | Recall | F1 | PR-AUC | Alert precision | Alert recall | Block precision | Block recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Benign | 1,923 | 0.4997 | 0.9485 | 0.6546 | 0.9479 | — | — | — | — |
| DDoS_DoS | 14,394 | 0.9999 | 0.9908 | 0.9953 | 0.9976 | 99.99% | 99.08% | — | — |
| PortScan | 122 | 0.0424 | 0.9426 | 0.0812 | 0.8601 | 4.26% | 94.26% | 4.26% | 94.26% |
| CnC | 6,706 | 0.9781 | 0.3671 | 0.5339 | 0.9859 | 96.08% | 0.73% | 96.08% | 0.73% |
| Malware_Download | 0 | 0.0000 | 0.0000 | 0.0000 | — | 0.00% | 0.00% | — | — |

Replay of the repeat rule on 34-1 with the chosen block thresholds (reported only; nothing chosen from it):

| Class | Threshold | Blocks | Wrong (benign) | Right class | Benign targets blocked |
| --- | ---: | ---: | ---: | ---: | ---: |
| PortScan | 0.30 | 27 | 1 | 1 | 1 of 2 |
| CnC | 0.39 | 1 | 0 | 1 | 0 of 45 |

Confusion matrix (rows = true class, columns = predicted class, order: Benign, DDoS_DoS, PortScan, CnC, Malware_Download):

```
Benign                1,824         0        45        49         5
DDoS_DoS                  0    14,261       133         0         0
PortScan                  0         1       115         6         0
CnC                   1,826         0     2,418     2,462         0
Malware_Download          0         0         0         0         0
```

## 5. Feature importance

Gini importance comes from training. Permutation importance is the drop in macro-F1 (classes present) when one feature is shuffled in a 5,000-flow sample of 34-1 (proposal 2.4). One importance value is not proof of what caused an attack (proposal 3.4).

| Feature | Gini importance | Permutation importance (mean ± std) |
| --- | ---: | ---: |
| `conn_state` | 0.0540 | 0.2286 ± 0.0043 |
| `history` | 0.1284 | 0.2251 ± 0.0021 |
| `duration` | 0.1352 | 0.0994 ± 0.0037 |
| `orig_ip_bytes` | 0.1934 | 0.0591 ± 0.0044 |
| `proto` | 0.0591 | 0.0511 ± 0.0016 |
| `pkt_ratio` | 0.0173 | 0.0140 ± 0.0015 |
| `orig_bytes_per_pkt` | 0.0138 | 0.0056 ± 0.0011 |
| `resp_pkts` | 0.0074 | 0.0031 ± 0.0009 |
| `orig_bytes` | 0.0275 | 0.0026 ± 0.0010 |
| `resp_ip_bytes` | 0.0092 | 0.0012 ± 0.0004 |
| `byte_ratio` | 0.0123 | 0.0008 ± 0.0002 |
| `service` | 0.0014 | 0.0007 ± 0.0001 |
| `is_incomplete_flow` | 0.0011 | 0.0006 ± 0.0001 |
| `missed_bytes` | 0.0000 | 0.0000 ± 0.0000 |
| `resp_bytes_per_pkt` | 0.0016 | -0.0001 ± 0.0001 |
| `resp_bytes` | 0.0022 | -0.0001 ± 0.0002 |
| `orig_port_cat` | 0.0240 | -0.0007 ± 0.0006 |
| `orig_pkts` | 0.0705 | -0.0020 ± 0.0013 |
| `resp_port_cat` | 0.2415 | -0.0730 ± 0.0045 |

## 6. Example decision paths (tree 0 of the forest)

For each class in 34-1, the correctly predicted flow with the highest calibrated probability, followed through the first tree. These are real splits from the trained model, shown as examples only.

**Benign** (calibrated probability 0.7310; first 8 of 9 splits):
1. resp_port_cat = well_known (code 3 > 0.5)
2. resp_port_cat = well_known (code 3 > 2.5)
3. duration = 0.001496 (<= 3.161)
4. pkt_ratio = 0.5 (<= 0.875)
5. orig_pkts = 1 (<= 49)
6. orig_ip_bytes = 76 (<= 117)
7. resp_ip_bytes = 76 (> 42)
8. history = Dd (code 3 <= 27.0)

**DDoS_DoS** (calibrated probability 0.4029; first 8 of 8 splits):
1. resp_port_cat = well_known (code 3 > 0.5)
2. resp_port_cat = well_known (code 3 > 2.5)
3. duration = 0 (<= 3.161)
4. pkt_ratio = 0 (<= 0.875)
5. orig_pkts = 0 (<= 49)
6. orig_ip_bytes = 0 (<= 117)
7. resp_ip_bytes = 0 (<= 42)
8. resp_pkts = 0 (<= 0.5)

**PortScan** (calibrated probability 0.4359; first 5 of 5 splits):
1. resp_port_cat = dynamic (code 0 <= 0.5)
2. pkt_ratio = 1 (> 0.2432)
3. resp_pkts = 0 (<= 0.5)
4. orig_ip_bytes = 40 (<= 59)
5. proto = tcp (code 1 <= 1.5)

**CnC** (calibrated probability 0.4308; first 8 of 15 splits):
1. resp_port_cat = registered (code 2 > 0.5)
2. resp_port_cat = registered (code 2 <= 2.5)
3. orig_pkts = 3 (<= 20.5)
4. history = S (code 8 > 7.5)
5. orig_pkts = 3 (> 2.5)
6. resp_bytes_per_pkt = 0 (<= 0.4583)
7. resp_ip_bytes = 0 (<= 66)
8. duration = 3.101 (> 3)

## 7. Reason codes used by the response policy

The reason codes (`DOS_HIGH_RATE_PACKET_FLOOD`, `SCAN_RAPID_PROBE_SWEEP`, `CNC_PERSISTENT_BEACON`, `MALWARE_STAGING_TRANSFER`) are names the team gave to each class for the audit log. They are **not** rules taken from the model.

## 8. Results per original IoT-23 label — out-of-fold training data (proposal 3.2)

Labels with at least 30 flows. 'Right group' = the model's top class is the group the label belongs to (Table 5 mapping).

| Original label | Group | Flows | Put in the right group | Called an attack |
| --- | --- | ---: | ---: | ---: |
| Benign (no detailed label) | Benign | 345,424 | 54.26% | 45.74% |
| C&C | CnC | 15,289 | 6.27% | 61.76% |
| C&C-FileDownload | Malware_Download | 39 | 79.49% | 84.62% |
| C&C-HeartBeat | CnC | 33,673 | 66.15% | 84.55% |
| C&C-Torii | CnC | 30 | 80.00% | 83.33% |
| DDoS | DDoS_DoS | 239,585 | 0.16% | 21.03% |
| Okiru | Malware_Download | 250,000 | 73.65% | 99.98% |
| PartOfAHorizontalPortScan | PortScan | 499,989 | 38.31% | 78.97% |

## 8. Results per original IoT-23 label — held-out scenario 34-1 (proposal 3.2)

Labels with at least 30 flows. 'Right group' = the model's top class is the group the label belongs to (Table 5 mapping).

| Original label | Group | Flows | Put in the right group | Called an attack |
| --- | --- | ---: | ---: | ---: |
| Benign (no detailed label) | Benign | 1,923 | 94.85% | 5.15% |
| C&C | CnC | 6,706 | 36.71% | 72.77% |
| DDoS | DDoS_DoS | 14,394 | 99.08% | 100.00% |
| PartOfAHorizontalPortScan | PortScan | 122 | 94.26% | 100.00% |

