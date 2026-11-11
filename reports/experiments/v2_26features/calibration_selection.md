# Step 17a: Choice of the Calibration Method (D-044)

**Generated:** 2026-11-10 18:15:03  
**Data:** grouped out-of-fold probabilities from Step 14 (1,184,004 flows, 22 scenarios, 5 folds). **The held-out scenario 34-1 is not used.**  
**Scoring:** cross-fitted — each fold is calibrated by a fit on the other folds.

## 1. Rule (written in D-044 before this comparison)

1. Keep only methods where every one of the 5 classes has recall ≥ 0.05.
2. Among those, choose the highest macro-F1.
3. If none passes step 1, choose the highest lowest-class recall (ties: higher macro-F1).

## 2. Results

| Method | Macro-F1 | Lowest class recall | Recall Benign | Recall DDoS_DoS | Recall PortScan | Recall CnC | Recall Malware_Download | Mean Brier | Classes reaching the block rule |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `none` **(used)** | 0.7009 | 0.5316 | 0.9561 | 0.6514 | 0.5316 | 0.9071 | 0.7367 | 0.0964 | DDoS_DoS, CnC, Malware_Download |
| `sigmoid_per_class` (D-044 rule) | 0.7160 | 0.6036 | 0.7924 | 0.7892 | 0.6345 | 0.8107 | 0.6036 | 0.1026 | DDoS_DoS, CnC, Malware_Download |
| `temperature` | 0.7009 | 0.5316 | 0.9561 | 0.6514 | 0.5316 | 0.9071 | 0.7367 | 0.1018 | DDoS_DoS, CnC, Malware_Download |
| `multinomial` | 0.6151 | 0.5332 | 0.5538 | 0.6674 | 0.5332 | 0.7358 | 0.5874 | 0.1329 | CnC |
| `multinomial_balanced` | 0.5861 | 0.3778 | 0.5835 | 0.7182 | 0.3778 | 0.9615 | 0.6042 | 0.1386 | CnC |

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

