# Step 17: Calibration, Explanation and Final Thresholds

**Generated:** 2026-11-10 18:16:25  
**Proposal:** Sections 2.4, 3.4; Table 9; Table 11  
**Model:** Random Forest from Step 14 + calibration `none` (raw Random Forest probabilities (no calibration)), fitted on grouped out-of-fold data (1,184,004 training flows, 22 scenarios). The method was chosen in Step 17a by the D-044 rule, from out-of-fold data only (`calibration_selection.md`).  
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
| Benign | 0.0560 | 0.0560 | 0.0563 | 0.0563 |
| DDoS_DoS | 0.0778 | 0.0778 | 0.0087 | 0.0087 |
| PortScan | 0.2062 | 0.2062 | 0.0140 | 0.0140 |
| CnC | 0.0214 | 0.0214 | 0.0698 | 0.0698 |
| Malware_Download | 0.1207 | 0.1207 | — | — |

## 3. Thresholds (chosen from calibrated OOF data only)

Rules fixed before looking at any result:
- **Alert threshold (D-040):** lowest value in 0.30–0.99 where OOF alert precision ≥ 0.50.
- **Block threshold (D-046, proposal 3.4: a confidence threshold *and* repeats inside a time window):** the live response rule is replayed on the OOF flows. A block fires when the same target has 3 block candidates of the class within 60 s and is not already blocked (a block lasts 30 min). The block threshold is the lowest value where at least 10 blocks happen, at least 95% of them are fired by a truly malicious flow, and at most 1% of the benign targets are blocked. Otherwise the class is alert only.
- A flow is flagged for class *k* when the model's top class is *k* and its calibrated probability is at least the threshold (the same rule the decision engine uses).
- An automatic block also needs the other safety rules (repeats in the time window, allowlist, local-network protection, maximum rule time, master switch) — see `docs/response_policy.md`.

| Class | Alert threshold | OOF alert precision | OOF alert recall | Block threshold | OOF replay: blocks | fired by malicious flows | benign targets blocked |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DDoS_DoS | 0.30 | 99.07% | 65.14% | none (alert only) | — | — | — |
| PortScan | 0.30 | 68.74% | 53.16% | 0.95 | 95 | 96.84% | 0.003% |
| CnC | 0.30 | 64.09% | 90.71% | 0.30 | 384 | 97.92% | 0.003% |
| Malware_Download | 0.30 | 53.58% | 73.67% | none (alert only) | — | — | — |

Replay of the repeat rule on the OOF data at each threshold (until no block happens):

**DDoS_DoS**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.30 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.31 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.32 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.33 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.34 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.35 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.36 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.37 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.38 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.39 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.40 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.41 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.42 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.43 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.44 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.45 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.46 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.47 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.48 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.49 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.50 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.51 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.52 | 5 | 1 | 4 | 80.00% | 1 of 28594 | 4 |
| 0.53 | 5 | 1 | 4 | 80.00% | 1 of 28594 | 4 |
| 0.54 | 5 | 1 | 4 | 80.00% | 1 of 28594 | 4 |
| 0.55 | 5 | 1 | 4 | 80.00% | 1 of 28594 | 4 |
| 0.56 | 4 | 1 | 3 | 75.00% | 1 of 28594 | 3 |
| 0.57 | 4 | 1 | 3 | 75.00% | 1 of 28594 | 3 |
| 0.58 | 4 | 1 | 3 | 75.00% | 1 of 28594 | 3 |
| 0.59 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.60 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.61 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.62 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.63 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.64 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.65 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.66 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.67 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.68 | 2 | 1 | 1 | 50.00% | 1 of 28594 | 1 |
| 0.69 | 2 | 1 | 1 | 50.00% | 1 of 28594 | 1 |
| 0.70 | 2 | 1 | 1 | 50.00% | 1 of 28594 | 1 |
| 0.71 | 2 | 1 | 1 | 50.00% | 1 of 28594 | 1 |
| 0.72 | 2 | 1 | 1 | 50.00% | 1 of 28594 | 1 |
| 0.73 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.74 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.75 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.76 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.77 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.78 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.79 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.80 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.81 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.82 | 0 | 0 | 0 | — | 0 of 28594 | 0 |

**PortScan**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.30 | 467 | 48 | 391 | 89.72% | 3 of 28594 | 9 |
| 0.31 | 467 | 48 | 391 | 89.72% | 3 of 28594 | 9 |
| 0.32 | 467 | 48 | 391 | 89.72% | 3 of 28594 | 9 |
| 0.33 | 467 | 48 | 391 | 89.72% | 3 of 28594 | 9 |
| 0.34 | 467 | 48 | 391 | 89.72% | 3 of 28594 | 9 |
| 0.35 | 467 | 48 | 391 | 89.72% | 3 of 28594 | 9 |
| 0.36 | 467 | 48 | 391 | 89.72% | 3 of 28594 | 9 |
| 0.37 | 467 | 48 | 391 | 89.72% | 3 of 28594 | 9 |
| 0.38 | 467 | 48 | 391 | 89.72% | 3 of 28594 | 9 |
| 0.39 | 467 | 48 | 391 | 89.72% | 3 of 28594 | 9 |
| 0.40 | 467 | 48 | 391 | 89.72% | 3 of 28594 | 9 |
| 0.41 | 467 | 48 | 391 | 89.72% | 3 of 28594 | 9 |
| 0.42 | 466 | 48 | 391 | 89.70% | 3 of 28594 | 9 |
| 0.43 | 466 | 48 | 391 | 89.70% | 3 of 28594 | 9 |
| 0.44 | 466 | 48 | 391 | 89.70% | 3 of 28594 | 9 |
| 0.45 | 466 | 48 | 391 | 89.70% | 3 of 28594 | 9 |
| 0.46 | 465 | 48 | 390 | 89.68% | 3 of 28594 | 9 |
| 0.47 | 465 | 48 | 390 | 89.68% | 3 of 28594 | 9 |
| 0.48 | 463 | 48 | 388 | 89.63% | 3 of 28594 | 9 |
| 0.49 | 462 | 48 | 387 | 89.61% | 3 of 28594 | 9 |
| 0.50 | 460 | 48 | 385 | 89.57% | 3 of 28594 | 9 |
| 0.51 | 457 | 48 | 382 | 89.50% | 3 of 28594 | 9 |
| 0.52 | 457 | 47 | 383 | 89.72% | 3 of 28594 | 9 |
| 0.53 | 455 | 47 | 381 | 89.67% | 3 of 28594 | 9 |
| 0.54 | 452 | 45 | 380 | 90.04% | 2 of 28594 | 9 |
| 0.55 | 451 | 45 | 379 | 90.02% | 2 of 28594 | 9 |
| 0.56 | 450 | 45 | 378 | 90.00% | 2 of 28594 | 9 |
| 0.57 | 449 | 45 | 377 | 89.98% | 2 of 28594 | 9 |
| 0.58 | 449 | 45 | 377 | 89.98% | 2 of 28594 | 9 |
| 0.59 | 449 | 45 | 377 | 89.98% | 2 of 28594 | 9 |
| 0.60 | 447 | 45 | 375 | 89.93% | 2 of 28594 | 8 |
| 0.61 | 447 | 45 | 375 | 89.93% | 2 of 28594 | 8 |
| 0.62 | 447 | 45 | 375 | 89.93% | 2 of 28594 | 8 |
| 0.63 | 446 | 45 | 374 | 89.91% | 2 of 28594 | 8 |
| 0.64 | 446 | 45 | 374 | 89.91% | 2 of 28594 | 8 |
| 0.65 | 445 | 45 | 373 | 89.89% | 2 of 28594 | 8 |
| 0.66 | 445 | 45 | 373 | 89.89% | 2 of 28594 | 8 |
| 0.67 | 445 | 45 | 364 | 89.89% | 2 of 28594 | 8 |
| 0.68 | 444 | 44 | 364 | 90.09% | 2 of 28594 | 8 |
| 0.69 | 443 | 44 | 362 | 90.07% | 2 of 28594 | 8 |
| 0.70 | 436 | 44 | 354 | 89.91% | 2 of 28594 | 8 |
| 0.71 | 431 | 44 | 350 | 89.79% | 2 of 28594 | 8 |
| 0.72 | 421 | 43 | 347 | 89.79% | 1 of 28594 | 7 |
| 0.73 | 418 | 43 | 344 | 89.71% | 1 of 28594 | 7 |
| 0.74 | 412 | 42 | 343 | 89.81% | 1 of 28594 | 7 |
| 0.75 | 405 | 41 | 333 | 89.88% | 1 of 28594 | 7 |
| 0.76 | 390 | 38 | 321 | 90.26% | 1 of 28594 | 7 |
| 0.77 | 368 | 31 | 306 | 91.58% | 1 of 28594 | 7 |
| 0.78 | 355 | 31 | 293 | 91.27% | 1 of 28594 | 7 |
| 0.79 | 339 | 30 | 278 | 91.15% | 1 of 28594 | 7 |
| 0.80 | 325 | 30 | 263 | 90.77% | 1 of 28594 | 7 |
| 0.81 | 317 | 30 | 255 | 90.54% | 1 of 28594 | 7 |
| 0.82 | 309 | 30 | 248 | 90.29% | 1 of 28594 | 7 |
| 0.83 | 300 | 30 | 239 | 90.00% | 1 of 28594 | 7 |
| 0.84 | 291 | 30 | 231 | 89.69% | 1 of 28594 | 7 |
| 0.85 | 282 | 30 | 223 | 89.36% | 1 of 28594 | 7 |
| 0.86 | 276 | 30 | 217 | 89.13% | 1 of 28594 | 7 |
| 0.87 | 260 | 30 | 201 | 88.46% | 1 of 28594 | 7 |
| 0.88 | 191 | 30 | 131 | 84.29% | 1 of 28594 | 6 |
| 0.89 | 156 | 30 | 96 | 80.77% | 1 of 28594 | 5 |
| 0.90 | 126 | 29 | 67 | 76.98% | 1 of 28594 | 5 |
| 0.91 | 121 | 26 | 66 | 78.51% | 1 of 28594 | 4 |
| 0.92 | 115 | 20 | 62 | 82.61% | 1 of 28594 | 4 |
| 0.93 | 109 | 17 | 63 | 84.40% | 1 of 28594 | 4 |
| 0.94 | 100 | 8 | 64 | 92.00% | 1 of 28594 | 4 |
| 0.95 | 95 | 3 | 65 | 96.84% | 1 of 28594 | 4 |
| 0.96 | 89 | 0 | 55 | 100.00% | 0 of 28594 | 3 |
| 0.97 | 73 | 0 | 58 | 100.00% | 0 of 28594 | 3 |
| 0.98 | 57 | 0 | 42 | 100.00% | 0 of 28594 | 3 |
| 0.99 | 7 | 0 | 1 | 100.00% | 0 of 28594 | 1 |

**CnC**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.30 | 384 | 8 | 303 | 97.92% | 2 of 68621 | 18 |
| 0.31 | 384 | 8 | 303 | 97.92% | 2 of 68621 | 18 |
| 0.32 | 384 | 8 | 303 | 97.92% | 2 of 68621 | 18 |
| 0.33 | 384 | 8 | 303 | 97.92% | 2 of 68621 | 18 |
| 0.34 | 384 | 8 | 303 | 97.92% | 2 of 68621 | 18 |
| 0.35 | 384 | 8 | 303 | 97.92% | 2 of 68621 | 18 |
| 0.36 | 384 | 8 | 303 | 97.92% | 2 of 68621 | 18 |
| 0.37 | 384 | 8 | 303 | 97.92% | 2 of 68621 | 18 |
| 0.38 | 383 | 7 | 303 | 98.17% | 2 of 68621 | 18 |
| 0.39 | 383 | 7 | 303 | 98.17% | 2 of 68621 | 18 |
| 0.40 | 383 | 7 | 303 | 98.17% | 2 of 68621 | 18 |
| 0.41 | 383 | 7 | 303 | 98.17% | 2 of 68621 | 18 |
| 0.42 | 383 | 7 | 303 | 98.17% | 2 of 68621 | 18 |
| 0.43 | 380 | 4 | 303 | 98.95% | 1 of 68621 | 17 |
| 0.44 | 380 | 4 | 303 | 98.95% | 1 of 68621 | 17 |
| 0.45 | 380 | 4 | 303 | 98.95% | 1 of 68621 | 17 |
| 0.46 | 379 | 3 | 303 | 99.21% | 1 of 68621 | 17 |
| 0.47 | 379 | 3 | 303 | 99.21% | 1 of 68621 | 17 |
| 0.48 | 379 | 3 | 303 | 99.21% | 1 of 68621 | 17 |
| 0.49 | 379 | 3 | 303 | 99.21% | 1 of 68621 | 17 |
| 0.50 | 379 | 3 | 303 | 99.21% | 1 of 68621 | 17 |
| 0.51 | 379 | 3 | 303 | 99.21% | 1 of 68621 | 17 |
| 0.52 | 379 | 3 | 303 | 99.21% | 1 of 68621 | 17 |
| 0.53 | 377 | 3 | 302 | 99.20% | 1 of 68621 | 15 |
| 0.54 | 375 | 1 | 302 | 99.73% | 1 of 68621 | 15 |
| 0.55 | 374 | 0 | 302 | 100.00% | 0 of 68621 | 14 |
| 0.56 | 374 | 0 | 302 | 100.00% | 0 of 68621 | 14 |
| 0.57 | 374 | 0 | 302 | 100.00% | 0 of 68621 | 14 |
| 0.58 | 374 | 0 | 302 | 100.00% | 0 of 68621 | 14 |
| 0.59 | 374 | 0 | 302 | 100.00% | 0 of 68621 | 14 |
| 0.60 | 374 | 0 | 302 | 100.00% | 0 of 68621 | 14 |
| 0.61 | 374 | 0 | 302 | 100.00% | 0 of 68621 | 14 |
| 0.62 | 374 | 0 | 302 | 100.00% | 0 of 68621 | 14 |
| 0.63 | 374 | 0 | 302 | 100.00% | 0 of 68621 | 14 |
| 0.64 | 374 | 0 | 302 | 100.00% | 0 of 68621 | 14 |
| 0.65 | 371 | 0 | 300 | 100.00% | 0 of 68621 | 14 |
| 0.66 | 370 | 0 | 299 | 100.00% | 0 of 68621 | 14 |
| 0.67 | 369 | 0 | 299 | 100.00% | 0 of 68621 | 14 |
| 0.68 | 369 | 0 | 299 | 100.00% | 0 of 68621 | 14 |
| 0.69 | 365 | 0 | 298 | 100.00% | 0 of 68621 | 14 |
| 0.70 | 354 | 0 | 298 | 100.00% | 0 of 68621 | 14 |
| 0.71 | 350 | 0 | 298 | 100.00% | 0 of 68621 | 14 |
| 0.72 | 346 | 0 | 297 | 100.00% | 0 of 68621 | 14 |
| 0.73 | 342 | 0 | 296 | 100.00% | 0 of 68621 | 14 |
| 0.74 | 338 | 0 | 296 | 100.00% | 0 of 68621 | 14 |
| 0.75 | 334 | 0 | 296 | 100.00% | 0 of 68621 | 14 |
| 0.76 | 323 | 0 | 286 | 100.00% | 0 of 68621 | 14 |
| 0.77 | 323 | 0 | 286 | 100.00% | 0 of 68621 | 14 |
| 0.78 | 303 | 0 | 266 | 100.00% | 0 of 68621 | 14 |
| 0.79 | 247 | 0 | 210 | 100.00% | 0 of 68621 | 13 |
| 0.80 | 247 | 0 | 210 | 100.00% | 0 of 68621 | 13 |
| 0.81 | 247 | 0 | 210 | 100.00% | 0 of 68621 | 13 |
| 0.82 | 247 | 0 | 209 | 100.00% | 0 of 68621 | 13 |
| 0.83 | 246 | 0 | 209 | 100.00% | 0 of 68621 | 12 |
| 0.84 | 246 | 0 | 209 | 100.00% | 0 of 68621 | 12 |
| 0.85 | 246 | 0 | 209 | 100.00% | 0 of 68621 | 12 |
| 0.86 | 245 | 0 | 208 | 100.00% | 0 of 68621 | 11 |
| 0.87 | 245 | 0 | 208 | 100.00% | 0 of 68621 | 11 |
| 0.88 | 244 | 0 | 207 | 100.00% | 0 of 68621 | 11 |
| 0.89 | 239 | 0 | 207 | 100.00% | 0 of 68621 | 11 |
| 0.90 | 229 | 0 | 206 | 100.00% | 0 of 68621 | 11 |
| 0.91 | 227 | 0 | 205 | 100.00% | 0 of 68621 | 11 |
| 0.92 | 208 | 0 | 200 | 100.00% | 0 of 68621 | 11 |
| 0.93 | 191 | 0 | 191 | 100.00% | 0 of 68621 | 10 |
| 0.94 | 185 | 0 | 185 | 100.00% | 0 of 68621 | 10 |
| 0.95 | 174 | 0 | 174 | 100.00% | 0 of 68621 | 9 |
| 0.96 | 165 | 0 | 165 | 100.00% | 0 of 68621 | 5 |
| 0.97 | 163 | 0 | 163 | 100.00% | 0 of 68621 | 4 |
| 0.98 | 126 | 0 | 126 | 100.00% | 0 of 68621 | 4 |
| 0.99 | 108 | 0 | 108 | 100.00% | 0 of 68621 | 4 |

**Malware_Download**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.30 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.31 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.32 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.33 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.34 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.35 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.36 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.37 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.38 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.39 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.40 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.41 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.42 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.43 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.44 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.45 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.46 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.47 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.48 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.49 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.50 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.51 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.52 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.53 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.54 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.55 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.56 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.57 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.58 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.59 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.60 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.61 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.62 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.63 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.64 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.65 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.66 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.67 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.68 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.69 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.70 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.71 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.72 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.73 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.74 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.75 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.76 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.77 | 3 | 0 | 3 | 100.00% | 0 of 68621 | 3 |
| 0.78 | 3 | 0 | 3 | 100.00% | 0 of 68621 | 3 |
| 0.79 | 3 | 0 | 3 | 100.00% | 0 of 68621 | 3 |
| 0.80 | 3 | 0 | 3 | 100.00% | 0 of 68621 | 3 |
| 0.81 | 2 | 0 | 2 | 100.00% | 0 of 68621 | 2 |
| 0.82 | 2 | 0 | 2 | 100.00% | 0 of 68621 | 2 |
| 0.83 | 2 | 0 | 2 | 100.00% | 0 of 68621 | 2 |
| 0.84 | 2 | 0 | 2 | 100.00% | 0 of 68621 | 2 |
| 0.85 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.86 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.87 | 0 | 0 | 0 | — | 0 of 68621 | 0 |

Limit: the training data is a sample (at most 50,000 flows per class and scenario), so repeats are rarer than in full traffic. Large attack classes were cut the most, so correct blocks are likely under-counted.


## 4. Final check on the held-out scenario 34-1 (deployed model, fixed thresholds)

- Accuracy: **0.9148**
- Macro-F1 over all 5 classes: **0.6337** (proposal target ≥ 0.85: **not met**)
- Macro-F1 over the classes present in 34-1: **0.7921** (34-1 has no Malware_Download flows)
- Weighted F1: 0.9215
- IoT-23 benign flows predicted as an attack (top class): 5.564%; raising an alert: 5.356%; reaching a block threshold: 4.264%. These are IoT-23 benign flows, **not** the local camera traffic named in Hypothesis H1.

| Class | Support | Precision | Recall | F1 | PR-AUC | Alert precision | Alert recall | Block precision | Block recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Benign | 1,923 | 0.5224 | 0.9444 | 0.6727 | 0.9037 | — | — | — | — |
| DDoS_DoS | 14,394 | 0.9999 | 0.9901 | 0.9949 | 0.9999 | 99.99% | 98.94% | — | — |
| PortScan | 122 | 0.5066 | 0.9508 | 0.6610 | 0.3239 | 53.95% | 95.08% | 0.00% | 0.00% |
| CnC | 6,706 | 0.9637 | 0.7441 | 0.8398 | 0.9669 | 96.67% | 74.41% | 96.67% | 74.41% |
| Malware_Download | 0 | 0.0000 | 0.0000 | 0.0000 | — | 0.00% | 0.00% | — | — |

Replay of the repeat rule on 34-1 with the chosen block thresholds (reported only; nothing chosen from it):

| Class | Threshold | Blocks | Wrong (benign) | Right class | Benign targets blocked |
| --- | ---: | ---: | ---: | ---: | ---: |
| PortScan | 0.95 | 0 | 0 | 0 | 0 of 2 |
| CnC | 0.30 | 31 | 2 | 27 | 2 of 45 |

Confusion matrix (rows = true class, columns = predicted class, order: Benign, DDoS_DoS, PortScan, CnC, Malware_Download):

```
Benign                1,816         0        12        86         9
DDoS_DoS                 21    14,251        24        98         0
PortScan                  0         2       116         4         0
CnC                   1,639         0        77     4,990         0
Malware_Download          0         0         0         0         0
```

## 5. Feature importance

Gini importance comes from training. Permutation importance is the drop in macro-F1 (classes present) when one feature is shuffled in a 5,000-flow sample of 34-1 (proposal 2.4). One importance value is not proof of what caused an attack (proposal 3.4).

| Feature | Gini importance | Permutation importance (mean ± std) |
| --- | ---: | ---: |
| `history` | 0.1006 | 0.1651 ± 0.0122 |
| `pair_conn_60s` | 0.0905 | 0.0947 ± 0.0193 |
| `conn_state` | 0.0281 | 0.0657 ± 0.0183 |
| `resp_port_cat` | 0.1298 | 0.0635 ± 0.0055 |
| `duration` | 0.0324 | 0.0625 ± 0.0031 |
| `pair_gap_change` | 0.1091 | 0.0532 ± 0.0023 |
| `src_conn_60s` | 0.0394 | 0.0290 ± 0.0046 |
| `orig_port_cat` | 0.0105 | 0.0148 ± 0.0021 |
| `pair_gap` | 0.0853 | 0.0076 ± 0.0117 |
| `orig_pkts` | 0.0243 | 0.0075 ± 0.0043 |
| `orig_ip_bytes` | 0.0689 | 0.0068 ± 0.0032 |
| `src_udst_60s` | 0.0384 | 0.0067 ± 0.0029 |
| `proto` | 0.0440 | 0.0056 ± 0.0058 |
| `src_uport_60s` | 0.0344 | 0.0052 ± 0.0045 |
| `resp_bytes_per_pkt` | 0.0031 | 0.0035 ± 0.0024 |
| `service` | 0.0033 | 0.0034 ± 0.0010 |
| `resp_pkts` | 0.0065 | 0.0034 ± 0.0031 |
| `is_incomplete_flow` | 0.0023 | 0.0033 ± 0.0025 |
| `byte_ratio` | 0.0102 | 0.0031 ± 0.0029 |
| `pkt_ratio` | 0.0081 | 0.0026 ± 0.0040 |
| `src_udst_ratio` | 0.0776 | 0.0025 ± 0.0039 |
| `resp_ip_bytes` | 0.0072 | 0.0013 ± 0.0025 |
| `orig_bytes_per_pkt` | 0.0237 | 0.0011 ± 0.0029 |
| `resp_bytes` | 0.0032 | 0.0011 ± 0.0016 |
| `missed_bytes` | 0.0000 | 0.0000 ± 0.0000 |
| `orig_bytes` | 0.0191 | -0.0068 ± 0.0022 |

## 6. Example decision paths (tree 0 of the forest)

For each class in 34-1, the correctly predicted flow with the highest calibrated probability, followed through the first tree. These are real splits from the trained model, shown as examples only.

**Benign** (calibrated probability 1.0000; first 3 of 3 splits):
1. orig_ip_bytes = 76 (> 42)
2. history = Dd (code 3 <= 7.5)
3. pkt_ratio = 0.5 (<= 0.9918)

**DDoS_DoS** (calibrated probability 0.9700; first 4 of 4 splits):
1. orig_ip_bytes = 0 (<= 42)
2. pair_gap = 0.001003 (> -0.5)
3. src_conn_60s = 555 (<= 647)
4. src_udst_ratio = 0.001802 (<= 0.002167)

**PortScan** (calibrated probability 0.6606; first 8 of 11 splits):
1. orig_ip_bytes = 1.228e+05 (> 42)
2. history = S (code 8 > 7.5)
3. conn_state = S0 (code 6 > 0.5)
4. src_udst_ratio = 1 (> 0.9966)
5. pkt_ratio = 1 (> 0.9737)
6. duration = 2.735 (<= 3.057)
7. resp_port_cat = dynamic (code 0 <= 1.0)
8. duration = 2.735 (> 5e-07)

**CnC** (calibrated probability 0.9276; first 8 of 11 splits):
1. orig_ip_bytes = 180 (> 42)
2. history = S (code 8 > 7.5)
3. conn_state = S0 (code 6 > 0.5)
4. src_udst_ratio = 1 (> 0.9966)
5. pkt_ratio = 1 (> 0.9737)
6. duration = 3.143 (> 3.057)
7. orig_port_cat = dynamic (code 0 <= 1.0)
8. pair_gap = 14.06 (> -0.5)

## 7. Reason codes used by the response policy

The reason codes (`DOS_HIGH_RATE_PACKET_FLOOD`, `SCAN_RAPID_PROBE_SWEEP`, `CNC_PERSISTENT_BEACON`, `MALWARE_STAGING_TRANSFER`) are names the team gave to each class for the audit log. They are **not** rules taken from the model.

## 8. Results per original IoT-23 label — out-of-fold training data (proposal 3.2)

Labels with at least 30 flows. 'Right group' = the model's top class is the group the label belongs to (Table 5 mapping).

| Original label | Group | Flows | Put in the right group | Called an attack |
| --- | --- | ---: | ---: | ---: |
| Benign (no detailed label) | Benign | 145,358 | 95.61% | 4.39% |
| C&C | CnC | 15,289 | 80.47% | 84.48% |
| C&C-FileDownload | Malware_Download | 39 | 76.92% | 82.05% |
| C&C-HeartBeat | CnC | 33,673 | 95.37% | 95.40% |
| C&C-Torii | CnC | 30 | 80.00% | 93.33% |
| DDoS | DDoS_DoS | 239,585 | 65.14% | 86.01% |
| Okiru | Malware_Download | 250,000 | 73.67% | 99.98% |
| PartOfAHorizontalPortScan | PortScan | 499,989 | 53.16% | 89.98% |

## 8. Results per original IoT-23 label — held-out scenario 34-1 (proposal 3.2)

Labels with at least 30 flows. 'Right group' = the model's top class is the group the label belongs to (Table 5 mapping).

| Original label | Group | Flows | Put in the right group | Called an attack |
| --- | --- | ---: | ---: | ---: |
| Benign (no detailed label) | Benign | 1,923 | 94.44% | 5.56% |
| C&C | CnC | 6,706 | 74.41% | 75.56% |
| DDoS | DDoS_DoS | 14,394 | 99.01% | 99.85% |
| PartOfAHorizontalPortScan | PortScan | 122 | 95.08% | 100.00% |

