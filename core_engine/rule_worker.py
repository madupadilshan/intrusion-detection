"""
core_engine/rule_worker.py
==========================
Real-Time Intrusion Detection and Autonomous Response System for IP-Camera IoT Networks
Group 03 - University of Sri Jayewardenepura

Step 34: Manual Control, Rule Expiry, and Restart Recovery.
Proposal Section 3.7; Table 9 (reliability: old rules cleaned up); Objective O5.

Responsibilities:
  1. Background Rule Expiry Worker:
     - Periodically sweeps active blocking rules in MongoDB that have passed expires_at.
     - Transitions MongoDB records from 'active' to 'expired' with audit timestamps.
     - Calls firewall_adapter.unblock() if the adapter does not support automatic kernel-level timeout,
       or ensures elements are pruned.
     - Emits real-time Socket.IO 'blocklist_update' events with status='expired' to notify React dashboard.
     - Records audit trail in MongoDB 'system_logs' and 'response_actions'.
  2. Crash and Restart Recovery:
     - Reconciles active firewall rules with MongoDB 'blocklist' at application startup.
     - Sweeps rules that expired while the service was stopped.
     - Re-enacts still-active blocks on the firewall adapter with remaining clamped minutes.
     - Prunes orphaned rules from the firewall adapter if they are not in MongoDB.
     - Enforces management allowlist immunity against orphaned or accidental firewall rules.
     - Logs all startup reconciliation actions to 'system_logs'.
"""

from datetime import datetime, timezone
import logging
import math
import threading
import time
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger("ids.rule_worker")


def _dir_code(direction: Any) -> str:
    """Blocklist direction ('source', 'destination', 'src', 'dst', 'inbound', 'outbound') -> 'src' / 'dst'."""
    return "dst" if str(direction).lower() in ("destination", "dst", "outbound") else "src"


def _rule_dir(rule: Dict[str, Any]) -> str:
    """Direction of an active firewall rule: 'src', 'dst' or 'limit' (from its direction or set name)."""
    d = str(rule.get("direction", "")).lower()
    if d in ("src", "dst"):
        return d
    set_name = str(rule.get("set", "")).lower()
    if "limit" in set_name:
        return "limit"
    return "dst" if "dst" in set_name else "src"


def sweep_expired_rules(
    db: Any,
    firewall: Any,
    socketio: Optional[Any] = None,
    decision_engine: Optional[Any] = None,
) -> List[Dict[str, Any]]:
    """
    Find and transition all active blocklist entries that have expired.
    Unblocks the IP on the firewall adapter, notifies the decision engine,
    records audit log entries, and broadcasts a real-time WebSocket update.

    :param db: DatabaseService instance
    :param firewall: BaseFirewallAdapter instance
    :param socketio: Flask-SocketIO instance
    :param decision_engine: DecisionEngine instance (optional)
    :return: List of swept expired block dictionaries
    """
    if db is None:
        return []

    # Retrieve expired blocks from DB
    if hasattr(db, "sweep_expired_blocks"):
        expired_docs = db.sweep_expired_blocks()
    else:
        # Fallback for mock objects
        now = datetime.now(timezone.utc)
        expired_docs = []
        if hasattr(db, "blocklist") and db.blocklist is not None:
            try:
                cursor = db.blocklist.find({"status": "active", "expires_at": {"$lte": now}})
                expired_docs = list(cursor)
                if expired_docs:
                    ids = [d["_id"] for d in expired_docs]
                    db.blocklist.update_many(
                        {"_id": {"$in": ids}},
                        {
                            "$set": {
                                "status": "expired",
                                "unblocked_at": now,
                                "unblock_reason": "RULE_TIMEOUT_EXPIRED",
                                "unblock_actor": "system_auto",
                            }
                        },
                    )
            except Exception as e:
                logger.error("Error finding expired blocks in fallback: %s", e)

    if not expired_docs:
        return []

    now_iso = datetime.now(timezone.utc).isoformat()
    is_sim = getattr(firewall, "is_simulated", True)

    for doc in expired_docs:
        ip = doc.get("ip")
        if not ip:
            continue

        direction = doc.get("direction", "source")

        # 1. Unblock on firewall adapter. nftables may already have removed the element by its own
        #    timeout; that is fine. A real error is recorded in the audit entries below.
        fw_error: Optional[str] = None
        if firewall is not None:
            try:
                firewall.unblock(ip=ip, direction="all")
            except Exception as exc:
                fw_error = str(exc)
                logger.warning("Firewall unblock during expiry failed for %s: %s", ip, exc)

        # 2. Inform decision engine so repeats can be tracked afresh
        if decision_engine is not None and hasattr(decision_engine, "forget_block"):
            try:
                decision_engine.forget_block(ip)
            except Exception as exc:
                logger.warning("Decision engine forget_block failed for %s: %s", ip, exc)

        # 3. Log response action in MongoDB
        if hasattr(db, "log_response_action"):
            try:
                db.log_response_action({
                    "action": "expire",
                    "target_ip": ip,
                    "direction": direction,
                    "rule": f"expire ip {ip}",
                    "reason_code": "RULE_TIMEOUT_EXPIRED",
                    "actor": "system_auto",
                    "status": "applied" if fw_error is None else "firewall_error",
                    "error": fw_error,
                    "simulated": is_sim,
                })
            except Exception as exc:
                logger.warning("Logging response action failed for %s: %s", ip, exc)

        # 4. Log system audit event in MongoDB
        if hasattr(db, "log_system_event"):
            try:
                db.log_system_event(
                    actor="system_auto",
                    event="RULE_EXPIRED",
                    outcome="SUCCESS" if fw_error is None else "PARTIAL",
                    details={
                        "ip": ip,
                        "firewall_error": fw_error,
                        "block_id": doc.get("block_id"),
                        "direction": direction,
                        "duration_minutes": doc.get("duration_minutes"),
                        "reason": doc.get("reason"),
                    },
                )
            except Exception as exc:
                logger.warning("Logging system event failed for %s: %s", ip, exc)

        # 5. Broadcast real-time Socket.IO update
        if socketio is not None:
            try:
                socketio.emit("blocklist_update", {
                    "ip": ip,
                    "status": "expired",
                    "unblock_actor": "system_auto",
                    "unblock_reason": "RULE_TIMEOUT_EXPIRED",
                    "simulated": is_sim,
                    "timestamp": now_iso,
                })
            except Exception as exc:
                logger.warning("SocketIO broadcast failed for expired %s: %s", ip, exc)

    logger.info("Swept and expired %d firewall rule(s).", len(expired_docs))
    return expired_docs


def reconcile_on_startup(
    db: Any,
    firewall: Any,
    socketio: Optional[Any] = None,
    decision_engine: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Reconcile active firewall rules with MongoDB blocklist collection at startup.
    - Sweeps rules that expired while the server was down.
    - Re-enacts still-active blocks on the firewall adapter with remaining clamped minutes.
    - Prunes orphaned rules from the firewall adapter if they are absent in MongoDB.
    - Enforces management allowlist immunity against any orphaned or accidental firewall rules.
    - Writes all actions to MongoDB system_logs for complete forensic transparency (Step 34).

    :param db: DatabaseService instance
    :param firewall: BaseFirewallAdapter instance
    :param socketio: Flask-SocketIO instance (optional)
    :param decision_engine: DecisionEngine instance (optional)
    :return: Summary dictionary of reconciliation actions
    """
    summary = {
        "status": "success",
        "restored": 0,
        "expired_while_down": 0,
        "orphans_removed": 0,
        "allowlist_cleanups": 0,
        "restore_failed": 0,
    }

    if db is None:
        return summary

    # Step 1: Sweep rules that expired while offline
    try:
        expired_docs = sweep_expired_rules(
            db=db,
            firewall=firewall,
            socketio=socketio,
            decision_engine=decision_engine,
        )
        summary["expired_while_down"] = len(expired_docs)
    except Exception as exc:
        logger.error("Startup reconciliation failed during expired sweep: %s", exc)

    # Step 2: Retrieve all remaining active DB blocks
    active_db_blocks: List[Dict[str, Any]] = []
    try:
        if hasattr(db, "get_active_blocks"):
            active_db_blocks = db.get_active_blocks(format_dates=False)
        elif hasattr(db, "blocklist") and db.blocklist is not None:
            active_db_blocks = list(db.blocklist.find({"status": "active"}))
    except Exception as exc:
        logger.error("Failed to query active DB blocks at startup: %s", exc)

    # Step 3: Query active rules on firewall adapter
    active_fw_rules: List[Dict[str, Any]] = []
    if firewall is not None and hasattr(firewall, "list_active"):
        try:
            active_fw_rules = firewall.list_active()
        except Exception as exc:
            logger.error("Failed to list active firewall rules at startup: %s", exc)

    fw_keys: Set[Any] = {(r.get("ip"), _rule_dir(r)) for r in active_fw_rules if r.get("ip")}
    db_ips: Set[str] = set()
    now = datetime.now(timezone.utc)
    allowlist: Set[str] = set(getattr(firewall, "allowlist", None) or set())

    # Step 4: Re-enact active DB rules missing on firewall
    for block in active_db_blocks:
        ip = block.get("ip")
        if not ip:
            continue
        direction = block.get("direction", "source")
        dir_code = _dir_code(direction)

        # Never restore a block on an allowlisted host (proposal 3.7); close the database record instead.
        if ip in allowlist:
            if hasattr(db, "remove_from_blocklist"):
                try:
                    db.remove_from_blocklist(ip=ip, reason="STARTUP_ALLOWLIST_PROTECTION", actor="system_recovery")
                except Exception as exc:
                    logger.warning("Could not close allowlisted DB block for %s: %s", ip, exc)
            summary["allowlist_cleanups"] += 1
            if hasattr(db, "log_system_event"):
                try:
                    db.log_system_event(
                        actor="system_recovery",
                        event="STARTUP_ALLOWLIST_PROTECTION",
                        outcome="WARNING",
                        details={"ip": ip, "source": "database", "block_id": block.get("block_id")},
                    )
                except Exception as exc:
                    logger.warning("Failed to log STARTUP_ALLOWLIST_PROTECTION: %s", exc)
            continue

        db_ips.add(ip)
        if (ip, dir_code) in fw_keys:
            continue

        exp = block.get("expires_at")
        remaining_mins = 30
        if exp:
            if getattr(exp, "tzinfo", None) is None:
                exp = exp.replace(tzinfo=timezone.utc)
            remaining_secs = (exp - now).total_seconds()
            # Round up, so a restored rule never ends before the time in the database.
            remaining_mins = max(1, int(math.ceil(remaining_secs / 60.0)))

        restore_error: Optional[str] = None
        if firewall is None:
            restore_error = "no firewall adapter"
        else:
            try:
                firewall.block(
                    ip=ip,
                    direction=dir_code,
                    minutes=remaining_mins,
                    reason=block.get("reason", "Startup recovery restoration"),
                )
                summary["restored"] += 1
            except Exception as exc:
                restore_error = str(exc)
                logger.error("Failed to re-enact rule on firewall for %s: %s", ip, exc)
        if restore_error is not None:
            summary["restore_failed"] += 1

        if hasattr(db, "log_system_event"):
            try:
                db.log_system_event(
                    actor="system_recovery",
                    event="STARTUP_RULE_RESTORED",
                    outcome="SUCCESS" if restore_error is None else "FAILURE",
                    details={
                        "ip": ip,
                        "direction": direction,
                        "remaining_minutes": remaining_mins,
                        "block_id": block.get("block_id"),
                        "error": restore_error,
                    },
                )
            except Exception as exc:
                logger.warning("Failed to log STARTUP_RULE_RESTORED for %s: %s", ip, exc)

    # Step 5: Check firewall active rules for orphaned or allowlisted rules
    for r in active_fw_rules:
        r_ip = r.get("ip")
        if not r_ip:
            continue

        if r_ip in allowlist:
            # Allowlist safety override
            if firewall is not None:
                try:
                    firewall.unblock(r_ip, direction="all")
                    summary["allowlist_cleanups"] += 1
                except Exception as exc:
                    logger.error("Failed to unblock allowlisted IP %s at startup: %s", r_ip, exc)

            if hasattr(db, "log_system_event"):
                try:
                    db.log_system_event(
                        actor="system_recovery",
                        event="STARTUP_ALLOWLIST_PROTECTION",
                        outcome="WARNING",
                        details={"ip": r_ip, "set": r.get("set")},
                    )
                except Exception as exc:
                    logger.warning("Failed to log STARTUP_ALLOWLIST_PROTECTION: %s", exc)

        elif r_ip not in db_ips:
            # Orphan rule not present in active DB blocks
            if firewall is not None:
                try:
                    firewall.unblock(r_ip, direction="all")
                    summary["orphans_removed"] += 1
                except Exception as exc:
                    logger.error("Failed to prune orphan rule for %s at startup: %s", r_ip, exc)

            if hasattr(db, "log_system_event"):
                try:
                    db.log_system_event(
                        actor="system_recovery",
                        event="STARTUP_ORPHAN_RULE_REMOVED",
                        outcome="SUCCESS",
                        details={"ip": r_ip, "set": r.get("set")},
                    )
                except Exception as exc:
                    logger.warning("Failed to log STARTUP_ORPHAN_RULE_REMOVED: %s", exc)

    # Step 6: Log overall reconciliation completion
    if summary["restore_failed"]:
        summary["status"] = "partial"
    if hasattr(db, "log_system_event"):
        try:
            db.log_system_event(
                actor="system_recovery",
                event="STARTUP_RECOVERY_COMPLETE",
                outcome="SUCCESS" if summary["status"] == "success" else "PARTIAL",
                details=summary,
            )
        except Exception as exc:
            logger.warning("Failed to log STARTUP_RECOVERY_COMPLETE: %s", exc)

    logger.info("Startup reconciliation finished: %s", summary)
    return summary


class RuleExpiryWorker:
    """
    Background worker daemon running periodic rule expiration sweeps.
    """

    def __init__(
        self,
        db: Any,
        firewall: Any,
        socketio: Optional[Any] = None,
        decision_engine: Optional[Any] = None,
        interval_seconds: int = 10,
    ):
        """
        Initialize the rule expiry worker.

        :param db: DatabaseService instance
        :param firewall: BaseFirewallAdapter instance
        :param socketio: Flask-SocketIO instance (optional)
        :param decision_engine: DecisionEngine instance (optional)
        :param interval_seconds: Sweep loop cycle period in seconds (default 10)
        """
        self.db = db
        self.firewall = firewall
        self.socketio = socketio
        self.decision_engine = decision_engine
        self.interval_seconds = max(1, int(interval_seconds))

        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.RLock()
        self._sweeps_count = 0
        self._last_sweep_time: Optional[str] = None
        self._last_expired_count = 0

    @property
    def is_running(self) -> bool:
        """Returns True if the background worker thread is active."""
        with self._lock:
            return self._thread is not None and self._thread.is_alive()

    def start(self) -> bool:
        """
        Start the background worker thread.
        Returns True if started, False if already running.
        """
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                logger.warning("RuleExpiryWorker is already running.")
                return False

            self._stop_event.clear()
            self._thread = threading.Thread(
                target=self._run_loop,
                name="ids_rule_expiry_worker",
                daemon=True,
            )
            self._thread.start()
            logger.info("RuleExpiryWorker started with %ds interval.", self.interval_seconds)
            return True

    def stop(self, timeout: float = 3.0) -> bool:
        """
        Signal the worker thread to stop and wait for termination.
        Returns True if stopped cleanly.
        """
        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                return True

            self._stop_event.set()
            thread = self._thread

        thread.join(timeout=timeout)
        stopped = not thread.is_alive()
        if stopped:
            logger.info("RuleExpiryWorker stopped cleanly.")
        else:
            logger.warning("RuleExpiryWorker did not stop within %.1fs timeout.", timeout)
        return stopped

    def sweep_now(self) -> List[Dict[str, Any]]:
        """
        Trigger an immediate on-demand sweep outside the timer interval.
        """
        with self._lock:
            expired = sweep_expired_rules(
                db=self.db,
                firewall=self.firewall,
                socketio=self.socketio,
                decision_engine=self.decision_engine,
            )
            self._sweeps_count += 1
            self._last_sweep_time = datetime.now(timezone.utc).isoformat()
            self._last_expired_count = len(expired)
            return expired

    def get_status(self) -> Dict[str, Any]:
        """Retrieve telemetry status of the worker."""
        with self._lock:
            return {
                "running": self.is_running,
                "interval_seconds": self.interval_seconds,
                "total_sweeps": self._sweeps_count,
                "last_sweep_time": self._last_sweep_time,
                "last_expired_count": self._last_expired_count,
            }

    def _run_loop(self) -> None:
        """Internal daemon loop."""
        logger.info("RuleExpiryWorker background loop initiated.")
        while not self._stop_event.is_set():
            try:
                self.sweep_now()
            except Exception as exc:
                logger.error("Unhandled error in RuleExpiryWorker loop: %s", exc, exc_info=True)

            # Wait for next interval or stop signal
            if self._stop_event.wait(self.interval_seconds):
                break

        logger.info("RuleExpiryWorker background loop terminated.")
