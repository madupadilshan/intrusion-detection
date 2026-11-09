"""
tests/unit/test_rule_worker.py
==============================
Unit tests for Step 34: Manual control, rule expiry, and restart recovery.
Proposal Section 3.7; Table 9 (reliability: old rules cleaned up); Objective O5.
"""

from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock
import pytest

from core_engine.rule_worker import (
    RuleExpiryWorker,
    sweep_expired_rules,
    reconcile_on_startup,
)


class FakeFirewallAdapter:
    def __init__(self, allowlist=None):
        self.allowlist = set(allowlist or ["192.168.50.1", "192.168.50.10"])
        self.active_rules = {}  # ip -> dict
        self.unblock_calls = []
        self.block_calls = []
        self.is_simulated = True

    def block(self, ip, direction="src", minutes=30, reason=None):
        rule = {
            "ip": ip,
            "direction": direction,
            "minutes": minutes,
            "reason": reason,
            "set": "block_src" if direction == "src" else "block_dst",
        }
        self.active_rules[ip] = rule
        self.block_calls.append(rule)
        return rule

    def unblock(self, ip, direction="all"):
        self.unblock_calls.append((ip, direction))
        if ip in self.active_rules:
            del self.active_rules[ip]
            return True
        return False

    def list_active(self, set_name=None):
        return list(self.active_rules.values())


class FakeDbService:
    def __init__(self):
        self.blocks = []
        self.response_actions = []
        self.system_logs = []
        self._connected = True

    def is_connected(self):
        return self._connected

    def add_block(self, ip, direction, reason, expires_at, status="active"):
        block = {
            "block_id": f"blk-{len(self.blocks)+1}",
            "ip": ip,
            "direction": direction,
            "reason": reason,
            "status": status,
            "created_at": datetime.now(timezone.utc),
            "expires_at": expires_at,
            "duration_minutes": 30,
        }
        self.blocks.append(block)
        return block

    def sweep_expired_blocks(self):
        now = datetime.now(timezone.utc)
        expired = []
        for b in self.blocks:
            if b["status"] == "active" and b["expires_at"] <= now:
                b["status"] = "expired"
                b["unblocked_at"] = now
                b["unblock_reason"] = "RULE_TIMEOUT_EXPIRED"
                b["unblock_actor"] = "system_auto"
                expired.append(b)
        return expired

    def get_active_blocks(self, format_dates=False):
        return [b for b in self.blocks if b["status"] == "active"]

    def log_response_action(self, action_data):
        self.response_actions.append(action_data)
        return "act-123"

    def log_system_event(self, actor, event=None, outcome="INFO", details=None):
        doc = {
            "actor": actor,
            "event": event,
            "outcome": outcome,
            "details": details or {},
            "timestamp": datetime.now(timezone.utc),
        }
        self.system_logs.append(doc)
        return "log-123"


def test_sweep_expired_rules_prunes_only_expired():
    db = FakeDbService()
    now = datetime.now(timezone.utc)

    # 1. Expired rule
    db.add_block(
        ip="192.168.50.150",
        direction="source",
        reason="Port scan test",
        expires_at=now - timedelta(minutes=5),
    )
    # 2. Still active rule
    db.add_block(
        ip="192.168.50.160",
        direction="source",
        reason="C&C beacon test",
        expires_at=now + timedelta(minutes=25),
    )

    fw = FakeFirewallAdapter()
    fw.active_rules["192.168.50.150"] = {"ip": "192.168.50.150", "set": "block_src"}
    fw.active_rules["192.168.50.160"] = {"ip": "192.168.50.160", "set": "block_src"}

    socketio = MagicMock()
    decision_engine = MagicMock()

    swept = sweep_expired_rules(
        db=db,
        firewall=fw,
        socketio=socketio,
        decision_engine=decision_engine,
    )

    assert len(swept) == 1
    assert swept[0]["ip"] == "192.168.50.150"
    assert swept[0]["status"] == "expired"

    # Firewall unblock called for expired IP only
    assert ("192.168.50.150", "all") in fw.unblock_calls
    assert "192.168.50.150" not in fw.active_rules
    assert "192.168.50.160" in fw.active_rules

    # Decision engine notified
    decision_engine.forget_block.assert_called_once_with("192.168.50.150")

    # Audit records created
    assert any(
        a["action"] == "expire" and a["target_ip"] == "192.168.50.150"
        for a in db.response_actions
    )
    assert any(
        log["event"] == "RULE_EXPIRED" and log["details"]["ip"] == "192.168.50.150"
        for log in db.system_logs
    )

    # Real-time WebSocket event emitted
    socketio.emit.assert_called_once()
    args, kwargs = socketio.emit.call_args
    assert args[0] == "blocklist_update"
    assert args[1]["ip"] == "192.168.50.150"
    assert args[1]["status"] == "expired"


def test_reconcile_on_startup_restores_missing_rules():
    db = FakeDbService()
    now = datetime.now(timezone.utc)

    # Active block in DB that firewall lost due to reboot
    db.add_block(
        ip="192.168.50.170",
        direction="source",
        reason="PortScan active",
        expires_at=now + timedelta(minutes=20),
    )

    fw = FakeFirewallAdapter()  # Empty active_rules (simulating flushed firewall)

    summary = reconcile_on_startup(db=db, firewall=fw)

    assert summary["restored"] == 1
    assert "192.168.50.170" in fw.active_rules
    restored_rule = fw.active_rules["192.168.50.170"]
    assert restored_rule["direction"] == "src"
    assert 18 <= restored_rule["minutes"] <= 21

    # Check recovery audit in system_logs
    assert any(
        log["event"] == "STARTUP_RULE_RESTORED" and log["details"]["ip"] == "192.168.50.170"
        for log in db.system_logs
    )
    assert any(
        log["event"] == "STARTUP_RECOVERY_COMPLETE"
        for log in db.system_logs
    )


def test_reconcile_on_startup_sweeps_offline_expired():
    db = FakeDbService()
    now = datetime.now(timezone.utc)

    # Block that expired while the server was offline
    db.add_block(
        ip="192.168.50.180",
        direction="source",
        reason="Expired during crash",
        expires_at=now - timedelta(minutes=15),
    )

    fw = FakeFirewallAdapter()
    fw.active_rules["192.168.50.180"] = {"ip": "192.168.50.180"}

    summary = reconcile_on_startup(db=db, firewall=fw)

    assert summary["expired_while_down"] == 1
    assert "192.168.50.180" not in fw.active_rules
    assert any(
        log["event"] == "RULE_EXPIRED" and log["details"]["ip"] == "192.168.50.180"
        for log in db.system_logs
    )


def test_reconcile_on_startup_prunes_orphans():
    db = FakeDbService()
    fw = FakeFirewallAdapter()

    # Orphan rule in firewall that has no active record in MongoDB
    fw.active_rules["192.168.50.199"] = {"ip": "192.168.50.199", "set": "block_src"}

    summary = reconcile_on_startup(db=db, firewall=fw)

    assert summary["orphans_removed"] == 1
    assert "192.168.50.199" not in fw.active_rules
    assert any(
        log["event"] == "STARTUP_ORPHAN_RULE_REMOVED"
        and log["details"]["ip"] == "192.168.50.199"
        for log in db.system_logs
    )


def test_reconcile_on_startup_protects_allowlist():
    db = FakeDbService()
    fw = FakeFirewallAdapter(allowlist=["192.168.50.1"])

    # Rogue or accidental block on gateway router
    fw.active_rules["192.168.50.1"] = {"ip": "192.168.50.1", "set": "block_src"}

    summary = reconcile_on_startup(db=db, firewall=fw)

    assert summary["allowlist_cleanups"] == 1
    assert "192.168.50.1" not in fw.active_rules
    assert any(
        log["event"] == "STARTUP_ALLOWLIST_PROTECTION"
        and log["details"]["ip"] == "192.168.50.1"
        for log in db.system_logs
    )


def test_rule_expiry_worker_lifecycle():
    db = FakeDbService()
    fw = FakeFirewallAdapter()

    worker = RuleExpiryWorker(db=db, firewall=fw, interval_seconds=1)
    assert not worker.is_running

    started = worker.start()
    assert started
    assert worker.is_running

    status = worker.get_status()
    assert status["running"] is True
    assert status["interval_seconds"] == 1

    stopped = worker.stop(timeout=2.0)
    assert stopped
    assert not worker.is_running


def test_rule_expiry_worker_sweep_now():
    db = FakeDbService()
    fw = FakeFirewallAdapter()

    now = datetime.now(timezone.utc)
    db.add_block(
        ip="192.168.50.210",
        direction="source",
        reason="Manual sweep test",
        expires_at=now - timedelta(seconds=10),
    )

    worker = RuleExpiryWorker(db=db, firewall=fw, interval_seconds=10)
    expired = worker.sweep_now()

    assert len(expired) == 1
    status = worker.get_status()
    assert status["total_sweeps"] == 1
    assert status["last_expired_count"] == 1
    assert status["last_sweep_time"] is not None
