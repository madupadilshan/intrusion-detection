# Step 17a: Choice of the Calibration Method (D-044)

**Generated:** 2026-11-09 10:05:47  
**Data:** grouped out-of-fold probabilities from Step 14 (1,384,070 flows, 22 scenarios, 5 folds). **The held-out scenario 34-1 is not used.**  
**Scoring:** cross-fitted — each fold is calibrated by a fit on the other folds.

## 1. Rule (written in D-044 before this comparison)

1. Keep only methods where every one of the 5 classes has recall ≥ 0.05.
2. Among those, choose the highest macro-F1.
3. If none passes step 1, choose the highest lowest-class recall (ties: higher macro-F1).

## 2. Results

| Method | Macro-F1 | Lowest class recall | Recall Benign | Recall DDoS_DoS | Recall PortScan | Recall CnC | Recall Malware_Download | Mean Brier | Classes reaching the block rule |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `none` | 0.3422 | 0.0016 | 0.5426 | 0.0016 | 0.3831 | 0.4747 | 0.7365 | 0.1759 | none |
| `sigmoid_per_class` | 0.3633 | 0.0004 | 0.3632 | 0.2429 | 0.5323 | 0.0004 | 0.7365 | 0.1418 | none |
| `temperature` **(used)** | 0.3422 | 0.0016 | 0.5426 | 0.0016 | 0.3831 | 0.4747 | 0.7365 | 0.1454 | none |
| `multinomial` (D-044 rule) | 0.3750 | 0.1417 | 0.4981 | 0.3709 | 0.5705 | 0.1417 | 0.2634 | 0.1765 | PortScan |
| `multinomial_balanced` | 0.3359 | 0.2634 | 0.4946 | 0.3621 | 0.2696 | 0.4074 | 0.2634 | 0.1932 | none |

Method descriptions:

- `none`: raw Random Forest probabilities (no calibration)
- `sigmoid_per_class`: per-class sigmoid (Platt), rows re-normalised
- `temperature`: one temperature on the log-probabilities (softmax); keeps the raw top class
- `multinomial`: multinomial logistic regression on the 5 log-probabilities
- `multinomial_balanced`: multinomial logistic regression on the 5 log-probabilities, class_weight='balanced'

## 3. Choice

**D-044 rule result: `multinomial`** — every class has recall >= 0.05 for: multinomial, multinomial_balanced; 'multinomial' has the highest macro-F1 among them.

This method then **failed** the single final check on the held-out scenario 34-1 (decision D-045): it learns how the model confuses classes on unseen out-of-fold scenarios, and these confusions do not carry over to the final model trained on all 22 scenarios. For example, it turned most 34-1 DDoS flows into Benign.

**Method used now: `temperature`** — D-045: only methods that keep the Random Forest's top class are allowed (none, temperature); 'temperature' has the lower mean Brier score.

Because this choice was made after a 34-1 result, 34-1 is no longer a clean unseen test (D-045). The clean test of the model is the local lab data (Steps 20 and 35).

The block rule is the one from D-040 (precision ≥ 0.95 and at most 1% of benign flows reach the threshold, measured on the out-of-fold data). It is shown here for information; it was not part of the selection rule.

## 4. Limits

- Out-of-fold scores are pessimistic for classes that appear in few scenarios: a fold that holds a scenario trains without it. For example, each DDoS scenario is a different flood type.
- The class mix of the out-of-fold data comes from the Step 12 sampling (at most 50,000 flows per class and scenario), not from a real network. Precision depends on this mix.
- The team had seen results for `none` and `sigmoid_per_class` before writing the rule (D-044).

