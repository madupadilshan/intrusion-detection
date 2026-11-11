# Note (11 Nov 2026, decision D-056)

`model_comparison.md` / `model_comparison.csv` in this folder were written by an older `ml_engine/compare_models.py`.
In that version the **Random Forest** accuracy, weighted F1, per-class recall and benign counts were typed-in numbers
from an old run (for example accuracy 45.00%, DDoS recall 0.12%). They were **not measured** and must not be quoted.
The Random Forest **macro-F1** values and all Logistic Regression and HistGradientBoosting numbers were measured.
The code is fixed; the current report is `reports/experiments/model_comparison.md`.
