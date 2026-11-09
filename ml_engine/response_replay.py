"""ml_engine/response_replay.py - Replay the live response rule on labelled flows (decision D-046).

Proposal 3.4: "One high prediction will not cause an automatic block by itself. The event must
pass a confidence threshold, and it must happen again inside a set time window. Events with lower
confidence will only send an alert."

This module replays exactly that rule (the same one `core_engine/response_policy.py` and
`core_engine/decision_engine.py` use live) on flows whose true class is known:

    1. A flow is a block candidate for class k when the model's top class is k and its
       (calibrated) confidence is at least the block threshold t.
    2. A block fires when the same target has at least `min_repeats` block candidates of class k
       inside `repeat_window_seconds`, and the target is not already blocked.
    3. A block lasts `max_rule_minutes`; during that time the target is not blocked again.

Target per class (proposal Table 5, response_policy.py): the source IP for DDoS_DoS and PortScan;
the destination (outside host) for CnC and Malware_Download.

It also builds the per-original-label table that proposal 3.2 asks for.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

CLASS_NAMES = ["Benign", "DDoS_DoS", "PortScan", "CnC", "Malware_Download"]
TARGET_FIELD = {1: "src", 2: "src", 3: "dst", 4: "dst"}

# D-046 rule for a block threshold
BLOCK_MIN_SAFE_SHARE = 0.95       # at least 95% of the blocks are fired by a truly malicious flow
BLOCK_MAX_BENIGN_TARGETS = 0.01   # at most 1% of the benign targets are ever blocked
BLOCK_MIN_EVENTS = 10             # at least 10 blocks, so there is evidence
MIN_LABEL_FLOWS = 30              # proposal 3.2: "when there are enough samples"


def _targets(k: int, src: np.ndarray, dst: np.ndarray) -> np.ndarray:
    return src if TARGET_FIELD[k] == "src" else dst


def replay_blocks(
    pred: np.ndarray,
    conf: np.ndarray,
    y: np.ndarray,
    scenario: np.ndarray,
    ts: np.ndarray,
    src: np.ndarray,
    dst: np.ndarray,
    k: int,
    threshold: float,
    min_repeats: int = 3,
    window_s: float = 60.0,
    rule_minutes: float = 30.0,
) -> Dict[str, Any]:
    """Replay the response rule for class k at one threshold. Returns block counts."""
    target = _targets(k, src, dst)
    benign_keys = pd.unique(pd.Series(scenario[y == 0]).astype(str) + "|" + pd.Series(target[y == 0]).astype(str))
    n_benign_targets = int(len(benign_keys))

    mask = (pred == k) & (conf >= threshold) & np.isfinite(ts)
    idx = np.nonzero(mask)[0]
    empty = {"threshold": round(float(threshold), 2), "blocks": 0, "wrong_blocks": 0, "right_class_blocks": 0,
             "safe_share": None, "benign_targets_blocked": 0, "benign_targets": n_benign_targets,
             "benign_target_rate": 0.0, "scenarios_with_blocks": 0}
    if len(idx) == 0:
        return empty

    keys = pd.Series(scenario[idx]).astype(str).values + "|" + pd.Series(target[idx]).astype(str).values
    key_codes, _ = pd.factorize(keys)
    t = ts[idx].astype(np.float64)
    order = np.lexsort((t, key_codes))
    kc, tt, yy, keys_sorted = key_codes[order], t[order], y[idx][order], keys[order]

    # Count block candidates of the same target inside the window (inclusive), per target.
    t0 = tt.min()
    span = (tt.max() - t0) + 2 * window_s + 1.0
    comp = kc.astype(np.float64) * span + (tt - t0)
    first_in_window = np.searchsorted(comp, comp - window_s, side="left")
    counts = np.arange(len(comp)) - first_in_window + 1
    eligible = np.nonzero(counts >= min_repeats)[0]

    fires: List[int] = []
    last_key, blocked_until = -1, -np.inf
    rule_s = rule_minutes * 60.0
    for i in eligible:
        if kc[i] != last_key:
            last_key, blocked_until = kc[i], -np.inf
        if tt[i] >= blocked_until:
            fires.append(i)
            blocked_until = tt[i] + rule_s

    if not fires:
        return empty
    fires_arr = np.asarray(fires)
    wrong = yy[fires_arr] == 0
    wrong_targets = set(keys_sorted[fires_arr][wrong].tolist())
    n_blocks = int(len(fires_arr))
    return {
        "threshold": round(float(threshold), 2),
        "blocks": n_blocks,
        "wrong_blocks": int(wrong.sum()),
        "right_class_blocks": int((yy[fires_arr] == k).sum()),
        "safe_share": round(float(1.0 - wrong.mean()), 4),
        "benign_targets_blocked": len(wrong_targets),
        "benign_targets": n_benign_targets,
        "benign_target_rate": round(len(wrong_targets) / n_benign_targets, 5) if n_benign_targets else 0.0,
        "scenarios_with_blocks": int(len({s.split("|", 1)[0] for s in keys_sorted[fires_arr]})),
    }


def meets_block_rule(r: Dict[str, Any]) -> bool:
    return (
        r["blocks"] >= BLOCK_MIN_EVENTS
        and r["safe_share"] is not None
        and r["safe_share"] >= BLOCK_MIN_SAFE_SHARE
        and r["benign_target_rate"] <= BLOCK_MAX_BENIGN_TARGETS
    )


def choose_block_threshold(
    cal: np.ndarray,
    y: np.ndarray,
    scenario: np.ndarray,
    ts: np.ndarray,
    src: np.ndarray,
    dst: np.ndarray,
    k: int,
    start: float,
    min_repeats: int = 3,
    window_s: float = 60.0,
    rule_minutes: float = 30.0,
) -> Dict[str, Any]:
    """Lowest threshold (start..0.99) that meets the D-046 rule; also returns every replay row."""
    pred = cal.argmax(axis=1)
    conf = cal.max(axis=1)
    grid = [round(x, 2) for x in np.arange(max(0.30, start), 0.991, 0.01)]
    rows = []
    chosen: Optional[Dict[str, Any]] = None
    for t in grid:
        r = replay_blocks(pred, conf, y, scenario, ts, src, dst, k, t, min_repeats, window_s, rule_minutes)
        rows.append(r)
        if chosen is None and meets_block_rule(r):
            chosen = r
        if r["blocks"] == 0:  # higher thresholds can only give fewer candidates
            break
    return {"chosen": chosen, "rows": rows}


def detailed_label_table(pred: np.ndarray, y: np.ndarray, detailed: np.ndarray,
                         min_flows: int = MIN_LABEL_FLOWS) -> List[Dict[str, Any]]:
    """Per original IoT-23 label: flows, its group, share put in the right group, share called an attack."""
    names = np.where(pd.Series(detailed).astype(str).isin(["-", "", "nan", "None"]), "Benign (no detailed label)",
                     pd.Series(detailed).astype(str))
    out = []
    for name in sorted(set(names.tolist())):
        m = names == name
        n = int(m.sum())
        if n < min_flows:
            continue
        group = int(np.bincount(y[m], minlength=len(CLASS_NAMES)).argmax())
        out.append({
            "label": name,
            "group": CLASS_NAMES[group],
            "flows": n,
            "right_group_share": round(float((pred[m] == y[m]).mean()), 4),
            "called_attack_share": round(float((pred[m] != 0).mean()), 4),
        })
    return out
