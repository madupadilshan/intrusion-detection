# Step 17a: Choice of the Calibration Method (D-044)

**Generated:** 2026-11-11 09:29:45  
**Data:** grouped out-of-fold probabilities from Step 14 (1,182,984 flows, 22 scenarios, 5 folds). **The held-out scenario 34-1 is not used.**  
**Scoring:** cross-fitted — each fold is calibrated by a fit on the other folds.

## 1. Rule (written in D-044 before this comparison)

1. Keep only methods where every one of the 5 classes has recall ≥ 0.05.
2. Among those, choose the highest macro-F1.
3. If none passes step 1, choose the highest lowest-class recall (ties: higher macro-F1).

## 2. Results

| Method | Macro-F1 | Lowest class recall | Recall Benign | Recall DDoS_DoS | Recall PortScan | Recall CnC | Recall Malware_Download | Mean Brier | Classes reaching the block rule |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `none` **(used)** | 0.7097 | 0.5707 | 0.9633 | 0.6224 | 0.5707 | 0.9642 | 0.7370 | 0.0925 | DDoS_DoS, PortScan, CnC, Malware_Download |
| `sigmoid_per_class` (D-044 rule) | 0.7505 | 0.5971 | 0.8312 | 0.7900 | 0.6477 | 0.8967 | 0.5971 | 0.0998 | DDoS_DoS, CnC, Malware_Download |
| `temperature` | 0.7097 | 0.5707 | 0.9633 | 0.6224 | 0.5707 | 0.9642 | 0.7370 | 0.0998 | DDoS_DoS, PortScan, CnC, Malware_Download |
| `multinomial` | 0.6372 | 0.5388 | 0.6183 | 0.7046 | 0.5388 | 0.7395 | 0.6120 | 0.1367 | DDoS_DoS |
| `multinomial_balanced` | 0.6307 | 0.4375 | 0.6144 | 0.6954 | 0.4375 | 0.9480 | 0.6521 | 0.1439 | DDoS_DoS |

Method descriptions:

- `none`: raw Random Forest probabilities (no calibration)
- `sigmoid_per_class`: per-class sigmoid (Platt), rows re-normalised
- `temperature`: one temperature on the log-probabilities (softmax); keeps the raw top class
- `multinomial`: multinomial logistic regression on the 5 log-probabilities
- `multinomial_balanced`: multinomial logistic regression on the 5 log-probabilities, class_weight='balanced'

## 3. Choice

**D-044 rule result: `sigmoid_per_class`** — every class has recall >= 0.05 for: none, sigmoid_per_class, temperature, multinomial, multinomial_balanced; 'sigmoid_per_class' has the highest macro-F1 among them.

This method then **failed** the single final check on the held-out scenario 34-1 (decision D-045): it learns how the model confuses classes on unseen out-of-fold scenarios, and these confusions do not carry over to the final model trained on all 22 scenarios. For example, it turned most 34-1 DDoS flows into Benign.

**Method used now: `none`** — D-045: only methods that keep the Random Forest's top class are allowed (none, temperature); 'none' has the lower mean Brier score.

Because this choice was made after a 34-1 result, 34-1 is no longer a clean unseen test (D-045). The clean test of the model is the local lab data (Steps 20 and 35).

The block rule is the one from D-040 (precision ≥ 0.95 and at most 1% of benign flows reach the threshold, measured on the out-of-fold data). It is shown here for information; it was not part of the selection rule.

## 4. Limits

- Out-of-fold scores are pessimistic for classes that appear in few scenarios: a fold that holds a scenario trains without it. For example, each DDoS scenario is a different flood type.
- The class mix of the out-of-fold data comes from the Step 12 sampling (at most 50,000 flows per class and scenario), not from a real network. Precision depends on this mix.
- The team had seen results for `none` and `sigmoid_per_class` before writing the rule (D-044).

