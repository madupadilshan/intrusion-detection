"""tests/unit/test_rate_limit.py - Automatic rate-limit for DDoS from outside (decision D-055).

Proposal Table 5 (DDoS row): "Alert. Rate-limit or block the outside source if the policy allows it."
Proposal Table 10 row 3: "The source is blocked or rate-limited. The camera service comes back."
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from core_engine.decision_engine import DecisionEngine, DecisionOutcome
from core_engine.firewall import SimulationAdapter
from core_engine.response_policy import (
    REASON_AUTO_DDOS_RATELIMIT,
    REASON_SKIP_PRIVATE_TARGET,
    ResponsePolicy,
)
from core_engine.rule_worker import _rule_dir, reconcile_on_startup

# Thresholds as Step 17 writes them when DDoS_DoS has no block threshold (D-055)
THRESHOLDS = {
    "classes": {
        "Benign": {"active_response_threshold": None, "passive_alert_threshold": None},
        "PortScan": {"active_response_threshold": 0.90, "passive_alert_threshold": 0.30},
        "DDoS_DoS": {"active_response_threshold": None, "passive_alert_threshold": 0.30,
                     "rate_limit_threshold": 0.30},
        "CnC": {"active_response_threshold": 0.30, "passive_alert_threshold": 0.30},
        "Malware_Download": {"active_response_threshold": None, "passive_alert_threshold": 0.30},
    }
}
ATTACKER, CAMERA = "10.10.10.50", "192.168.50.30"


def _engine(tmp_path: Path, rate_limit: bool = True) -> DecisionEngine:
    settings = {
        "lab": {"local_networks": ["192.168.50.0/24"]},
        "allowlist": ["192.168.50.1", "192.168.50.5", "192.168.50.10", "192.168.50.20"],
        "response": {"adapter": "simulation", "auto_response": True, "min_repeats": 3,
                     "repeat_window_seconds": 60, "max_rule_minutes": 30, "ddos_rate_limit": rate_limit},
    }
    path = tmp_path / "settings.yaml"
    path.write_text(yaml.safe_dump(settings), encoding="utf-8")
    fw = SimulationAdapter(allowlist=set(settings["allowlist"]), max_rule_minutes=30)
    return DecisionEngine(db_service=None, socketio=None, thresholds_config=THRESHOLDS,
                          settings_path=path, firewall_adapter=fw)


def _ddos(src=ATTACKER, dst=CAMERA, conf=0.6, cls="DDoS_DoS") -> DecisionOutcome:
    return DecisionOutcome(action="ACTIVE_BLOCK_CANDIDATE", predicted_class=cls, confidence=conf,
                           src_ip=src, dst_ip=dst, traffic_direction="inbound", response_status="candidate")


def test_outside_ddos_source_is_rate_limited_not_blocked(tmp_path):
    eng = _engine(tmp_path)
    assert eng.rate_limit_classes == {"DDoS_DoS"}
    outs = [_ddos() for _ in range(3)]
    for o in outs:
        eng.respond_to_outcome(o)
    assert outs[1].response_reason == "SKIP_NOT_REPEATED"  # one flood flow alone is not enough
    assert outs[2].response_status == "rate_limited"
    assert outs[2].response_reason == REASON_AUTO_DDOS_RATELIMIT
    active = eng.firewall.list_active()
    assert [r["set"] for r in active if r["ip"] == ATTACKER] == ["limit_src"]  # never block_src


def test_rate_limit_switched_off_means_alert_only(tmp_path):
    eng = _engine(tmp_path, rate_limit=False)
    assert eng.rate_limit_classes == set()
    for _ in range(5):
        o = _ddos()
        eng.respond_to_outcome(o)
    assert o.response_status == "candidate" and eng.firewall.list_active() == []


def test_local_flood_source_is_never_rate_limited():
    pol = ResponsePolicy(auto_response=True, local_networks=["192.168.50.0/24"],
                         min_confidence_map={"DDoS_DoS": 0.30}, rate_limit_classes=["DDoS_DoS"])
    for i in range(5):
        d = pol.evaluate({"predicted_class": "DDoS_DoS", "confidence": 0.9, "src_ip": CAMERA,
                          "dst_ip": "10.10.10.99"}, current_time=1000 + i)
    assert not d.should_act and d.reason_code == REASON_SKIP_PRIVATE_TARGET


def test_rate_limited_source_can_still_be_blocked_for_a_port_scan(tmp_path):
    eng = _engine(tmp_path)
    for _ in range(3):
        eng.respond_to_outcome(_ddos())
    scans = [_ddos(cls="PortScan", conf=0.95) for _ in range(3)]
    for o in scans:
        eng.respond_to_outcome(o)
    assert scans[2].response_status == "blocked"
    sets = sorted(r["set"] for r in eng.firewall.list_active() if r["ip"] == ATTACKER)
    assert sets == ["block_src", "limit_src"]


def test_runtime_settings_show_rate_limit_thresholds(tmp_path):
    eng = _engine(tmp_path)
    st = eng.get_runtime_settings()
    assert st["rate_limit_thresholds"] == {"DDoS_DoS": 0.30}
    assert "DDoS_DoS" not in st["block_thresholds"]


class _Fw:
    """Firewall that records which call startup recovery makes."""

    def __init__(self):
        self.allowlist = {"192.168.50.1"}
        self.calls = []

    def block(self, ip, direction="src", minutes=30, reason=None):
        self.calls.append(("block", ip, direction))

    def rate_limit(self, ip, minutes=30, reason=None):
        self.calls.append(("rate_limit", ip))

    def unblock(self, ip, direction="all"):
        self.calls.append(("unblock", ip))

    def list_active(self, set_name=None):
        return []


class _Db:
    def __init__(self, blocks):
        self.blocks = blocks

    def is_connected(self):
        return True

    def sweep_expired_blocks(self):
        return []

    def get_active_blocks(self, format_dates=False):
        return self.blocks

    def log_system_event(self, *a, **k):
        return "x"


def test_startup_recovery_restores_a_rate_limit_as_a_rate_limit():
    exp = datetime.now(timezone.utc) + timedelta(minutes=10)
    db = _Db([{"ip": ATTACKER, "direction": "source", "action": "rate_limit", "status": "active",
               "reason": REASON_AUTO_DDOS_RATELIMIT, "expires_at": exp},
              {"ip": "10.10.10.77", "direction": "source", "status": "active", "reason": "MANUAL_BLOCK",
               "expires_at": exp}])
    fw = _Fw()
    reconcile_on_startup(db=db, firewall=fw)
    assert ("rate_limit", ATTACKER) in fw.calls
    assert ("block", ATTACKER, "src") not in fw.calls          # never turned into a full block
    assert ("block", "10.10.10.77", "src") in fw.calls          # old records without 'action' are blocks


def test_rule_direction_of_a_rate_limit_rule():
    assert _rule_dir({"ip": ATTACKER, "set": "limit_src", "direction": "src"}) == "limit"
    assert _rule_dir({"ip": ATTACKER, "set": "block_src", "direction": "src"}) == "src"
    assert _rule_dir({"ip": ATTACKER, "set": "block_dst"}) == "dst"
