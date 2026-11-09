"""
core_engine/runner.py - Live Intrusion Detection & Telemetry Pipeline Runner.
=============================================================================

Governing Standards & Requirements:
- Group 03 Proposal: Figures 2 & 3 ("Intrusion Detection Pipeline");
  Sections 3.3, 3.5, 3.7; Requirements Table 7: FR-01, FR-02, FR-03, FR-04, FR-06;
  Table 9 latency target (median decision < 2 s, 95th percentile < 5 s).
- Connects the streaming Zeek conn.log reader directly into DecisionEngine.process_flows().
- Enables real-time, zero-reload alert dispatch to the React SOC Dashboard via WebSockets.
"""

from __future__ import annotations

import logging
import threading
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from core_engine.decision_engine import DecisionEngine, DecisionOutcome
from core_engine.zeek_adapter import ZeekAdapter

logger = logging.getLogger("core_engine.runner")


class LivePipelineRunner:
    """
    Continuous background daemon worker connecting Zeek log telemetry
    to the Machine Learning Detector, Decision Policy, MongoDB, and WebSocket Alert stream.
    """

    def __init__(
        self,
        zeek_adapter: Optional[ZeekAdapter] = None,
        decision_engine: Optional[DecisionEngine] = None,
        socketio: Optional[Any] = None,
        auto_start: bool = False,
    ) -> None:
        self.zeek_adapter = zeek_adapter or ZeekAdapter()
        self.decision_engine = decision_engine or DecisionEngine(socketio=socketio)
        self.socketio = socketio

        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._lock = threading.RLock()
        self._status = "stopped"
        self._error_message: Optional[str] = None

        self._metrics: Dict[str, Any] = {
            "started_at": None,
            "last_active": None,
            "batches_processed": 0,
            "flows_processed": 0,
            "attacks_detected": 0,
            "mitigations_dispatched": 0,
        }

        if auto_start:
            self.start()

    @property
    def is_running(self) -> bool:
        """Check if background worker thread is currently active."""
        with self._lock:
            return self._status == "running" and self._thread is not None and self._thread.is_alive()

    def get_status(self) -> Dict[str, Any]:
        """Return runtime status and telemetry metrics for operator monitoring."""
        with self._lock:
            return {
                "status": self._status,
                "is_running": self.is_running,
                "error_message": self._error_message,
                "conn_log_path": str(self.zeek_adapter.conn_log_path),
                "metrics": dict(self._metrics),
            }

    def start(self) -> bool:
        """
        Start the background streaming worker thread.
        Returns True if started, False if already running.
        """
        with self._lock:
            if self._status == "running" and self._thread and self._thread.is_alive():
                logger.warning("LivePipelineRunner is already running.")
                return False

            self._stop_event.clear()
            self._status = "running"
            self._error_message = None
            self._metrics["started_at"] = datetime.now(timezone.utc).isoformat()

            self._thread = threading.Thread(
                target=self._worker_loop,
                name="LivePipelineRunnerThread",
                daemon=True,
            )
            self._thread.start()
            logger.info(
                "LivePipelineRunner started in background, tailing: %s",
                self.zeek_adapter.conn_log_path,
            )
            return True

    def stop(self, timeout: float = 2.0) -> bool:
        """
        Signal the background worker to stop and wait for thread termination.
        Returns True if cleanly stopped.
        """
        with self._lock:
            if not self._thread or not self._thread.is_alive():
                self._status = "stopped"
                return True

            logger.info("Signaling LivePipelineRunner to stop...")
            self._stop_event.set()
            self.zeek_adapter.stop()

        self._thread.join(timeout=timeout)

        with self._lock:
            if self._thread.is_alive():
                logger.warning("LivePipelineRunner thread did not terminate within timeout.")
                self._status = "stopping"
                return False

            self._status = "stopped"
            self._thread = None
            logger.info("LivePipelineRunner stopped cleanly.")
            return True

    def _worker_loop(self) -> None:
        """Main daemon loop consuming micro-batches from Zeek and executing decision pipeline."""
        logger.info("Live worker loop active.")
        try:
            # tail_batches yields batches when batch_size is reached or batch_timeout elapses
            for batch in self.zeek_adapter.tail_batches(seek_end=False, stop_event=self._stop_event):
                if self._stop_event.is_set():
                    break

                if batch:
                    self._process_batch(batch)

        except Exception as exc:
            logger.error("LivePipelineRunner worker encountered unhandled exception: %s", exc, exc_info=True)
            with self._lock:
                self._status = "error"
                self._error_message = str(exc)
        finally:
            with self._lock:
                if self._status != "error":
                    self._status = "stopped"
            logger.info("Live worker loop exited.")

    def _process_batch(self, batch: List[Dict[str, Any]]) -> List[DecisionOutcome]:
        """Pass a flow batch to DecisionEngine and update metrics."""
        now_iso = datetime.now(timezone.utc).isoformat()
        try:
            outcomes = self.decision_engine.process_flows(batch)
            attacks = [
                o for o in outcomes
                if getattr(o, "action", "") in ("ALERT_ONLY", "ACTIVE_BLOCK_CANDIDATE")
            ]
            # DecisionEngine.process_flows() runs the response policy for every block
            # candidate (respond_to_outcome); a new firewall rule sets these statuses.
            mitigations = [
                o for o in outcomes
                if getattr(o, "response_status", "") in ("blocked", "rate_limited")
            ]

            with self._lock:
                self._metrics["batches_processed"] += 1
                self._metrics["flows_processed"] += len(batch)
                self._metrics["attacks_detected"] += len(attacks)
                self._metrics["mitigations_dispatched"] += len(mitigations)
                self._metrics["last_active"] = now_iso

            return outcomes
        except Exception as exc:
            logger.error("Error processing batch of %d flows: %s", len(batch), exc)
            return []
