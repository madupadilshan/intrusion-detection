"""
tests/unit/test_runner.py - Unit tests for LivePipelineRunner (Problem 1 Fix).
==============================================================================
"""

import time
import pytest
from unittest.mock import MagicMock

from core_engine.runner import LivePipelineRunner
from core_engine.decision_engine import DecisionOutcome


def test_runner_initialization():
    """Verify runner instantiates with default stopped state and zero metrics."""
    mock_adapter = MagicMock()
    mock_engine = MagicMock()
    mock_sio = MagicMock()

    runner = LivePipelineRunner(
        zeek_adapter=mock_adapter,
        decision_engine=mock_engine,
        socketio=mock_sio,
        auto_start=False,
    )

    status = runner.get_status()
    assert status["status"] == "stopped"
    assert status["is_running"] is False
    assert status["metrics"]["batches_processed"] == 0
    assert status["metrics"]["flows_processed"] == 0


def test_runner_start_stop_lifecycle():
    """Verify background worker thread starts and terminates gracefully."""
    mock_adapter = MagicMock()
    # Generator that yields nothing or blocks on stop_event
    def mock_tail(seek_end=False, stop_event=None):
        while not (stop_event and stop_event.is_set()):
            time.sleep(0.01)
            yield []

    mock_adapter.tail_batches.side_effect = mock_tail
    mock_engine = MagicMock()

    runner = LivePipelineRunner(
        zeek_adapter=mock_adapter,
        decision_engine=mock_engine,
        auto_start=False,
    )

    started = runner.start()
    assert started is True
    assert runner.is_running is True

    # Duplicate start should return False
    duplicate = runner.start()
    assert duplicate is False

    stopped = runner.stop(timeout=1.0)
    assert stopped is True
    assert runner.is_running is False
    assert runner.get_status()["status"] == "stopped"


def test_runner_batch_processing_and_metrics():
    """Verify batch processing delegates to DecisionEngine and updates metrics."""
    mock_adapter = MagicMock()
    mock_engine = MagicMock()

    sample_flow = {"uid": "CFlow1", "id.orig_h": "192.168.50.150"}
    mock_outcome = DecisionOutcome(
        flow_id="CFlow1",
        src_ip="192.168.50.150",
        dst_ip="192.168.50.10",
        predicted_class="DDoS_DoS",
        confidence=0.98,
        action="ACTIVE_BLOCK_CANDIDATE",
        response_status="blocked",
    )
    mock_engine.process_flows.return_value = [mock_outcome]

    runner = LivePipelineRunner(
        zeek_adapter=mock_adapter,
        decision_engine=mock_engine,
        auto_start=False,
    )

    outcomes = runner._process_batch([sample_flow])
    assert len(outcomes) == 1
    mock_engine.process_flows.assert_called_once_with([sample_flow])

    status = runner.get_status()
    assert status["metrics"]["batches_processed"] == 1
    assert status["metrics"]["flows_processed"] == 1
    assert status["metrics"]["attacks_detected"] == 1
    assert status["metrics"]["mitigations_dispatched"] == 1
    assert status["metrics"]["last_active"] is not None
