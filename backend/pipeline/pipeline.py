"""
backend/pipeline/pipeline.py
ORPipeline — end-to-end: Mic → MedASR → MedGemma → machine_states.json

Architecture
------------
  AudioCapture (sounddevice thread)
       │  VAD-segmented PCM utterance
       ▼
  MedASRModel (ONNX CPU)   ─── callback ──▶  _queue  (thread-safe)
                                                │
                                          LLM worker thread
                                                │
                                       MedGemmaModel.infer()
                                                │
                                       StateManager.apply_update()
                                                │
                                       output/machine_states.json  (atomic write)

Threading model
---------------
  * AudioCapture runs its own background thread (sounddevice callback).
  * MedASR inference runs synchronously inside that callback (~50 ms on CPU).
  * _on_transcription() enqueues the result immediately — never blocks audio.
  * A single LLM worker thread drains the queue serially.
    MedGemma is NOT thread-safe (single llama.cpp context), so one worker is correct.
  * StateManager is thread-safe internally (uses a Lock).
"""

from __future__ import annotations

import queue
import threading
from pathlib import Path
from typing import Optional

from loguru import logger

from backend.data.surgeries    import SurgeryType
from backend.data.models       import StateUpdateRequest
from backend.data.state_manager import StateManager
from backend.llm.medgemma      import MedGemmaModel
from backend.asr.transcriber   import LiveTranscriber


class ORPipeline:
    """
    End-to-end OR pipeline.

    Parameters
    ----------
    surgery        : SurgeryType          Which surgery is active.
    model_path     : Path | None          Path to .gguf file (default: auto-detect).
    n_gpu_layers   : int                  -1 = all GPU, 0 = CPU only.
    llm_queue_size : int                  Max pending transcriptions before dropping oldest.

    Usage
    -----
    pipeline = ORPipeline(SurgeryType.HEART_TRANSPLANT)
    pipeline.start()   # blocks until Ctrl+C or pipeline.stop() called elsewhere
    """

    def __init__(
        self,
        surgery:        SurgeryType,
        model_path:     Optional[Path] = None,
        n_gpu_layers:   int            = -1,
        llm_queue_size: int            = 8,
    ):
        self.surgery = surgery

        # ── data layer ────────────────────────────────────────────────────────
        self.state_manager = StateManager(surgery)

        # ── LLM ───────────────────────────────────────────────────────────────
        self.llm = MedGemmaModel(
            surgery      = surgery,
            model_path   = model_path,
            n_gpu_layers = n_gpu_layers,
        )

        # ── ASR ───────────────────────────────────────────────────────────────
        self.transcriber = LiveTranscriber(
            on_transcription=self._on_transcription,
        )

        # ── internal state ────────────────────────────────────────────────────
        self._queue: queue.Queue[tuple[str, str]] = queue.Queue(maxsize=llm_queue_size)
        self._stop  = threading.Event()
        self._worker = threading.Thread(
            target = self._llm_worker,
            name   = "llm-worker",
            daemon = True,
        )

        logger.info(
            f"ORPipeline ready — surgery={surgery.value}, "
            f"n_gpu_layers={n_gpu_layers}"
        )

    # ── public API ────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start the LLM worker thread and the ASR capture loop."""
        logger.info("ORPipeline starting…")
        self._worker.start()
        self.transcriber.start()
        logger.info("ORPipeline running — speak surgery commands. Ctrl+C to stop.")

    def stop(self) -> None:
        """
        Gracefully stop the pipeline.
        Waits for the LLM worker to finish its current inference (up to 60 s).
        """
        logger.info("ORPipeline stopping…")
        self.transcriber.stop()      # stop audio capture first
        self._stop.set()             # signal worker to exit after current job
        self._worker.join(timeout=60)
        if self._worker.is_alive():
            logger.warning("LLM worker did not stop in 60 s — forcibly abandoned.")
        logger.info("ORPipeline stopped.")

    def change_surgery(self, surgery: SurgeryType) -> None:
        """
        Hot-switch surgery mid-session without reloading the model.
        Resets all machine states to OFF for the new surgery.
        """
        self.surgery = surgery
        self.state_manager = StateManager(surgery)
        self.llm.change_surgery(surgery)
        logger.info(f"ORPipeline surgery changed to: {surgery.value}")

    # ── ASR callback (audio thread) ───────────────────────────────────────────

    def _on_transcription(self, text: str, timestamp: str) -> None:
        """
        Called from the MedASR audio thread after each full utterance.
        Must return immediately — never block here.
        """
        try:
            self._queue.put_nowait((text, timestamp))
            logger.debug(f"[{timestamp}] Queued: {text!r}  (queue depth: {self._queue.qsize()})")
        except queue.Full:
            # Drop the oldest item and enqueue the new one
            try:
                dropped_text, dropped_ts = self._queue.get_nowait()
                logger.warning(
                    f"LLM queue full — dropped [{dropped_ts}] {dropped_text!r}"
                )
                self._queue.put_nowait((text, timestamp))
            except queue.Empty:
                pass   # race condition, not a problem

    # ── LLM worker thread ─────────────────────────────────────────────────────

    def _llm_worker(self) -> None:
        """
        Single background thread: drain _queue → infer → update state.
        Runs until _stop is set AND the queue is empty.
        """
        logger.info("LLM worker started.")

        while not (self._stop.is_set() and self._queue.empty()):
            try:
                text, timestamp = self._queue.get(timeout=0.5)
            except queue.Empty:
                continue

            logger.info(f"LLM ← [{timestamp}] {text!r}")

            try:
                snapshot   = self.state_manager.get_snapshot()
                llm_output = self.llm.infer(text, snapshot)

                req = StateUpdateRequest(
                    **llm_output.to_state_update_kwargs(),
                    transcription = text,
                )
                snap = self.state_manager.apply_update(req)

                logger.info(
                    f"LLM → ON={snap.machine_states['1']}  "
                    f"OFF={snap.machine_states['0']}"
                )

            except Exception as exc:
                logger.error(f"LLM worker error on {text!r}: {exc}", exc_info=True)

            finally:
                self._queue.task_done()

        logger.info("LLM worker exited.")
