# Step 17: Calibration, Explanation and Final Thresholds

**Generated:** 2026-11-10 23:24:06  
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
| Benign | 0.0549 | 0.0549 | 0.0461 | 0.0461 |
| DDoS_DoS | 0.0735 | 0.0735 | 0.0097 | 0.0097 |
| PortScan | 0.1977 | 0.1977 | 0.0125 | 0.0125 |
| CnC | 0.0177 | 0.0177 | 0.0607 | 0.0607 |
| Malware_Download | 0.1167 | 0.1167 | — | — |

## 3. Thresholds (chosen from calibrated OOF data only)

Rules fixed before looking at any result:
- **Alert threshold (D-040):** lowest value in 0.30–0.99 where OOF alert precision ≥ 0.50.
- **Block threshold (D-046, proposal 3.4: a confidence threshold *and* repeats inside a time window):** the live response rule is replayed on the OOF flows. A block fires when the same target has 3 block candidates of the class within 60 s and is not already blocked (a block lasts 30 min). The block threshold is the lowest value where at least 10 blocks happen, at least 95% of them are fired by a truly malicious flow, and at most 1% of the benign targets are blocked. Otherwise the class is alert only.
- A flow is flagged for class *k* when the model's top class is *k* and its calibrated probability is at least the threshold (the same rule the decision engine uses).
- An automatic block also needs the other safety rules (repeats in the time window, allowlist, local-network protection, maximum rule time, master switch) — see `docs/response_policy.md`.

| Class | Alert threshold | OOF alert precision | OOF alert recall | Block threshold | OOF replay: blocks | fired by malicious flows | benign targets blocked |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DDoS_DoS | 0.30 | 98.90% | 66.58% | none (alert only) | — | — | — |
| PortScan | 0.30 | 68.53% | 52.52% | 0.91 | 105 | 97.14% | 0.003% |
| CnC | 0.30 | 65.94% | 94.66% | 0.30 | 381 | 98.69% | 0.003% |
| Malware_Download | 0.30 | 52.69% | 73.68% | none (alert only) | — | — | — |

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
| 0.52 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.53 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.54 | 6 | 1 | 5 | 83.33% | 1 of 28594 | 4 |
| 0.55 | 5 | 1 | 4 | 80.00% | 1 of 28594 | 3 |
| 0.56 | 5 | 1 | 4 | 80.00% | 1 of 28594 | 3 |
| 0.57 | 5 | 1 | 4 | 80.00% | 1 of 28594 | 3 |
| 0.58 | 4 | 1 | 3 | 75.00% | 1 of 28594 | 2 |
| 0.59 | 4 | 1 | 3 | 75.00% | 1 of 28594 | 2 |
| 0.60 | 4 | 1 | 3 | 75.00% | 1 of 28594 | 2 |
| 0.61 | 4 | 1 | 3 | 75.00% | 1 of 28594 | 2 |
| 0.62 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.63 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.64 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.65 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.66 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.67 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.68 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.69 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.70 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.71 | 3 | 1 | 2 | 66.67% | 1 of 28594 | 2 |
| 0.72 | 2 | 1 | 1 | 50.00% | 1 of 28594 | 1 |
| 0.73 | 2 | 1 | 1 | 50.00% | 1 of 28594 | 1 |
| 0.74 | 2 | 1 | 1 | 50.00% | 1 of 28594 | 1 |
| 0.75 | 2 | 1 | 1 | 50.00% | 1 of 28594 | 1 |
| 0.76 | 2 | 1 | 1 | 50.00% | 1 of 28594 | 1 |
| 0.77 | 2 | 1 | 1 | 50.00% | 1 of 28594 | 1 |
| 0.78 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.79 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.80 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.81 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.82 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.83 | 1 | 0 | 1 | 100.00% | 0 of 28594 | 1 |
| 0.84 | 0 | 0 | 0 | — | 0 of 28594 | 0 |

**PortScan**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.30 | 469 | 46 | 392 | 90.19% | 3 of 28594 | 10 |
| 0.31 | 469 | 46 | 392 | 90.19% | 3 of 28594 | 10 |
| 0.32 | 468 | 46 | 392 | 90.17% | 3 of 28594 | 10 |
| 0.33 | 467 | 46 | 392 | 90.15% | 3 of 28594 | 9 |
| 0.34 | 467 | 46 | 392 | 90.15% | 3 of 28594 | 9 |
| 0.35 | 467 | 46 | 392 | 90.15% | 3 of 28594 | 9 |
| 0.36 | 467 | 46 | 392 | 90.15% | 3 of 28594 | 9 |
| 0.37 | 467 | 46 | 392 | 90.15% | 3 of 28594 | 9 |
| 0.38 | 467 | 46 | 392 | 90.15% | 3 of 28594 | 9 |
| 0.39 | 467 | 46 | 392 | 90.15% | 3 of 28594 | 9 |
| 0.40 | 467 | 46 | 392 | 90.15% | 3 of 28594 | 9 |
| 0.41 | 467 | 46 | 392 | 90.15% | 3 of 28594 | 9 |
| 0.42 | 467 | 46 | 392 | 90.15% | 3 of 28594 | 9 |
| 0.43 | 467 | 46 | 392 | 90.15% | 3 of 28594 | 9 |
| 0.44 | 467 | 47 | 392 | 89.94% | 3 of 28594 | 9 |
| 0.45 | 467 | 47 | 392 | 89.94% | 3 of 28594 | 9 |
| 0.46 | 467 | 47 | 392 | 89.94% | 3 of 28594 | 9 |
| 0.47 | 466 | 45 | 393 | 90.34% | 2 of 28594 | 9 |
| 0.48 | 466 | 45 | 393 | 90.34% | 2 of 28594 | 9 |
| 0.49 | 466 | 45 | 393 | 90.34% | 2 of 28594 | 9 |
| 0.50 | 466 | 45 | 393 | 90.34% | 2 of 28594 | 9 |
| 0.51 | 465 | 45 | 392 | 90.32% | 2 of 28594 | 9 |
| 0.52 | 459 | 45 | 386 | 90.20% | 2 of 28594 | 9 |
| 0.53 | 456 | 45 | 383 | 90.13% | 2 of 28594 | 9 |
| 0.54 | 453 | 45 | 380 | 90.07% | 2 of 28594 | 9 |
| 0.55 | 451 | 45 | 378 | 90.02% | 2 of 28594 | 9 |
| 0.56 | 450 | 45 | 377 | 90.00% | 2 of 28594 | 9 |
| 0.57 | 447 | 45 | 375 | 89.93% | 2 of 28594 | 9 |
| 0.58 | 447 | 45 | 375 | 89.93% | 2 of 28594 | 9 |
| 0.59 | 446 | 45 | 367 | 89.91% | 2 of 28594 | 9 |
| 0.60 | 443 | 45 | 362 | 89.84% | 2 of 28594 | 9 |
| 0.61 | 441 | 45 | 360 | 89.80% | 2 of 28594 | 9 |
| 0.62 | 437 | 45 | 356 | 89.70% | 2 of 28594 | 8 |
| 0.63 | 436 | 45 | 355 | 89.68% | 2 of 28594 | 8 |
| 0.64 | 435 | 45 | 354 | 89.66% | 2 of 28594 | 8 |
| 0.65 | 433 | 45 | 356 | 89.61% | 2 of 28594 | 8 |
| 0.66 | 432 | 45 | 354 | 89.58% | 2 of 28594 | 8 |
| 0.67 | 432 | 45 | 359 | 89.58% | 2 of 28594 | 8 |
| 0.68 | 431 | 45 | 358 | 89.56% | 2 of 28594 | 8 |
| 0.69 | 429 | 44 | 357 | 89.74% | 2 of 28594 | 8 |
| 0.70 | 429 | 44 | 355 | 89.74% | 2 of 28594 | 8 |
| 0.71 | 426 | 41 | 357 | 90.38% | 1 of 28594 | 8 |
| 0.72 | 424 | 39 | 356 | 90.80% | 1 of 28594 | 8 |
| 0.73 | 422 | 39 | 355 | 90.76% | 1 of 28594 | 7 |
| 0.74 | 419 | 39 | 357 | 90.69% | 1 of 28594 | 7 |
| 0.75 | 417 | 37 | 357 | 91.13% | 1 of 28594 | 7 |
| 0.76 | 411 | 33 | 349 | 91.97% | 1 of 28594 | 7 |
| 0.77 | 405 | 33 | 343 | 91.85% | 1 of 28594 | 7 |
| 0.78 | 400 | 33 | 338 | 91.75% | 1 of 28594 | 7 |
| 0.79 | 394 | 31 | 334 | 92.13% | 1 of 28594 | 7 |
| 0.80 | 386 | 31 | 326 | 91.97% | 1 of 28594 | 7 |
| 0.81 | 368 | 31 | 308 | 91.58% | 1 of 28594 | 6 |
| 0.82 | 354 | 31 | 294 | 91.24% | 1 of 28594 | 6 |
| 0.83 | 327 | 30 | 268 | 90.83% | 1 of 28594 | 6 |
| 0.84 | 309 | 30 | 250 | 90.29% | 1 of 28594 | 6 |
| 0.85 | 301 | 30 | 240 | 90.03% | 1 of 28594 | 6 |
| 0.86 | 257 | 30 | 197 | 88.33% | 1 of 28594 | 6 |
| 0.87 | 206 | 26 | 153 | 87.38% | 1 of 28594 | 5 |
| 0.88 | 174 | 23 | 125 | 86.78% | 1 of 28594 | 5 |
| 0.89 | 148 | 20 | 101 | 86.49% | 1 of 28594 | 5 |
| 0.90 | 119 | 15 | 75 | 87.39% | 1 of 28594 | 4 |
| 0.91 | 105 | 3 | 73 | 97.14% | 1 of 28594 | 4 |
| 0.92 | 99 | 1 | 70 | 98.99% | 1 of 28594 | 4 |
| 0.93 | 88 | 1 | 70 | 98.86% | 1 of 28594 | 4 |
| 0.94 | 76 | 0 | 62 | 100.00% | 0 of 28594 | 3 |
| 0.95 | 73 | 0 | 58 | 100.00% | 0 of 28594 | 3 |
| 0.96 | 72 | 0 | 56 | 100.00% | 0 of 28594 | 3 |
| 0.97 | 69 | 0 | 53 | 100.00% | 0 of 28594 | 3 |
| 0.98 | 20 | 0 | 6 | 100.00% | 0 of 28594 | 2 |
| 0.99 | 0 | 0 | 0 | — | 0 of 28594 | 0 |

**CnC**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.30 | 381 | 5 | 303 | 98.69% | 2 of 68621 | 17 |
| 0.31 | 381 | 5 | 303 | 98.69% | 2 of 68621 | 17 |
| 0.32 | 381 | 5 | 303 | 98.69% | 2 of 68621 | 17 |
| 0.33 | 380 | 5 | 302 | 98.68% | 2 of 68621 | 17 |
| 0.34 | 379 | 5 | 301 | 98.68% | 2 of 68621 | 17 |
| 0.35 | 379 | 5 | 301 | 98.68% | 2 of 68621 | 17 |
| 0.36 | 379 | 5 | 301 | 98.68% | 2 of 68621 | 17 |
| 0.37 | 377 | 5 | 299 | 98.67% | 2 of 68621 | 17 |
| 0.38 | 377 | 5 | 299 | 98.67% | 2 of 68621 | 17 |
| 0.39 | 377 | 5 | 299 | 98.67% | 2 of 68621 | 17 |
| 0.40 | 375 | 4 | 298 | 98.93% | 2 of 68621 | 17 |
| 0.41 | 374 | 4 | 297 | 98.93% | 2 of 68621 | 17 |
| 0.42 | 374 | 4 | 297 | 98.93% | 2 of 68621 | 17 |
| 0.43 | 371 | 4 | 294 | 98.92% | 2 of 68621 | 17 |
| 0.44 | 370 | 4 | 293 | 98.92% | 2 of 68621 | 17 |
| 0.45 | 370 | 4 | 293 | 98.92% | 2 of 68621 | 17 |
| 0.46 | 370 | 4 | 293 | 98.92% | 2 of 68621 | 17 |
| 0.47 | 369 | 4 | 292 | 98.92% | 2 of 68621 | 17 |
| 0.48 | 365 | 3 | 289 | 99.18% | 1 of 68621 | 17 |
| 0.49 | 363 | 3 | 288 | 99.17% | 1 of 68621 | 16 |
| 0.50 | 363 | 3 | 288 | 99.17% | 1 of 68621 | 16 |
| 0.51 | 363 | 3 | 288 | 99.17% | 1 of 68621 | 16 |
| 0.52 | 363 | 3 | 288 | 99.17% | 1 of 68621 | 16 |
| 0.53 | 361 | 2 | 287 | 99.45% | 1 of 68621 | 16 |
| 0.54 | 361 | 2 | 287 | 99.45% | 1 of 68621 | 16 |
| 0.55 | 361 | 2 | 287 | 99.45% | 1 of 68621 | 16 |
| 0.56 | 361 | 2 | 287 | 99.45% | 1 of 68621 | 16 |
| 0.57 | 361 | 2 | 287 | 99.45% | 1 of 68621 | 16 |
| 0.58 | 361 | 2 | 287 | 99.45% | 1 of 68621 | 16 |
| 0.59 | 360 | 2 | 286 | 99.44% | 1 of 68621 | 16 |
| 0.60 | 358 | 1 | 285 | 99.72% | 1 of 68621 | 16 |
| 0.61 | 358 | 1 | 285 | 99.72% | 1 of 68621 | 16 |
| 0.62 | 357 | 0 | 285 | 100.00% | 0 of 68621 | 15 |
| 0.63 | 357 | 0 | 285 | 100.00% | 0 of 68621 | 15 |
| 0.64 | 357 | 0 | 284 | 100.00% | 0 of 68621 | 15 |
| 0.65 | 356 | 0 | 283 | 100.00% | 0 of 68621 | 15 |
| 0.66 | 355 | 0 | 282 | 100.00% | 0 of 68621 | 15 |
| 0.67 | 353 | 0 | 281 | 100.00% | 0 of 68621 | 14 |
| 0.68 | 353 | 0 | 281 | 100.00% | 0 of 68621 | 14 |
| 0.69 | 352 | 0 | 280 | 100.00% | 0 of 68621 | 13 |
| 0.70 | 352 | 0 | 280 | 100.00% | 0 of 68621 | 13 |
| 0.71 | 352 | 0 | 280 | 100.00% | 0 of 68621 | 13 |
| 0.72 | 352 | 0 | 280 | 100.00% | 0 of 68621 | 13 |
| 0.73 | 352 | 0 | 280 | 100.00% | 0 of 68621 | 13 |
| 0.74 | 352 | 0 | 280 | 100.00% | 0 of 68621 | 13 |
| 0.75 | 351 | 0 | 279 | 100.00% | 0 of 68621 | 13 |
| 0.76 | 347 | 0 | 275 | 100.00% | 0 of 68621 | 13 |
| 0.77 | 344 | 0 | 272 | 100.00% | 0 of 68621 | 13 |
| 0.78 | 344 | 0 | 272 | 100.00% | 0 of 68621 | 13 |
| 0.79 | 342 | 0 | 271 | 100.00% | 0 of 68621 | 13 |
| 0.80 | 341 | 0 | 270 | 100.00% | 0 of 68621 | 13 |
| 0.81 | 272 | 0 | 208 | 100.00% | 0 of 68621 | 13 |
| 0.82 | 251 | 0 | 206 | 100.00% | 0 of 68621 | 13 |
| 0.83 | 228 | 0 | 191 | 100.00% | 0 of 68621 | 13 |
| 0.84 | 228 | 0 | 191 | 100.00% | 0 of 68621 | 13 |
| 0.85 | 228 | 0 | 191 | 100.00% | 0 of 68621 | 13 |
| 0.86 | 227 | 0 | 190 | 100.00% | 0 of 68621 | 13 |
| 0.87 | 227 | 0 | 190 | 100.00% | 0 of 68621 | 13 |
| 0.88 | 227 | 0 | 190 | 100.00% | 0 of 68621 | 13 |
| 0.89 | 225 | 0 | 188 | 100.00% | 0 of 68621 | 12 |
| 0.90 | 225 | 0 | 188 | 100.00% | 0 of 68621 | 12 |
| 0.91 | 225 | 0 | 188 | 100.00% | 0 of 68621 | 12 |
| 0.92 | 224 | 0 | 187 | 100.00% | 0 of 68621 | 12 |
| 0.93 | 222 | 0 | 185 | 100.00% | 0 of 68621 | 11 |
| 0.94 | 218 | 0 | 183 | 100.00% | 0 of 68621 | 9 |
| 0.95 | 191 | 0 | 183 | 100.00% | 0 of 68621 | 9 |
| 0.96 | 183 | 0 | 183 | 100.00% | 0 of 68621 | 8 |
| 0.97 | 180 | 0 | 180 | 100.00% | 0 of 68621 | 7 |
| 0.98 | 168 | 0 | 168 | 100.00% | 0 of 68621 | 6 |
| 0.99 | 130 | 0 | 130 | 100.00% | 0 of 68621 | 4 |

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
| 0.55 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.56 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.57 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.58 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.59 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.60 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.61 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.62 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
| 0.63 | 5 | 0 | 5 | 100.00% | 0 of 68621 | 5 |
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
| 0.77 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.78 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.79 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.80 | 4 | 0 | 4 | 100.00% | 0 of 68621 | 4 |
| 0.81 | 2 | 0 | 2 | 100.00% | 0 of 68621 | 2 |
| 0.82 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.83 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.84 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.85 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.86 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.87 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.88 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.89 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.90 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.91 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.92 | 1 | 0 | 1 | 100.00% | 0 of 68621 | 1 |
| 0.93 | 0 | 0 | 0 | — | 0 of 68621 | 0 |

Limit: the training data is a sample (at most 50,000 flows per class and scenario), so repeats are rarer than in full traffic. Large attack classes were cut the most, so correct blocks are likely under-counted.


## 4. Final check on the held-out scenario 34-1 (deployed model, fixed thresholds)

- Accuracy: **0.9158**
- Macro-F1 over all 5 classes: **0.6596** (proposal target ≥ 0.85: **not met**)
- Macro-F1 over the classes present in 34-1: **0.8244** (34-1 has no Malware_Download flows)
- Weighted F1: 0.9222
- IoT-23 benign flows predicted as an attack (top class): 5.668%; raising an alert: 5.668%; reaching a block threshold: 4.836%. These are IoT-23 benign flows, **not** the local camera traffic named in Hypothesis H1.

| Class | Support | Precision | Recall | F1 | PR-AUC | Alert precision | Alert recall | Block precision | Block recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Benign | 1,923 | 0.5229 | 0.9433 | 0.6728 | 0.9590 | — | — | — | — |
| DDoS_DoS | 14,394 | 0.9999 | 0.9895 | 0.9947 | 0.9999 | 99.99% | 98.95% | — | — |
| PortScan | 122 | 0.7078 | 0.8934 | 0.7899 | 0.4396 | 70.78% | 89.34% | 0.00% | 0.00% |
| CnC | 6,706 | 0.9552 | 0.7502 | 0.8404 | 0.9675 | 95.52% | 75.02% | 95.52% | 75.02% |
| Malware_Download | 0 | 0.0000 | 0.0000 | 0.0000 | — | 0.00% | 0.00% | — | — |

Replay of the repeat rule on 34-1 with the chosen block thresholds (reported only; nothing chosen from it):

| Class | Threshold | Blocks | Wrong (benign) | Right class | Benign targets blocked |
| --- | ---: | ---: | ---: | ---: | ---: |
| PortScan | 0.91 | 0 | 0 | 0 | 0 of 2 |
| CnC | 0.30 | 30 | 2 | 26 | 2 of 45 |

Confusion matrix (rows = true class, columns = predicted class, order: Benign, DDoS_DoS, PortScan, CnC, Malware_Download):

```
Benign                1,814         0         5        93        11
DDoS_DoS                 18    14,243         2       131         0
PortScan                  0         1       109        12         0
CnC                   1,637         0        38     5,031         0
Malware_Download          0         0         0         0         0
```

## 5. Feature importance

Gini importance comes from training. Permutation importance is the drop in macro-F1 (classes present) when one feature is shuffled in a 5,000-flow sample of 34-1 (proposal 2.4). One importance value is not proof of what caused an attack (proposal 3.4).

| Feature | Gini importance | Permutation importance (mean ± std) |
| --- | ---: | ---: |
| `resp_port_cat` | 0.1289 | 0.1855 ± 0.0009 |
| `pair_conn_60s` | 0.1078 | 0.1708 ± 0.0176 |
| `history` | 0.1034 | 0.1340 ± 0.0100 |
| `conn_state` | 0.0339 | 0.0750 ± 0.0109 |
| `duration` | 0.0266 | 0.0395 ± 0.0039 |
| `pair_gap` | 0.0528 | 0.0216 ± 0.0095 |
| `pair_fail_1h` | 0.0978 | 0.0184 ± 0.0085 |
| `pkt_ratio` | 0.0094 | 0.0153 ± 0.0039 |
| `src_udst_ratio` | 0.0552 | 0.0102 ± 0.0084 |
| `orig_port_cat` | 0.0094 | 0.0056 ± 0.0013 |
| `pair_gap_change` | 0.0899 | 0.0046 ± 0.0114 |
| `src_conn_60s` | 0.0347 | 0.0009 ± 0.0024 |
| `missed_bytes` | 0.0000 | 0.0000 ± 0.0000 |
| `is_incomplete_flow` | 0.0012 | 0.0000 ± 0.0000 |
| `byte_ratio` | 0.0102 | 0.0000 ± 0.0000 |
| `service` | 0.0022 | -0.0005 ± 0.0001 |
| `resp_bytes` | 0.0024 | -0.0005 ± 0.0025 |
| `orig_pkts` | 0.0192 | -0.0012 ± 0.0028 |
| `proto` | 0.0467 | -0.0018 ± 0.0052 |
| `orig_bytes` | 0.0114 | -0.0023 ± 0.0013 |
| `resp_bytes_per_pkt` | 0.0018 | -0.0024 ± 0.0002 |
| `src_uport_60s` | 0.0322 | -0.0030 ± 0.0027 |
| `resp_ip_bytes` | 0.0065 | -0.0035 ± 0.0025 |
| `src_udst_60s` | 0.0279 | -0.0043 ± 0.0025 |
| `resp_pkts` | 0.0080 | -0.0050 ± 0.0060 |
| `orig_ip_bytes` | 0.0588 | -0.0063 ± 0.0027 |
| `orig_bytes_per_pkt` | 0.0219 | -0.0256 ± 0.0025 |

## 6. Example decision paths (tree 0 of the forest)

For each class in 34-1, the correctly predicted flow with the highest calibrated probability, followed through the first tree. These are real splits from the trained model, shown as examples only.

**Benign** (calibrated probability 1.0000; first 8 of 11 splits):
1. conn_state = S0 (code 6 > 5.5)
2. pair_conn_60s = 7 (<= 116.5)
3. pair_gap = 10.01 (> 1.431e-06)
4. proto = udp (code 2 > 1.5)
5. pair_gap_change = 0.003491 (<= 230.3)
6. src_udst_ratio = 0.1579 (> 0.06066)
7. pkt_ratio = 1 (> 0.9918)
8. pair_conn_60s = 7 (<= 13.5)

**DDoS_DoS** (calibrated probability 0.9700; first 3 of 3 splits):
1. conn_state = OTH (code 0 <= 5.5)
2. pair_fail_1h = 1.274e+04 (> 2014)
3. is_incomplete_flow = 1 (> 0.5)

**PortScan** (calibrated probability 0.5603; first 8 of 11 splits):
1. conn_state = S0 (code 6 > 5.5)
2. pair_conn_60s = 6 (<= 116.5)
3. pair_gap = 0.5484 (> 1.431e-06)
4. proto = tcp (code 1 <= 1.5)
5. src_conn_60s = 6 (<= 159.5)
6. duration = 0 (<= 3.055)
7. resp_port_cat = dynamic (code 0 <= 2.5)
8. is_incomplete_flow = 1 (> 0.5)

**CnC** (calibrated probability 0.9881; first 8 of 9 splits):
1. conn_state = S0 (code 6 > 5.5)
2. pair_conn_60s = 1 (<= 116.5)
3. pair_gap = 12.07 (> 1.431e-06)
4. proto = tcp (code 1 <= 1.5)
5. src_conn_60s = 1 (<= 159.5)
6. duration = 3.134 (> 3.055)
7. history = S (code 8 <= 8.5)
8. pair_gap_change = 4.878 (> -0.5)

## 7. Reason codes used by the response policy

The reason codes (`DOS_HIGH_RATE_PACKET_FLOOD`, `SCAN_RAPID_PROBE_SWEEP`, `CNC_PERSISTENT_BEACON`, `MALWARE_STAGING_TRANSFER`) are names the team gave to each class for the audit log. They are **not** rules taken from the model.

## 8. Results per original IoT-23 label — out-of-fold training data (proposal 3.2)

Labels with at least 30 flows. 'Right group' = the model's top class is the group the label belongs to (Table 5 mapping).

| Original label | Group | Flows | Put in the right group | Called an attack |
| --- | --- | ---: | ---: | ---: |
| Benign (no detailed label) | Benign | 145,358 | 95.34% | 4.66% |
| C&C | CnC | 15,289 | 83.65% | 84.71% |
| C&C-FileDownload | Malware_Download | 39 | 76.92% | 82.05% |
| C&C-HeartBeat | CnC | 33,673 | 99.67% | 99.70% |
| C&C-Torii | CnC | 30 | 76.67% | 90.00% |
| DDoS | DDoS_DoS | 239,585 | 66.58% | 87.45% |
| Okiru | Malware_Download | 250,000 | 73.68% | 99.98% |
| PartOfAHorizontalPortScan | PortScan | 499,989 | 52.52% | 90.34% |

## 8. Results per original IoT-23 label — held-out scenario 34-1 (proposal 3.2)

Labels with at least 30 flows. 'Right group' = the model's top class is the group the label belongs to (Table 5 mapping).

| Original label | Group | Flows | Put in the right group | Called an attack |
| --- | --- | ---: | ---: | ---: |
| Benign (no detailed label) | Benign | 1,923 | 94.33% | 5.67% |
| C&C | CnC | 6,706 | 75.02% | 75.59% |
| DDoS | DDoS_DoS | 14,394 | 98.95% | 99.87% |
| PartOfAHorizontalPortScan | PortScan | 122 | 89.34% | 100.00% |

