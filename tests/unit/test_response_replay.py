"""tests/unit/test_response_replay.py - Tests for the D-046 repeat-rule replay (proposal 3.4)."""

import numpy as np

from ml_engine.response_replay import (
    choose_block_threshold,
    detailed_label_table,
    meets_block_rule,
    replay_blocks,
)


def _flows(times, y, src, dst, k=2, conf=0.9, scenario="S1"):
    n = len(times)
    pred = np.full(n, k)
    return (pred, np.full(n, conf), np.asarray(y), np.full(n, scenario, dtype=object),
            np.asarray(times, dtype=float), np.asarray(src, dtype=object), np.asarray(dst, dtype=object))


def test_block_needs_repeats_inside_the_window():
    # Two candidates in 60 s: no block. Third one inside the window: block.
    pred, conf, y, sc, ts, src, dst = _flows([0, 30, 50], [2, 2, 2], ["a"] * 3, ["x"] * 3)
    r = replay_blocks(pred, conf, y, sc, ts, src, dst, k=2, threshold=0.5, min_repeats=3, window_s=60)
    assert r["blocks"] == 1 and r["wrong_blocks"] == 0
    r2 = replay_blocks(pred[:2], conf[:2], y[:2], sc[:2], ts[:2], src[:2], dst[:2], k=2, threshold=0.5)
    assert r2["blocks"] == 0


def test_repeats_outside_the_window_do_not_count():
    pred, conf, y, sc, ts, src, dst = _flows([0, 100, 200], [2, 2, 2], ["a"] * 3, ["x"] * 3)
    assert replay_blocks(pred, conf, y, sc, ts, src, dst, k=2, threshold=0.5, window_s=60)["blocks"] == 0


def test_a_blocked_target_is_not_blocked_again_until_the_rule_expires():
    times = [0, 1, 2, 3, 4, 5, 1900, 1901, 1902]
    pred, conf, y, sc, ts, src, dst = _flows(times, [2] * 9, ["a"] * 9, ["x"] * 9)
    r = replay_blocks(pred, conf, y, sc, ts, src, dst, k=2, threshold=0.5, rule_minutes=30)
    assert r["blocks"] == 2  # once at t=2, again after 30 minutes


def test_targets_follow_table_5():
    # PortScan blocks the source; CnC blocks the destination.
    pred, conf, y, sc, ts, src, dst = _flows([0, 1, 2], [3, 3, 3], ["a", "b", "c"], ["x"] * 3, k=3)
    assert replay_blocks(pred, conf, y, sc, ts, src, dst, k=3, threshold=0.5)["blocks"] == 1
    pred, conf, y, sc, ts, src, dst = _flows([0, 1, 2], [2, 2, 2], ["a", "b", "c"], ["x"] * 3, k=2)
    assert replay_blocks(pred, conf, y, sc, ts, src, dst, k=2, threshold=0.5)["blocks"] == 0


def test_wrong_blocks_and_benign_targets_are_counted():
    pred, conf, y, sc, ts, src, dst = _flows([0, 1, 2], [0, 0, 0], ["b"] * 3, ["x"] * 3)
    r = replay_blocks(pred, conf, y, sc, ts, src, dst, k=2, threshold=0.5)
    assert r["wrong_blocks"] == 1 and r["benign_targets_blocked"] == 1 and r["safe_share"] == 0.0
    assert not meets_block_rule(r)


def test_choose_block_threshold_finds_the_lowest_safe_value():
    rng = np.random.RandomState(0)
    rows = []
    # 20 scanners, each with 5 flows in 10 s, confidence 0.8 -> safe blocks
    for s in range(20):
        for j in range(5):
            rows.append((s * 100 + j, 2, f"scan{s}", "x", 0.8))
    # benign hosts flagged as PortScan with low confidence 0.4
    for b in range(20):
        for j in range(5):
            rows.append((5000 + b * 100 + j, 0, f"ben{b}", "x", 0.4))
    ts = np.array([r[0] for r in rows], float)
    y = np.array([r[1] for r in rows])
    src = np.array([r[2] for r in rows], dtype=object)
    dst = np.array([r[3] for r in rows], dtype=object)
    conf = np.array([r[4] for r in rows])
    cal = np.zeros((len(rows), 5))
    cal[:, 2] = conf
    cal[:, 0] = (1 - conf) / 2
    cal[:, 1] = (1 - conf) / 2
    sc = np.full(len(rows), "S1", dtype=object)
    res = choose_block_threshold(cal, y, sc, ts, src, dst, k=2, start=0.30)
    assert res["chosen"] is not None
    assert 0.40 < res["chosen"]["threshold"] <= 0.80
    assert res["chosen"]["wrong_blocks"] == 0
    rng.rand()


def test_detailed_label_table_uses_min_flows_and_groups():
    pred = np.array([2] * 40 + [0] * 10)
    y = np.array([2] * 50)
    det = np.array(["PartOfAHorizontalPortScan"] * 50 + [])
    rows = detailed_label_table(pred, y, det, min_flows=30)
    assert rows[0]["label"] == "PartOfAHorizontalPortScan"
    assert rows[0]["group"] == "PortScan"
    assert rows[0]["right_group_share"] == 0.8
    assert detailed_label_table(pred[:20], y[:20], det[:20], min_flows=30) == []
