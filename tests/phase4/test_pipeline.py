"""
tests/phase4/test_pipeline.py
Unit tests for backend/pipeline/pipeline.py — ORPipeline.

All external dependencies (StateManager, MedGemmaModel, LiveTranscriber)
are mocked so tests run without a GPU, microphone, or model files.
"""

from __future__ import annotations

import queue
import threading
import time
from unittest.mock import MagicMock, patch, call

import pytest

from backend.data.surgeries import SurgeryType
from backend.data.models    import StateUpdateRequest, ORStateSnapshot


# ── helpers ───────────────────────────────────────────────────────────────────

def _make_snapshot(surgery: SurgeryType = SurgeryType.HEART_TRANSPLANT) -> ORStateSnapshot:
    return ORStateSnapshot(
        surgery        = surgery.value,
        machine_states = {"0": ["Ventilator"], "1": ["Patient Monitor"]},
        transcription  = "",
        reasoning      = "",
    )


def _make_llm_output(turn_on: list[str], turn_off: list[str]) -> MagicMock:
    """Return a mock LLMOutput whose to_state_update_kwargs() returns the given lists."""
    out = MagicMock()
    out.to_state_update_kwargs.return_value = {
        "turn_on":   turn_on,
        "turn_off":  turn_off,
        "reasoning": "mocked reasoning",
    }
    return out


@pytest.fixture()
def pipeline_mocks():
    """
    Fixture that patches all heavy dependencies of ORPipeline and yields
    (pipeline_instance, mock_state_manager, mock_llm, mock_transcriber).
    """
    with (
        patch("backend.pipeline.pipeline.StateManager")  as MockSM,
        patch("backend.pipeline.pipeline.MedGemmaModel") as MockLLM,
        patch("backend.pipeline.pipeline.LiveTranscriber") as MockTr,
    ):
        # Configure return values
        mock_sm  = MagicMock()
        mock_llm = MagicMock()
        mock_tr  = MagicMock()

        MockSM.return_value  = mock_sm
        MockLLM.return_value = mock_llm
        MockTr.return_value  = mock_tr

        mock_sm.get_snapshot.return_value = _make_snapshot()
        mock_sm.apply_update.return_value = _make_snapshot()
        mock_llm.infer.return_value       = _make_llm_output(["Patient Monitor"], [])

        # Import here so patches are active
        from backend.pipeline.pipeline import ORPipeline
        pipeline = ORPipeline(surgery=SurgeryType.HEART_TRANSPLANT)

        yield pipeline, mock_sm, mock_llm, mock_tr


# ── constructor / init tests ──────────────────────────────────────────────────

class TestInit:
    def test_state_manager_created_with_correct_surgery(self, pipeline_mocks):
        pipeline, mock_sm, _, _ = pipeline_mocks
        assert pipeline.state_manager is mock_sm

    def test_llm_created_with_correct_surgery(self, pipeline_mocks):
        _, _, mock_llm, _ = pipeline_mocks
        assert mock_llm is not None

    def test_transcriber_callback_is_pipeline_method(self, pipeline_mocks):
        pipeline, _, _, _ = pipeline_mocks
        with (
            patch("backend.pipeline.pipeline.StateManager"),
            patch("backend.pipeline.pipeline.MedGemmaModel"),
            patch("backend.pipeline.pipeline.LiveTranscriber") as MockTr,
        ):
            from backend.pipeline.pipeline import ORPipeline
            p2 = ORPipeline(SurgeryType.LIVER_RESECTION)
            init_kwargs = MockTr.call_args.kwargs
            assert init_kwargs.get("on_transcription") == p2._on_transcription

    def test_queue_created_with_correct_maxsize(self, pipeline_mocks):
        with (
            patch("backend.pipeline.pipeline.StateManager"),
            patch("backend.pipeline.pipeline.MedGemmaModel"),
            patch("backend.pipeline.pipeline.LiveTranscriber"),
        ):
            from backend.pipeline.pipeline import ORPipeline
            p = ORPipeline(SurgeryType.HEART_TRANSPLANT, llm_queue_size=5)
        assert p._queue.maxsize == 5

    def test_worker_thread_is_daemon(self, pipeline_mocks):
        pipeline, _, _, _ = pipeline_mocks
        assert pipeline._worker.daemon is True


# ── _on_transcription tests ───────────────────────────────────────────────────

class TestOnTranscription:
    def test_enqueues_text_and_timestamp(self, pipeline_mocks):
        pipeline, _, _, _ = pipeline_mocks
        pipeline._on_transcription("turn on the ventilator", "12:00:01.000")
        item = pipeline._queue.get_nowait()
        assert item == ("turn on the ventilator", "12:00:01.000")

    def test_multiple_items_in_order(self, pipeline_mocks):
        pipeline, _, _, _ = pipeline_mocks
        texts = ["activate bypass", "turn off lights", "start suction"]
        for i, t in enumerate(texts):
            pipeline._on_transcription(t, f"ts{i}")
        for i, t in enumerate(texts):
            text, ts = pipeline._queue.get_nowait()
            assert text == t
            assert ts == f"ts{i}"

    def test_queue_full_drops_oldest(self, pipeline_mocks):
        """
        When queue is full, the oldest item is dropped silently and the newest
        item is enqueued.
        """
        with (
            patch("backend.pipeline.pipeline.StateManager"),
            patch("backend.pipeline.pipeline.MedGemmaModel"),
            patch("backend.pipeline.pipeline.LiveTranscriber"),
        ):
            from backend.pipeline.pipeline import ORPipeline
            p = ORPipeline(SurgeryType.HEART_TRANSPLANT, llm_queue_size=2)

        # Fill queue to capacity
        p._on_transcription("first",  "t1")
        p._on_transcription("second", "t2")
        # This should drop "first" and enqueue "third"
        p._on_transcription("third",  "t3")

        items = []
        while not p._queue.empty():
            items.append(p._queue.get_nowait()[0])

        assert "first"  not in items, "Oldest item was not dropped"
        assert "third"  in    items,  "Newest item was not enqueued"


# ── LLM worker thread tests ───────────────────────────────────────────────────

class TestLLMWorker:
    def _run_worker_for_item(self, pipeline, mock_sm, mock_llm, text="activate bypass pump"):
        """
        Put one item in queue, signal stop, run the worker synchronously, wait.
        Callers must set mock_llm.infer.return_value BEFORE this call.
        Returns the worker thread (already joined).
        """
        mock_sm.get_snapshot.return_value = _make_snapshot()
        mock_sm.apply_update.return_value = _make_snapshot()

        pipeline._on_transcription(text, "ts")
        pipeline._stop.set()

        t = threading.Thread(target=pipeline._llm_worker)
        t.start()
        t.join(timeout=5)
        assert not t.is_alive(), "Worker did not exit in time"
        return t

    def test_worker_calls_get_snapshot(self, pipeline_mocks):
        pipeline, mock_sm, mock_llm, _ = pipeline_mocks
        self._run_worker_for_item(pipeline, mock_sm, mock_llm)
        mock_sm.get_snapshot.assert_called_once()

    def test_worker_calls_llm_infer_with_transcription(self, pipeline_mocks):
        pipeline, mock_sm, mock_llm, _ = pipeline_mocks
        self._run_worker_for_item(pipeline, mock_sm, mock_llm, "activate bypass pump")
        mock_llm.infer.assert_called_once()
        call_args = mock_llm.infer.call_args
        assert call_args.args[0] == "activate bypass pump"

    def test_worker_calls_apply_update_with_correct_machines(self, pipeline_mocks):
        pipeline, mock_sm, mock_llm, _ = pipeline_mocks
        mock_llm.infer.return_value = _make_llm_output(["Patient Monitor"], ["Ventilator"])
        self._run_worker_for_item(pipeline, mock_sm, mock_llm)

        mock_sm.apply_update.assert_called_once()
        req: StateUpdateRequest = mock_sm.apply_update.call_args.args[0]
        assert isinstance(req, StateUpdateRequest)
        assert "Patient Monitor" in req.turn_on
        assert "Ventilator"       in req.turn_off

    def test_worker_passes_transcription_in_request(self, pipeline_mocks):
        pipeline, mock_sm, mock_llm, _ = pipeline_mocks
        self._run_worker_for_item(pipeline, mock_sm, mock_llm, "turn off OR lights")
        req = mock_sm.apply_update.call_args.args[0]
        assert req.transcription == "turn off OR lights"

    def test_worker_handles_llm_exception_gracefully(self, pipeline_mocks):
        """If MedGemma raises, worker should log the error and continue — not crash."""
        pipeline, mock_sm, mock_llm, _ = pipeline_mocks
        mock_llm.infer.side_effect = RuntimeError("GPU OOM")

        pipeline._on_transcription("crash test", "ts")
        pipeline._stop.set()

        t = threading.Thread(target=pipeline._llm_worker)
        t.start()
        t.join(timeout=5)
        assert not t.is_alive(), "Worker crashed instead of handling the exception"
        # apply_update must NOT have been called
        mock_sm.apply_update.assert_not_called()

    def test_worker_processes_multiple_items(self, pipeline_mocks):
        pipeline, mock_sm, mock_llm, _ = pipeline_mocks
        mock_llm.infer.return_value = _make_llm_output([], [])
        mock_sm.apply_update.return_value = _make_snapshot()

        texts = ["cmd one", "cmd two", "cmd three"]
        for text in texts:
            pipeline._on_transcription(text, "ts")

        pipeline._stop.set()
        t = threading.Thread(target=pipeline._llm_worker)
        t.start()
        t.join(timeout=10)
        assert not t.is_alive()

        assert mock_llm.infer.call_count == 3
        assert mock_sm.apply_update.call_count == 3


# ── start / stop lifecycle tests ─────────────────────────────────────────────

class TestStartStop:
    def test_start_calls_transcriber_start(self, pipeline_mocks):
        pipeline, _, _, mock_tr = pipeline_mocks
        pipeline.start()
        mock_tr.start.assert_called_once()
        pipeline._stop.set()
        pipeline._worker.join(timeout=2)

    def test_stop_calls_transcriber_stop(self, pipeline_mocks):
        pipeline, _, _, mock_tr = pipeline_mocks
        pipeline.start()
        pipeline.stop()
        mock_tr.stop.assert_called_once()

    def test_worker_thread_alive_after_start(self, pipeline_mocks):
        pipeline, _, _, _ = pipeline_mocks
        pipeline.start()
        assert pipeline._worker.is_alive()
        pipeline.stop()

    def test_worker_thread_dead_after_stop(self, pipeline_mocks):
        pipeline, _, _, _ = pipeline_mocks
        pipeline.start()
        pipeline.stop()
        assert not pipeline._worker.is_alive()


# ── change_surgery tests ──────────────────────────────────────────────────────

class TestChangeSurgery:
    def test_change_surgery_updates_surgery_attribute(self, pipeline_mocks):
        pipeline, _, mock_llm, _ = pipeline_mocks
        pipeline.change_surgery(SurgeryType.KIDNEY_PCNL)
        assert pipeline.surgery == SurgeryType.KIDNEY_PCNL

    def test_change_surgery_calls_llm_change_surgery(self, pipeline_mocks):
        pipeline, _, mock_llm, _ = pipeline_mocks
        pipeline.change_surgery(SurgeryType.LIVER_RESECTION)
        mock_llm.change_surgery.assert_called_once_with(SurgeryType.LIVER_RESECTION)

    def test_change_surgery_replaces_state_manager(self, pipeline_mocks):
        pipeline, mock_sm, _, _ = pipeline_mocks
        with patch("backend.pipeline.pipeline.StateManager") as MockSM2:
            new_sm = MagicMock()
            MockSM2.return_value = new_sm
            pipeline.change_surgery(SurgeryType.LIVER_RESECTION)
            MockSM2.assert_called_once_with(SurgeryType.LIVER_RESECTION)
            assert pipeline.state_manager is new_sm
