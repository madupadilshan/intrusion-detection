#!/usr/bin/env python3
"""
ml_engine/select_variant.py - Choose between two training variants (decisions D-051 and D-052).

The rule was written in docs/decision_log.md BEFORE any result:
  - Both variants are compared on the SAME rows: the rows that both variants keep
    (D-051, W vs WC: the trusted rows; D-052, WC vs WCD: trusted and not disputed).
  - The candidate is deployed only if its out-of-fold macro-F1 on those rows is at least 0.01
    higher than the base; otherwise the base is deployed (fewer data decisions).
Only grouped out-of-fold predictions of the training scenarios are used. The held-out scenario
34-1 is not read here.

The chosen variant's model, out-of-fold predictions and Step 14 reports are copied to the
standard paths used by Steps 15-18, and the choice is written to
reports/experiments/variant_selection.json (read by ml_engine/training_rows.py).

Run (after Step 14 for both variants):
  python ml_engine/select_variant.py --base WC --candidate WCD

A later, written decision may deploy the other variant (D-054: the owner and the supervisor chose
WCD after the out-of-fold results were seen). Then the rule's own result is still computed and
written next to the decision, so the report shows both:
  python ml_engine/select_variant.py --base WC --candidate WCD --decided WCD --decided-by D-054       --decided-reason "..."
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
import time
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from ml_engine.training_rows import (  # noqa: E402
    TRAIN_PARQUET,
    VARIANT_COLUMNS,
    VARIANT_FILE,
    VARIANTS,
    label_disputed,
    variant_mask,
)

CLASS_NAMES = ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]
LABELS = list(range(len(CLASS_NAMES)))
MIN_GAIN = 0.01
PROCESSED = PROJECT_ROOT / "data" / "processed"
MODELS = PROJECT_ROOT / "ml_engine" / "models"
EXPERIMENTS = PROJECT_ROOT / "reports" / "experiments"
STEP14_REPORTS = ["rf_search.csv", "rf_cv_results.csv", "rf_training_report.md"]
DECISION = {("W", "WC"): "D-051", ("WC", "WCD"): "D-052"}


def scores(y: np.ndarray, probs: np.ndarray) -> Dict[str, float]:
    pred = probs.argmax(axis=1)
    per = f1_score(y, pred, labels=LABELS, average=None, zero_division=0)
    out = {"macro_f1": float(per.mean()), "rows": int(len(y))}
    out.update({f"f1_{c}": float(v) for c, v in zip(CLASS_NAMES, per)})
    return out


def to_full(oof_path: Path, mask: np.ndarray, y_full: np.ndarray, name: str) -> Optional[np.ndarray]:
    """Place out-of-fold probabilities of a variant back on the full row index (NaN elsewhere).
    Returns None if the file does not line up with `mask` (other rows or another order)."""
    if not oof_path.exists():
        return None
    z = np.load(oof_path, allow_pickle=False)
    if int(mask.sum()) != len(z["y"]) or not np.array_equal(y_full[mask], z["y"]):
        print(f"  note: {name} ({oof_path}) does not line up with its rows; not compared")
        return None
    full = np.full((len(y_full), len(CLASS_NAMES)), np.nan, dtype=np.float32)
    full[mask] = z["oof_probs"]
    return full


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--base", choices=VARIANTS, default="WC")
    ap.add_argument("--candidate", choices=VARIANTS, default="WCD")
    ap.add_argument("--data-path", type=Path, default=TRAIN_PARQUET)
    ap.add_argument("--compare", action="append", default=[],
                    metavar="NAME=VARIANT=PATH",
                    help="extra out-of-fold file to score on the same rows, for comparison only "
                         "(e.g. 'v2.0.0 (26 features)=WC=data/processed/v2_26features/rf_oof_WC.npz')")
    ap.add_argument("--no-copy", action="store_true", help="only report; do not copy the chosen files")
    ap.add_argument("--decided", choices=VARIANTS, default=None,
                    help="deploy this variant because of a later written decision (needs --decided-by)")
    ap.add_argument("--decided-by", default=None, help="decision-log entry, e.g. D-054")
    ap.add_argument("--decided-reason", default="", help="one sentence: why the decision differs from the rule")
    args = ap.parse_args()
    if args.decided and not args.decided_by:
        raise SystemExit("--decided needs --decided-by (the decision-log entry)")
    base, cand = args.base, args.candidate
    decision = DECISION.get((base, cand), "D-052")

    cols = list(dict.fromkeys(["label_idx"] + VARIANT_COLUMNS["WCD"]))
    df = pd.read_parquet(args.data_path, columns=cols)
    y = df["label_idx"].to_numpy().astype(np.int8)
    m_base, m_cand = variant_mask(df, base), variant_mask(df, cand)
    rows = m_base & m_cand
    disputed = label_disputed(df)

    p_base = to_full(PROCESSED / f"rf_oof_{base}.npz", m_base, y, base)
    p_cand = to_full(PROCESSED / f"rf_oof_{cand}.npz", m_cand, y, cand)
    if p_base is None or p_cand is None:
        raise SystemExit("Out-of-fold files missing or not lined up; re-run Step 14 for both variants.")

    res = {
        f"{base}_compared_rows": scores(y[rows], p_base[rows]),
        f"{cand}_compared_rows": scores(y[rows], p_cand[rows]),
        f"{base}_own_rows": scores(y[m_base], p_base[m_base]),
    }
    labels = {
        f"{base}_compared_rows": f"**{base}, compared rows**",
        f"{cand}_compared_rows": f"**{cand}, compared rows**",
        f"{base}_own_rows": f"{base}, all its own rows",
    }
    for spec in args.compare:
        name, var, path = spec.split("=", 2)
        p = to_full(PROJECT_ROOT / path, variant_mask(df, var), y, name)
        if p is not None and not np.isnan(p[rows]).any():
            res[f"compare: {name}"] = scores(y[rows], p[rows])
            labels[f"compare: {name}"] = f"{name}, compared rows"

    gain = res[f"{cand}_compared_rows"]["macro_f1"] - res[f"{base}_compared_rows"]["macro_f1"]
    rule_choice = cand if gain >= MIN_GAIN else base
    chosen = args.decided or rule_choice
    if args.decided:
        decision = f"{decision}, {args.decided_by}"
    out = {
        "decision": decision,
        "rule_choice": rule_choice,
        "decided_by": args.decided_by,
        "decided_reason": args.decided_reason or None,
        "rule": (f"compare on the rows both variants keep; {cand} only if its macro-F1 is at least "
                 f"{MIN_GAIN} higher, else {base}"),
        "base": base,
        "candidate": cand,
        f"gain_{cand}_minus_{base}": round(gain, 4),
        "chosen": chosen,
        "compared_rows": int(rows.sum()),
        "rows_left_out_by_trusted_rule": int((~df["label_trusted"].astype(bool)).sum()),
        "rows_disputed": int(disputed.sum()),
        "results": res,
        "created": time.strftime("%Y-%m-%d %H:%M:%S"),
    }

    if not args.no_copy:
        EXPERIMENTS.mkdir(parents=True, exist_ok=True)
        shutil.copy2(MODELS / f"rf_model_{chosen}.joblib", MODELS / "rf_model.joblib")
        shutil.copy2(PROCESSED / f"rf_oof_{chosen}.npz", PROCESSED / "rf_oof_predictions.npz")
        for name in STEP14_REPORTS:
            src = EXPERIMENTS / f"variant_{chosen}" / name
            if src.exists():
                shutil.copy2(src, EXPERIMENTS / name)
        VARIANT_FILE.write_text(json.dumps(out, indent=2), encoding="utf-8")

    lines = [
        f"# Training variant choice (Step 14, decision {decision})",
        "",
        f"**Created:** {out['created']}  ",
        "**Data:** grouped out-of-fold predictions of the 22 training scenarios only. "
        "The held-out scenario 34-1 is not used.  ",
        f"**Rule (written before the results):** {out['rule']}.",
        "",
        "| Model | Rows | Macro-F1 | " + " | ".join(CLASS_NAMES) + " |",
        "| --- | ---: | ---: | " + " | ".join("---:" for _ in CLASS_NAMES) + " |",
    ]
    for key, label in labels.items():
        r = res.get(key)
        if r:
            lines.append(f"| {label} | {r['rows']:,} | {r['macro_f1']:.4f} | "
                         + " | ".join(f"{r['f1_' + c]:.3f}" for c in CLASS_NAMES) + " |")
    lines += [
        "",
        f"- Compared rows (kept by both {base} and {cand}): {out['compared_rows']:,}.",
        f"- Rows left out by the trusted-label rule (D-051): {out['rows_left_out_by_trusted_rule']:,}; "
        f"rows listed as disputed (D-052, `config/disputed_labels.yaml`): {out['rows_disputed']:,}.",
        f"- {cand} minus {base} on the compared rows: {gain:+.4f}. Result of the rule: {rule_choice}.",
        (f"- **Deployed: {chosen}, by decision {args.decided_by}** (made after these out-of-fold results were seen; "
         f"see `docs/decision_log.md`). {args.decided_reason}".rstrip()
         if args.decided else f"- **Deployed: {chosen}** (by the rule)."),
        "- Each variant has its own grouped folds (the fold split depends on the rows), "
        "so part of a difference can come from the fold split.",
        "- These are training-data (out-of-fold) results. The held-out result is in `evaluation_iot23.md`.",
    ]
    if not args.no_copy:
        (EXPERIMENTS / "variant_selection.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
