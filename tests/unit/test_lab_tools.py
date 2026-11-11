"""tests/unit/test_lab_tools.py - Lab tools (tools/lab_common.py, lab_hardware/hwlab.py) and the
dashboard push rules of the decision engine (one new_event per event)."""

import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lab_hardware"))

import hwlab  # noqa: E402
from core_engine.decision_engine import DecisionEngine  # noqa: E402
from tools.lab_common import ip_in_sets, nft_sets, scenario_report  # noqa: E402

NFT_JSON = json.dumps({"nftables": [
    {"metainfo": {"version": "1.0"}},
    {"set": {"family": "inet", "name": "allow", "table": "ids", "elem": ["192.168.50.1"]}},
    {"set": {"family": "inet", "name": "block_dst", "table": "ids",
             "elem": [{"elem": {"val": "10.10.10.50", "timeout": 1800, "expires": 1790}}]}},
    {"set": {"family": "inet", "name": "limit_src", "table": "ids"}},
]})


def test_nft_sets_reads_router_json():
    sets = nft_sets(NFT_JSON)
    assert sets["block_dst"] == ["10.10.10.50 (ends in 1790s)"]
    assert sets["limit_src"] == [] and "allow" not in sets
    assert ip_in_sets("10.10.10.50", sets) == ["block_dst"]
    assert ip_in_sets("10.10.10.5", sets) == []          # no partial matches
    assert "error" in nft_sets("Error: No such file or directory")


def test_report_flags_a_blocked_protected_device(tmp_path):
    p = tmp_path / "r.md"
    text = scenario_report(path=p, title="t", where="w", start=datetime(2026, 11, 11, 9), end=datetime(2026, 11, 11, 9, 5),
                           how="h", expect="e", safe="s", model="v3.1.0", flows=10,
                           events=[{"predicted_class": "CnC", "src_ip": "192.168.50.31", "dst_ip": "10.10.10.50",
                                    "reason_code": "CNC_PERSISTENT_BEACON", "flow_count": 4, "confidence": 0.9}],
                           blocks=[{"ip": "192.168.50.30", "direction": "source"}],
                           fw_sets={"block_dst": ["10.10.10.50"]}, protected={"192.168.50.30": "camera"},
                           checks=[("q", "a")], notes=[])
    assert "YES - WRONG: camera 192.168.50.30" in text and p.exists()


def test_router_rules_use_the_settings_allowlist():
    text = hwlab.nft_with_allowlist()
    allow = hwlab.cfg()["allowlist"]
    assert f"elements = {{ {', '.join(allow)} }}" in text
    assert text.count("elements = {") == 1 and "table inet ids" in text


def test_every_hardware_scenario_has_a_safe_result():
    sc = hwlab.scenarios()
    assert sorted(sc) == [1, 2, 3, 4, 5, 6]
    assert all(s["safe"] and s["expect"] for s in sc.values())
    assert "192.168.50.31" in sc[4]["how"]          # an infected-camera stand-in, never the real camera (D-054)


class _Sio:
    def __init__(self):
        self.sent = []

    def emit(self, name, data):
        self.sent.append((name, data))


def test_one_new_event_per_event_then_throttled_updates():
    eng = DecisionEngine.__new__(DecisionEngine)        # only the push logic is tested
    from collections import OrderedDict
    eng._pushed_events = OrderedDict()
    eng.socketio = _Sio()
    for i in range(50):                                 # 50 flows of one flood in 0.5 s
        eng._push_event({"timestamp": "t", "confidence": 0.9}, "ev-1", 1000.0 + i * 0.01)
    eng._push_event({"timestamp": "t2", "confidence": 0.9}, "ev-1", 1002.0)
    names = [n for n, _ in eng.socketio.sent]
    assert names.count("new_event") == 1
    assert names.count("event_update") == 1           # at most one per second
    assert eng.socketio.sent[-1][1]["flow_count"] == 51
    eng._push_event({"timestamp": "t"}, "ev-2", 1003.0)
    assert [n for n, _ in eng.socketio.sent].count("new_event") == 2


def test_measure_latency_percentiles_and_zeek_loss(tmp_path):
    from tools.measure_latency import pct, zeek_loss
    vals = [float(v) for v in range(1, 101)]
    assert pct(vals, 0.5) in (50.0, 51.0) and pct(vals, 0.95) in (95.0, 96.0) and pct([], 0.5) is None
    (tmp_path / "capture_loss.log").write_text(
        json.dumps({"ts": 100.0, "percent_lost": 0.5}) + "\n" + json.dumps({"ts": 200.0, "percent_lost": 2.0}) + "\n")
    (tmp_path / "stats.log").write_text(json.dumps({"ts": 150.0, "pkts_dropped": 3}) + "\n"
                                        + json.dumps({"ts": 50.0, "pkts_dropped": 99}) + "\n")
    r = zeek_loss(tmp_path, since=90.0)
    assert r["capture_loss_max_percent"] == 2.0 and r["pkts_dropped"] == 3
