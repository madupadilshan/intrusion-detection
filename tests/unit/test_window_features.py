"""Tests for the window features (decision D-051): correct values, and the same values in
training (chunked, ml_engine) and live (line by line, ZeekAdapter)."""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from core_engine.zeek_adapter import ZeekAdapter  # noqa: E402
from ml_engine.features import BASE_FEATURE_COLUMNS, FEATURE_COLUMNS, make_features  # noqa: E402
from ml_engine.sample_dataset import label_trusted  # noqa: E402
from ml_engine.training_rows import apply_variant  # noqa: E402
from ml_engine.window_features import (  # noqa: E402
    DEFAULT_VALUES,
    PAIR_GAP_MAX,
    WINDOW_FEATURES,
    WindowState,
    compute_window_features,
)


def flow(src, dst, port, ts, **extra):
    rec = {"ts": ts, "id.orig_h": src, "id.orig_p": 40000, "id.resp_h": dst, "id.resp_p": port,
           "proto": "tcp", "conn_state": "S0", "orig_bytes": 0, "resp_bytes": 0, "orig_pkts": 1,
           "resp_pkts": 0, "orig_ip_bytes": 40, "resp_ip_bytes": 0, "duration": 0.0, "missed_bytes": 0,
           "history": "S", "service": "-"}
    rec.update(extra)
    return rec


def test_feature_lists():
    assert len(WINDOW_FEATURES) == 8
    assert len(FEATURE_COLUMNS) == 27
    assert FEATURE_COLUMNS[:6] == BASE_FEATURE_COLUMNS[:6]
    assert set(BASE_FEATURE_COLUMNS) | set(WINDOW_FEATURES) == set(FEATURE_COLUMNS)
    # IP addresses and times are never model inputs (proposal Table 6)
    assert not {"id.orig_h", "id.resp_h", "ts", "uid"} & set(FEATURE_COLUMNS)


def test_scan_pattern_many_destinations():
    st = WindowState()
    out = [st.update("10.0.0.9", f"192.168.50.{i}", 23, 1000.0 + i * 0.1) for i in range(1, 6)]
    conn, udst, uport, ratio, pair_conn, gap, change, fails = out[-1]
    assert (conn, udst, uport, ratio, pair_conn) == (5, 5, 1, 1.0, 1)
    assert gap == -1.0 and change == -1.0  # first contact with each destination


def test_cnc_pattern_regular_contact():
    st = WindowState()
    out = [st.update("192.168.50.30", "203.0.113.7", 6667, 2000.0 + 10.0 * i) for i in range(4)]
    conn, udst, uport, ratio, pair_conn, gap, change, fails = out[-1]
    assert (conn, udst, pair_conn) == (4, 1, 4)
    assert gap == pytest.approx(10.0)
    assert change == pytest.approx(0.0)  # same gap every time = regular heartbeat
    assert ratio == pytest.approx(0.25)


def test_new_period_starts_new_counts_but_pair_gap_continues():
    st = WindowState()
    st.update("a", "b", 80, 59.0)
    conn, udst, _, _, pair_conn, gap, _, _ = st.update("a", "b", 80, 61.0)  # next 60 s period
    assert (conn, udst, pair_conn) == (1, 1, 1)
    assert gap == pytest.approx(2.0)


def test_long_gap_counts_as_no_previous_flow():
    st = WindowState()
    st.update("a", "b", 80, 0.0)
    assert st.update("a", "b", 80, PAIR_GAP_MAX + 5.0)[5] == -1.0


def test_missing_time_or_source_gives_defaults_and_is_not_counted():
    st = WindowState()
    assert st.update("a", "b", 80, None) == DEFAULT_VALUES
    assert st.update(None, "b", 80, 5.0) == DEFAULT_VALUES
    assert st.update("a", "b", 80, 5.0)[0] == 1.0


def test_memory_is_bounded_by_time():
    st = WindowState()
    for i in range(20000):  # one new destination per second for about 5.5 hours
        st.update("scanner", f"d{i}", 23, float(i))
    assert len(st) <= 610  # only pairs from the last 10 minutes are kept
    assert len(st._periods) <= 4


def test_memory_is_bounded_under_a_heavy_scan(monkeypatch):
    import ml_engine.window_features as wf
    monkeypatch.setattr(wf, "MAX_DSTS_PER_PERIOD", 100)
    monkeypatch.setattr(wf, "MAX_PAIRS", 500)
    monkeypatch.setattr(wf, "MAX_PAIR_LOG", 1000)
    st = WindowState()
    for i in range(5000):  # 5,000 new destinations in 5 seconds
        out = st.update("scanner", f"d{i}", 23, 100.0 + i / 1000)
    assert len(st) <= 500 and len(st._pair_log) <= 1000
    conn, udst, uport, ratio, pair_conn, gap, change, fails = out
    assert conn == 5000 and udst == 5000 and ratio == 1.0  # still counted after the limit
    assert len(st._periods[("scanner", 1)][1]) == 100      # but only 100 remembered


def test_chunked_equals_one_pass():
    rng = np.random.default_rng(1)
    n = 3000
    df = pd.DataFrame({
        "id.orig_h": rng.choice(["s1", "s2", "s3"], n),
        "id.resp_h": rng.choice([f"d{i}" for i in range(40)], n),
        "id.resp_p": rng.choice([23, 80, 443, 6667], n),
        "ts": np.cumsum(rng.exponential(0.5, n)) + rng.normal(0, 0.3, n),  # not sorted, like Zeek
        "proto": rng.choice(["tcp", "tcp", "udp"], n),
        "conn_state": rng.choice(["S0", "REJ", "SF", "S3"], n),
    })
    whole = compute_window_features(df)
    st = WindowState()
    parts = [compute_window_features(df.iloc[i:i + 700], st) for i in range(0, n, 700)]
    pd.testing.assert_frame_equal(whole, pd.concat(parts))


def test_training_and_live_give_the_same_values(tmp_path):
    """Training (make_features on a whole file) == live (ZeekAdapter line by line)."""
    rng = np.random.default_rng(7)
    flows = []
    t = 1_700_000_000.0
    for i in range(400):
        t += float(rng.exponential(0.4))
        src = rng.choice(["192.168.50.30", "10.10.10.50", "192.168.50.31"])
        dst = rng.choice(["192.168.50.30", "203.0.113.7", "198.51.100.2", f"192.168.50.{rng.integers(1, 60)}"])
        flows.append(flow(str(src), str(dst), int(rng.choice([23, 80, 554, 6667])), t + float(rng.normal(0, 0.2))))
    log = tmp_path / "conn.log"
    log.write_text("\n".join(json.dumps(f) for f in flows) + "\n", encoding="utf-8")

    adapter = ZeekAdapter(conn_log_path=log, enable_state_persistence=False, local_networks=["192.168.50.0/24"])
    live = make_features(adapter.read_file(log))
    offline = make_features(pd.DataFrame(flows))
    assert list(live.columns) == FEATURE_COLUMNS
    pd.testing.assert_frame_equal(live[WINDOW_FEATURES].reset_index(drop=True),
                                  offline[WINDOW_FEATURES].reset_index(drop=True))


def test_make_features_uses_given_window_columns():
    rec = flow("a", "b", 80, 10.0)
    rec.update({c: 9.0 for c in WINDOW_FEATURES})
    feats = make_features([rec])
    assert feats[WINDOW_FEATURES].iloc[0].tolist() == [9.0] * 8
    assert feats.isna().sum().sum() == 0


def test_adapter_reset_clears_window_memory(tmp_path):
    adapter = ZeekAdapter(conn_log_path=tmp_path / "x.log", enable_state_persistence=False)
    line = json.dumps(flow("a", "b", 80, 10.0))
    adapter.parse_and_enrich(line)
    assert adapter.parse_and_enrich(line)["src_conn_60s"] == 2.0
    adapter.reset_state()
    assert adapter.parse_and_enrich(line)["src_conn_60s"] == 1.0


def test_label_trusted_rule():
    df = pd.DataFrame([
        # Benign, S0, 0 bytes, private -> public: looks like scanning -> not trusted
        {"class_name": "Benign", "conn_state": "S0", "orig_bytes": 0, "id.orig_h": "192.168.1.5", "id.resp_h": "8.8.4.4"},
        # same but answered (SF) -> trusted
        {"class_name": "Benign", "conn_state": "SF", "orig_bytes": 0, "id.orig_h": "192.168.1.5", "id.resp_h": "8.8.4.4"},
        # inbound from the internet -> trusted
        {"class_name": "Benign", "conn_state": "S0", "orig_bytes": 0, "id.orig_h": "8.8.4.4", "id.resp_h": "192.168.1.5"},
        # attack label -> trusted (labels of attacks are not changed)
        {"class_name": "PortScan", "conn_state": "S0", "orig_bytes": 0, "id.orig_h": "192.168.1.5", "id.resp_h": "8.8.4.4"},
        # missing bytes count as 0 -> not trusted
        {"class_name": "Benign", "conn_state": "S0", "orig_bytes": None, "id.orig_h": "192.168.1.5", "id.resp_h": "1.1.1.1"},
    ])
    assert label_trusted(df, "CTU-IoT-Malware-Capture-35-1").tolist() == [False, True, True, True, False]
    # Honeypot captures have real benign devices: every label is trusted
    assert label_trusted(df, "CTU-Honeypot-Capture-4-1").all()


def test_apply_variant_keeps_order():
    df = pd.DataFrame({"x": [1, 2, 3, 4], "label_trusted": [True, False, True, True]})
    assert apply_variant(df, "W")["x"].tolist() == [1, 2, 3, 4]
    assert apply_variant(df, "WC")["x"].tolist() == [1, 3, 4]
    with pytest.raises(ValueError):
        apply_variant(df, "X")


# ---- D-052: failed tries of the same pair in the last hour ----

def test_pair_fail_counts_failed_tries_before_a_conversation():
    st = WindowState()
    outs = [st.update("192.168.50.30", "203.0.113.9", 6667, 100.0 + 30 * i, "tcp", "S0") for i in range(5)]
    assert [o[7] for o in outs] == [0.0, 1.0, 2.0, 3.0, 4.0]   # this flow is not counted
    conv = st.update("192.168.50.30", "203.0.113.9", 6667, 400.0, "tcp", "S3")
    assert conv[7] == 5.0                                        # the conversation sees the 5 failed tries
    assert st.update("192.168.50.30", "203.0.113.9", 6667, 410.0, "tcp", "SF")[7] == 5.0  # S3/SF not counted
    assert st.update("192.168.50.30", "198.51.100.1", 6667, 420.0, "tcp", "SF")[7] == 0.0  # other pair


def test_pair_fail_only_tcp_failed_states():
    st = WindowState()
    st.update("a", "b", 53, 10.0, "udp", "S0")        # UDP: not a failed TCP try
    st.update("a", "b", 53, 11.0, "tcp", "SF")        # completed
    st.update("a", "b", 53, 12.0, None, None)         # unknown
    assert st.update("a", "b", 53, 13.0, "tcp", "SF")[7] == 0.0
    for state in ("S0", "REJ", "RSTOS0", "SH", "RSTRH", "SHR", "OTH"):
        st.update("a", "c", 80, 20.0, "tcp", state)
    assert st.update("a", "c", 80, 21.0, "tcp", "SF")[7] == 7.0


def test_pair_fail_forgets_after_about_an_hour():
    st = WindowState()
    for i in range(10):
        st.update("a", "b", 80, 0.0 + i, "tcp", "S0")
    assert st.update("a", "b", 80, 3000.0, "tcp", "SF")[7] == 10.0    # 50 minutes later: still counted
    assert st.update("a", "b", 80, 3700.0, "tcp", "SF")[7] == 0.0     # more than 60 minutes: forgotten


def test_pair_fail_memory_is_bounded(monkeypatch):
    import ml_engine.window_features as wf
    monkeypatch.setattr(wf, "MAX_FAIL_PAIRS", 300)
    monkeypatch.setattr(wf, "MAX_FAIL_LOG", 600)
    st = WindowState()
    for i in range(5000):
        st.update("scanner", f"d{i}", 23, 100.0 + i / 1000, "tcp", "S0")
        st.update("cam", "c2", 4975, 100.0 + i / 1000, "tcp", "S0")   # refreshed all the time: kept
    assert len(st._fails) <= 300 and len(st._fail_log) <= 600
    assert st.update("cam", "c2", 4975, 106.0, "tcp", "S3")[7] == 5000.0
