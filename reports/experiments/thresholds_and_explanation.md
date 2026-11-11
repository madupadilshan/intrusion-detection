# Step 17: Calibration, Explanation and Final Thresholds

**Generated:** 2026-11-11 09:31:23  
**Proposal:** Sections 2.4, 3.4; Table 9; Table 11  
**Model:** Random Forest from Step 14 + calibration `none` (raw Random Forest probabilities (no calibration)), fitted on grouped out-of-fold data (1,182,984 training flows, 22 scenarios). The method was chosen in Step 17a by the D-044 rule, from out-of-fold data only (`calibration_selection.md`).  
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
| Benign | 0.0548 | 0.0548 | 0.0211 | 0.0211 |
| DDoS_DoS | 0.0758 | 0.0758 | 0.0088 | 0.0088 |
| PortScan | 0.1936 | 0.1936 | 0.0139 | 0.0139 |
| CnC | 0.0207 | 0.0207 | 0.0454 | 0.0454 |
| Malware_Download | 0.1175 | 0.1175 | — | — |

## 3. Thresholds (chosen from calibrated OOF data only)

Rules fixed before looking at any result:
- **Alert threshold (D-040):** lowest value in 0.30–0.99 where OOF alert precision ≥ 0.50.
- **Block threshold (D-046, proposal 3.4: a confidence threshold *and* repeats inside a time window):** the live response rule is replayed on the OOF flows. A block fires when the same target has 3 block candidates of the class within 60 s and is not already blocked (a block lasts 30 min). The block threshold is the lowest value where at least 10 blocks happen, at least 95% of them are fired by a truly malicious flow, and at most 1% of the benign targets are blocked. Otherwise the class is alert only.
- **Rate-limit threshold (D-055):** a class with no block threshold whose Table 5 action allows a rate-limit (DDoS_DoS) gets an automatic rate-limit of the outside source from its alert threshold, with the same repeat rule and safety checks. Packets above 200 per second from that source are dropped until the rule ends.
- A flow is flagged for class *k* when the model's top class is *k* and its calibrated probability is at least the threshold (the same rule the decision engine uses).
- An automatic block also needs the other safety rules (repeats in the time window, allowlist, local-network protection, maximum rule time, master switch) — see `docs/response_policy.md`.

| Class | Alert threshold | OOF alert precision | OOF alert recall | Block threshold | OOF replay: blocks | fired by malicious flows | benign targets blocked | Rate-limit threshold (D-055) |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| DDoS_DoS | 0.30 | 98.99% | 62.24% | none | 5 rate-limits | 80.00% | 0.003% | 0.30 |
| PortScan | 0.30 | 70.48% | 57.06% | 0.88 | 141 | 95.04% | 0.003% | — |
| CnC | 0.30 | 64.03% | 96.40% | 0.30 | 381 | 100.00% | 0.000% | — |
| Malware_Download | 0.30 | 57.23% | 73.70% | none (alert only) | — | — | — | — |

Replay of the repeat rule on the OOF data at each threshold (until no block happens):

**DDoS_DoS**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.30 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.31 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.32 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.33 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.34 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.35 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.36 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.37 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.38 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.39 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.40 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.41 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.42 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.43 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.44 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.45 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.46 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.47 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.48 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.49 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.50 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.51 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.52 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.53 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.54 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.55 | 5 | 1 | 4 | 80.00% | 1 of 28593 | 3 |
| 0.56 | 4 | 1 | 3 | 75.00% | 1 of 28593 | 3 |
| 0.57 | 4 | 1 | 3 | 75.00% | 1 of 28593 | 3 |
| 0.58 | 4 | 1 | 3 | 75.00% | 1 of 28593 | 3 |
| 0.59 | 4 | 1 | 3 | 75.00% | 1 of 28593 | 3 |
| 0.60 | 4 | 1 | 3 | 75.00% | 1 of 28593 | 3 |
| 0.61 | 4 | 1 | 3 | 75.00% | 1 of 28593 | 3 |
| 0.62 | 4 | 1 | 3 | 75.00% | 1 of 28593 | 3 |
| 0.63 | 4 | 1 | 3 | 75.00% | 1 of 28593 | 3 |
| 0.64 | 4 | 1 | 3 | 75.00% | 1 of 28593 | 3 |
| 0.65 | 3 | 1 | 2 | 66.67% | 1 of 28593 | 2 |
| 0.66 | 3 | 1 | 2 | 66.67% | 1 of 28593 | 2 |
| 0.67 | 3 | 1 | 2 | 66.67% | 1 of 28593 | 2 |
| 0.68 | 2 | 1 | 1 | 50.00% | 1 of 28593 | 1 |
| 0.69 | 2 | 1 | 1 | 50.00% | 1 of 28593 | 1 |
| 0.70 | 2 | 1 | 1 | 50.00% | 1 of 28593 | 1 |
| 0.71 | 2 | 1 | 1 | 50.00% | 1 of 28593 | 1 |
| 0.72 | 2 | 1 | 1 | 50.00% | 1 of 28593 | 1 |
| 0.73 | 1 | 0 | 1 | 100.00% | 0 of 28593 | 1 |
| 0.74 | 1 | 0 | 1 | 100.00% | 0 of 28593 | 1 |
| 0.75 | 1 | 0 | 1 | 100.00% | 0 of 28593 | 1 |
| 0.76 | 1 | 0 | 1 | 100.00% | 0 of 28593 | 1 |
| 0.77 | 1 | 0 | 1 | 100.00% | 0 of 28593 | 1 |
| 0.78 | 1 | 0 | 1 | 100.00% | 0 of 28593 | 1 |
| 0.79 | 1 | 0 | 1 | 100.00% | 0 of 28593 | 1 |
| 0.80 | 1 | 0 | 1 | 100.00% | 0 of 28593 | 1 |
| 0.81 | 1 | 0 | 1 | 100.00% | 0 of 28593 | 1 |
| 0.82 | 0 | 0 | 0 | — | 0 of 28593 | 0 |

**PortScan**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.30 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.31 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.32 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.33 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.34 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.35 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.36 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.37 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.38 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.39 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.40 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.41 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.42 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.43 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.44 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.45 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.46 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.47 | 467 | 45 | 394 | 90.36% | 2 of 28593 | 9 |
| 0.48 | 465 | 45 | 392 | 90.32% | 2 of 28593 | 9 |
| 0.49 | 463 | 45 | 390 | 90.28% | 2 of 28593 | 9 |
| 0.50 | 458 | 45 | 386 | 90.17% | 2 of 28593 | 9 |
| 0.51 | 456 | 45 | 384 | 90.13% | 2 of 28593 | 9 |
| 0.52 | 454 | 45 | 382 | 90.09% | 2 of 28593 | 9 |
| 0.53 | 452 | 45 | 377 | 90.04% | 2 of 28593 | 9 |
| 0.54 | 451 | 45 | 378 | 90.02% | 2 of 28593 | 9 |
| 0.55 | 450 | 45 | 377 | 90.00% | 2 of 28593 | 9 |
| 0.56 | 448 | 45 | 375 | 89.96% | 2 of 28593 | 9 |
| 0.57 | 439 | 45 | 366 | 89.75% | 2 of 28593 | 9 |
| 0.58 | 439 | 45 | 366 | 89.75% | 2 of 28593 | 9 |
| 0.59 | 437 | 45 | 364 | 89.70% | 2 of 28593 | 9 |
| 0.60 | 436 | 45 | 363 | 89.68% | 2 of 28593 | 9 |
| 0.61 | 435 | 45 | 362 | 89.66% | 2 of 28593 | 9 |
| 0.62 | 433 | 46 | 359 | 89.38% | 3 of 28593 | 8 |
| 0.63 | 432 | 45 | 359 | 89.58% | 2 of 28593 | 7 |
| 0.64 | 431 | 45 | 358 | 89.56% | 2 of 28593 | 7 |
| 0.65 | 431 | 45 | 358 | 89.56% | 2 of 28593 | 7 |
| 0.66 | 431 | 45 | 358 | 89.56% | 2 of 28593 | 7 |
| 0.67 | 430 | 45 | 357 | 89.53% | 2 of 28593 | 7 |
| 0.68 | 430 | 45 | 357 | 89.53% | 2 of 28593 | 7 |
| 0.69 | 428 | 45 | 355 | 89.49% | 2 of 28593 | 7 |
| 0.70 | 427 | 43 | 354 | 89.93% | 1 of 28593 | 7 |
| 0.71 | 425 | 43 | 352 | 89.88% | 1 of 28593 | 7 |
| 0.72 | 423 | 43 | 350 | 89.83% | 1 of 28593 | 7 |
| 0.73 | 422 | 42 | 350 | 90.05% | 1 of 28593 | 7 |
| 0.74 | 415 | 39 | 346 | 90.60% | 1 of 28593 | 7 |
| 0.75 | 410 | 39 | 340 | 90.49% | 1 of 28593 | 7 |
| 0.76 | 400 | 35 | 336 | 91.25% | 1 of 28593 | 7 |
| 0.77 | 388 | 34 | 325 | 91.24% | 1 of 28593 | 7 |
| 0.78 | 383 | 31 | 323 | 91.91% | 1 of 28593 | 7 |
| 0.79 | 380 | 31 | 319 | 91.84% | 1 of 28593 | 7 |
| 0.80 | 371 | 30 | 311 | 91.91% | 1 of 28593 | 7 |
| 0.81 | 356 | 30 | 296 | 91.57% | 1 of 28593 | 7 |
| 0.82 | 331 | 28 | 273 | 91.54% | 1 of 28593 | 7 |
| 0.83 | 291 | 27 | 234 | 90.72% | 1 of 28593 | 5 |
| 0.84 | 246 | 24 | 194 | 90.24% | 1 of 28593 | 5 |
| 0.85 | 235 | 24 | 184 | 89.79% | 1 of 28593 | 5 |
| 0.86 | 214 | 24 | 164 | 88.79% | 1 of 28593 | 5 |
| 0.87 | 171 | 21 | 124 | 87.72% | 1 of 28593 | 5 |
| 0.88 | 141 | 7 | 108 | 95.04% | 1 of 28593 | 5 |
| 0.89 | 127 | 3 | 96 | 97.64% | 1 of 28593 | 5 |
| 0.90 | 105 | 0 | 77 | 100.00% | 0 of 28593 | 4 |
| 0.91 | 101 | 0 | 73 | 100.00% | 0 of 28593 | 3 |
| 0.92 | 101 | 0 | 73 | 100.00% | 0 of 28593 | 3 |
| 0.93 | 97 | 0 | 69 | 100.00% | 0 of 28593 | 3 |
| 0.94 | 96 | 0 | 70 | 100.00% | 0 of 28593 | 3 |
| 0.95 | 94 | 0 | 77 | 100.00% | 0 of 28593 | 3 |
| 0.96 | 92 | 0 | 87 | 100.00% | 0 of 28593 | 3 |
| 0.97 | 75 | 0 | 69 | 100.00% | 0 of 28593 | 3 |
| 0.98 | 9 | 0 | 9 | 100.00% | 0 of 28593 | 1 |
| 0.99 | 0 | 0 | 0 | — | 0 of 28593 | 0 |

**CnC**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.30 | 381 | 0 | 305 | 100.00% | 0 of 68620 | 16 |
| 0.31 | 379 | 0 | 303 | 100.00% | 0 of 68620 | 16 |
| 0.32 | 376 | 0 | 302 | 100.00% | 0 of 68620 | 16 |
| 0.33 | 375 | 0 | 302 | 100.00% | 0 of 68620 | 16 |
| 0.34 | 375 | 0 | 302 | 100.00% | 0 of 68620 | 16 |
| 0.35 | 374 | 0 | 301 | 100.00% | 0 of 68620 | 16 |
| 0.36 | 372 | 0 | 299 | 100.00% | 0 of 68620 | 16 |
| 0.37 | 371 | 0 | 298 | 100.00% | 0 of 68620 | 16 |
| 0.38 | 370 | 0 | 297 | 100.00% | 0 of 68620 | 16 |
| 0.39 | 369 | 0 | 296 | 100.00% | 0 of 68620 | 16 |
| 0.40 | 368 | 0 | 295 | 100.00% | 0 of 68620 | 16 |
| 0.41 | 367 | 0 | 294 | 100.00% | 0 of 68620 | 16 |
| 0.42 | 366 | 0 | 293 | 100.00% | 0 of 68620 | 16 |
| 0.43 | 365 | 0 | 292 | 100.00% | 0 of 68620 | 16 |
| 0.44 | 363 | 0 | 290 | 100.00% | 0 of 68620 | 16 |
| 0.45 | 363 | 0 | 290 | 100.00% | 0 of 68620 | 16 |
| 0.46 | 362 | 0 | 289 | 100.00% | 0 of 68620 | 16 |
| 0.47 | 362 | 0 | 289 | 100.00% | 0 of 68620 | 16 |
| 0.48 | 362 | 0 | 289 | 100.00% | 0 of 68620 | 16 |
| 0.49 | 361 | 0 | 288 | 100.00% | 0 of 68620 | 16 |
| 0.50 | 360 | 0 | 287 | 100.00% | 0 of 68620 | 16 |
| 0.51 | 360 | 0 | 287 | 100.00% | 0 of 68620 | 16 |
| 0.52 | 360 | 0 | 287 | 100.00% | 0 of 68620 | 16 |
| 0.53 | 360 | 0 | 287 | 100.00% | 0 of 68620 | 16 |
| 0.54 | 359 | 0 | 286 | 100.00% | 0 of 68620 | 16 |
| 0.55 | 358 | 0 | 285 | 100.00% | 0 of 68620 | 16 |
| 0.56 | 358 | 0 | 285 | 100.00% | 0 of 68620 | 16 |
| 0.57 | 357 | 0 | 284 | 100.00% | 0 of 68620 | 16 |
| 0.58 | 357 | 0 | 284 | 100.00% | 0 of 68620 | 16 |
| 0.59 | 356 | 0 | 283 | 100.00% | 0 of 68620 | 16 |
| 0.60 | 356 | 0 | 283 | 100.00% | 0 of 68620 | 16 |
| 0.61 | 356 | 0 | 283 | 100.00% | 0 of 68620 | 16 |
| 0.62 | 356 | 0 | 283 | 100.00% | 0 of 68620 | 16 |
| 0.63 | 356 | 0 | 283 | 100.00% | 0 of 68620 | 16 |
| 0.64 | 355 | 0 | 283 | 100.00% | 0 of 68620 | 15 |
| 0.65 | 354 | 0 | 282 | 100.00% | 0 of 68620 | 15 |
| 0.66 | 354 | 0 | 282 | 100.00% | 0 of 68620 | 15 |
| 0.67 | 354 | 0 | 281 | 100.00% | 0 of 68620 | 15 |
| 0.68 | 354 | 0 | 281 | 100.00% | 0 of 68620 | 15 |
| 0.69 | 354 | 0 | 281 | 100.00% | 0 of 68620 | 15 |
| 0.70 | 354 | 0 | 281 | 100.00% | 0 of 68620 | 15 |
| 0.71 | 353 | 0 | 281 | 100.00% | 0 of 68620 | 14 |
| 0.72 | 353 | 0 | 281 | 100.00% | 0 of 68620 | 14 |
| 0.73 | 353 | 0 | 281 | 100.00% | 0 of 68620 | 14 |
| 0.74 | 353 | 0 | 281 | 100.00% | 0 of 68620 | 14 |
| 0.75 | 353 | 0 | 281 | 100.00% | 0 of 68620 | 14 |
| 0.76 | 353 | 0 | 281 | 100.00% | 0 of 68620 | 14 |
| 0.77 | 352 | 0 | 280 | 100.00% | 0 of 68620 | 14 |
| 0.78 | 350 | 0 | 278 | 100.00% | 0 of 68620 | 14 |
| 0.79 | 348 | 0 | 276 | 100.00% | 0 of 68620 | 14 |
| 0.80 | 338 | 0 | 266 | 100.00% | 0 of 68620 | 14 |
| 0.81 | 308 | 0 | 236 | 100.00% | 0 of 68620 | 14 |
| 0.82 | 277 | 0 | 205 | 100.00% | 0 of 68620 | 13 |
| 0.83 | 266 | 0 | 195 | 100.00% | 0 of 68620 | 13 |
| 0.84 | 260 | 0 | 190 | 100.00% | 0 of 68620 | 13 |
| 0.85 | 257 | 0 | 190 | 100.00% | 0 of 68620 | 13 |
| 0.86 | 254 | 0 | 190 | 100.00% | 0 of 68620 | 13 |
| 0.87 | 249 | 0 | 190 | 100.00% | 0 of 68620 | 13 |
| 0.88 | 240 | 0 | 189 | 100.00% | 0 of 68620 | 13 |
| 0.89 | 234 | 0 | 189 | 100.00% | 0 of 68620 | 13 |
| 0.90 | 226 | 0 | 188 | 100.00% | 0 of 68620 | 12 |
| 0.91 | 223 | 0 | 186 | 100.00% | 0 of 68620 | 11 |
| 0.92 | 222 | 0 | 185 | 100.00% | 0 of 68620 | 10 |
| 0.93 | 221 | 0 | 184 | 100.00% | 0 of 68620 | 9 |
| 0.94 | 219 | 0 | 184 | 100.00% | 0 of 68620 | 9 |
| 0.95 | 199 | 0 | 184 | 100.00% | 0 of 68620 | 9 |
| 0.96 | 183 | 0 | 183 | 100.00% | 0 of 68620 | 7 |
| 0.97 | 181 | 0 | 181 | 100.00% | 0 of 68620 | 6 |
| 0.98 | 172 | 0 | 172 | 100.00% | 0 of 68620 | 6 |
| 0.99 | 150 | 0 | 150 | 100.00% | 0 of 68620 | 5 |

**Malware_Download**

| Threshold | Blocks | Wrong (benign) | Right class | Fired by malicious | Benign targets blocked | Scenarios |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 0.30 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.31 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.32 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.33 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.34 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.35 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.36 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.37 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.38 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.39 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.40 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.41 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.42 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.43 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.44 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.45 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.46 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.47 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.48 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.49 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.50 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.51 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.52 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.53 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.54 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.55 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.56 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.57 | 5 | 0 | 5 | 100.00% | 0 of 68620 | 5 |
| 0.58 | 4 | 0 | 4 | 100.00% | 0 of 68620 | 4 |
| 0.59 | 4 | 0 | 4 | 100.00% | 0 of 68620 | 4 |
| 0.60 | 4 | 0 | 4 | 100.00% | 0 of 68620 | 4 |
| 0.61 | 4 | 0 | 4 | 100.00% | 0 of 68620 | 4 |
| 0.62 | 4 | 0 | 4 | 100.00% | 0 of 68620 | 4 |
| 0.63 | 4 | 0 | 4 | 100.00% | 0 of 68620 | 4 |
| 0.64 | 4 | 0 | 4 | 100.00% | 0 of 68620 | 4 |
| 0.65 | 4 | 0 | 4 | 100.00% | 0 of 68620 | 4 |
| 0.66 | 4 | 0 | 4 | 100.00% | 0 of 68620 | 4 |
| 0.67 | 4 | 0 | 4 | 100.00% | 0 of 68620 | 4 |
| 0.68 | 3 | 0 | 3 | 100.00% | 0 of 68620 | 3 |
| 0.69 | 3 | 0 | 3 | 100.00% | 0 of 68620 | 3 |
| 0.70 | 3 | 0 | 3 | 100.00% | 0 of 68620 | 3 |
| 0.71 | 3 | 0 | 3 | 100.00% | 0 of 68620 | 3 |
| 0.72 | 3 | 0 | 3 | 100.00% | 0 of 68620 | 3 |
| 0.73 | 3 | 0 | 3 | 100.00% | 0 of 68620 | 3 |
| 0.74 | 3 | 0 | 3 | 100.00% | 0 of 68620 | 3 |
| 0.75 | 2 | 0 | 2 | 100.00% | 0 of 68620 | 2 |
| 0.76 | 2 | 0 | 2 | 100.00% | 0 of 68620 | 2 |
| 0.77 | 1 | 0 | 1 | 100.00% | 0 of 68620 | 1 |
| 0.78 | 1 | 0 | 1 | 100.00% | 0 of 68620 | 1 |
| 0.79 | 1 | 0 | 1 | 100.00% | 0 of 68620 | 1 |
| 0.80 | 0 | 0 | 0 | — | 0 of 68620 | 0 |

Limit: the training data is a sample (at most 50,000 flows per class and scenario), so repeats are rarer than in full traffic. Large attack classes were cut the most, so correct blocks are likely under-counted.


## 4. Final check on the held-out scenario 34-1 (deployed model, fixed thresholds)

- Accuracy: **0.9322**
- Macro-F1 over all 5 classes: **0.6876** (proposal target ≥ 0.85: **not met**)
- Macro-F1 over the classes present in 34-1: **0.8595** (34-1 has no Malware_Download flows)
- Weighted F1: 0.9367
- IoT-23 benign flows predicted as an attack (top class): 5.616%; raising an alert: 5.616%; reaching a block threshold: 4.888%; reaching a rate-limit threshold: 0.000%. These are IoT-23 benign flows, **not** the local camera traffic named in Hypothesis H1.

| Class | Support | Precision | Recall | F1 | PR-AUC | Alert precision | Alert recall | Block precision | Block recall |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Benign | 1,923 | 0.5836 | 0.9438 | 0.7212 | 0.9616 | — | — | — | — |
| DDoS_DoS | 14,394 | 1.0000 | 0.9894 | 0.9947 | 0.9997 | 100.00% | 98.94% | — | — |
| PortScan | 122 | 0.7793 | 0.9262 | 0.8464 | 0.4905 | 77.93% | 92.62% | 0.00% | 0.00% |
| CnC | 6,706 | 0.9587 | 0.8061 | 0.8758 | 0.9728 | 95.87% | 80.61% | 95.87% | 80.61% |
| Malware_Download | 0 | 0.0000 | 0.0000 | 0.0000 | — | 0.00% | 0.00% | — | — |

Replay of the repeat rule on 34-1 with the chosen block thresholds (reported only; nothing chosen from it):

| Class | Threshold | Blocks | Wrong (benign) | Right class | Benign targets blocked |
| --- | ---: | ---: | ---: | ---: | ---: |
| DDoS_DoS (rate-limit) | 0.30 | 1 | 0 | 1 | 0 of 2 |
| PortScan | 0.88 | 0 | 0 | 0 | 0 of 2 |
| CnC | 0.30 | 31 | 2 | 27 | 2 of 45 |

Confusion matrix (rows = true class, columns = predicted class, order: Benign, DDoS_DoS, PortScan, CnC, Malware_Download):

```
Benign                1,815         0         4        94        10
DDoS_DoS                 20    14,241         2       131         0
PortScan                  1         0       113         8         0
CnC                   1,274         0        26     5,406         0
Malware_Download          0         0         0         0         0
```

## 5. Feature importance

Gini importance comes from training. Permutation importance is the drop in macro-F1 (classes present) when one feature is shuffled in a 5,000-flow sample of 34-1 (proposal 2.4). One importance value is not proof of what caused an attack (proposal 3.4).

| Feature | Gini importance | Permutation importance (mean ± std) |
| --- | ---: | ---: |
| `pair_conn_60s` | 0.1023 | 0.1655 ± 0.0175 |
| `history` | 0.0920 | 0.1411 ± 0.0087 |
| `resp_port_cat` | 0.1465 | 0.1219 ± 0.0031 |
| `duration` | 0.0239 | 0.0549 ± 0.0060 |
| `src_udst_ratio` | 0.0574 | 0.0301 ± 0.0046 |
| `pkt_ratio` | 0.0112 | 0.0278 ± 0.0090 |
| `orig_ip_bytes` | 0.0645 | 0.0233 ± 0.0018 |
| `conn_state` | 0.0278 | 0.0211 ± 0.0059 |
| `pair_fail_1h` | 0.0946 | 0.0095 ± 0.0058 |
| `orig_pkts` | 0.0216 | 0.0090 ± 0.0019 |
| `service` | 0.0022 | 0.0067 ± 0.0001 |
| `resp_bytes_per_pkt` | 0.0017 | 0.0062 ± 0.0003 |
| `pair_gap_change` | 0.1029 | 0.0053 ± 0.0065 |
| `proto` | 0.0409 | 0.0018 ± 0.0014 |
| `is_incomplete_flow` | 0.0017 | 0.0014 ± 0.0018 |
| `orig_port_cat` | 0.0114 | 0.0004 ± 0.0037 |
| `missed_bytes` | 0.0000 | 0.0000 ± 0.0000 |
| `pair_gap` | 0.0372 | -0.0005 ± 0.0053 |
| `src_uport_60s` | 0.0357 | -0.0010 ± 0.0031 |
| `resp_bytes` | 0.0019 | -0.0025 ± 0.0016 |
| `resp_ip_bytes` | 0.0091 | -0.0028 ± 0.0015 |
| `resp_pkts` | 0.0096 | -0.0045 ± 0.0036 |
| `src_conn_60s` | 0.0309 | -0.0081 ± 0.0044 |
| `orig_bytes` | 0.0119 | -0.0089 ± 0.0017 |
| `byte_ratio` | 0.0120 | -0.0091 ± 0.0013 |
| `src_udst_60s` | 0.0338 | -0.0098 ± 0.0031 |
| `orig_bytes_per_pkt` | 0.0152 | -0.0110 ± 0.0007 |

## 6. Example decision paths (tree 0 of the forest)

For each class in 34-1, the correctly predicted flow with the highest calibrated probability, followed through the first tree. These are real splits from the trained model, shown as examples only.

**Benign** (calibrated probability 1.0000; first 6 of 6 splits):
1. conn_state = SF (code 9 > 5.5)
2. pair_gap_change = -1 (<= -0.5)
3. orig_ip_bytes = 76 (<= 401)
4. pair_fail_1h = 0 (<= 0.5)
5. orig_port_cat = well_known (code 3 > 1.0)
6. orig_bytes_per_pkt = 48 (> 14.75)

**DDoS_DoS** (calibrated probability 0.9900; first 4 of 4 splits):
1. conn_state = OTH (code 0 <= 5.5)
2. pair_fail_1h = 4579 (> 2026)
3. orig_bytes_per_pkt = 0 (<= 0.3125)
4. conn_state = OTH (code 0 <= 1.0)

**PortScan** (calibrated probability 0.5782; first 8 of 10 splits):
1. conn_state = S0 (code 6 > 5.5)
2. pair_gap_change = -1 (<= -0.5)
3. orig_ip_bytes = 1.228e+05 (> 401)
4. src_udst_60s = 1 (<= 2.867e+04)
5. proto = tcp (code 1 <= 1.5)
6. duration = 2.735 (<= 318)
7. orig_bytes = 0 (<= 71.5)
8. src_uport_60s = 1 (<= 1.5)

**CnC** (calibrated probability 0.9899; first 8 of 11 splits):
1. conn_state = S0 (code 6 > 5.5)
2. pair_gap_change = 3.902 (> -0.5)
3. proto = tcp (code 1 <= 1.5)
4. duration = 3.095 (> 3.054)
5. resp_ip_bytes = 0 (<= 1246)
6. orig_bytes = 0 (<= 72)
7. pair_fail_1h = 576 (> 3.5)
8. orig_bytes_per_pkt = 0 (<= 0.9545)

## 7. Reason codes used by the response policy

The reason codes (`DOS_HIGH_RATE_PACKET_FLOOD`, `SCAN_RAPID_PROBE_SWEEP`, `CNC_PERSISTENT_BEACON`, `MALWARE_STAGING_TRANSFER`) are names the team gave to each class for the audit log. They are **not** rules taken from the model.

## 8. Results per original IoT-23 label — out-of-fold training data (proposal 3.2)

Labels with at least 30 flows. 'Right group' = the model's top class is the group the label belongs to (Table 5 mapping).

| Original label | Group | Flows | Put in the right group | Called an attack |
| --- | --- | ---: | ---: | ---: |
| Benign (no detailed label) | Benign | 144,338 | 96.33% | 3.67% |
| C&C | CnC | 15,289 | 89.14% | 90.31% |
| C&C-FileDownload | Malware_Download | 39 | 82.05% | 87.18% |
| C&C-HeartBeat | CnC | 33,673 | 99.74% | 99.78% |
| C&C-Torii | CnC | 30 | 83.33% | 90.00% |
| DDoS | DDoS_DoS | 239,585 | 62.24% | 83.12% |
| Okiru | Malware_Download | 250,000 | 73.69% | 99.97% |
| PartOfAHorizontalPortScan | PortScan | 499,989 | 57.07% | 89.89% |

## 8. Results per original IoT-23 label — held-out scenario 34-1 (proposal 3.2)

Labels with at least 30 flows. 'Right group' = the model's top class is the group the label belongs to (Table 5 mapping).

| Original label | Group | Flows | Put in the right group | Called an attack |
| --- | --- | ---: | ---: | ---: |
| Benign (no detailed label) | Benign | 1,923 | 94.38% | 5.62% |
| C&C | CnC | 6,706 | 80.61% | 81.00% |
| DDoS | DDoS_DoS | 14,394 | 98.94% | 99.86% |
| PartOfAHorizontalPortScan | PortScan | 122 | 92.62% | 99.18% |

