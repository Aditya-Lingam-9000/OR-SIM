"""
backend/asr/audio.py
Real-time microphone capture using sounddevice.

Strategy:
  - Capture 16 kHz mono float32 audio continuously in small blocks (20 ms).
  - Accumulate samples into a ring buffer.
  - Every STRIDE_SEC seconds of new audio arriving, extract the last
    WINDOW_SEC of audio and push it to an asyncio/threading queue for inference.
  - This sliding-window approach ensures no speech is lost between chunks.

Buffer sizes (defaults):
  WINDOW_SEC  = 3.0 s  → 48 000 samples per inference call
  STRIDE_SEC  = 0.5 s  → new inference every ~0.5 s of new audio
  BLOCK_SIZE  = 320     → 20 ms blocks fed to sounddevice callback
"""

import threading
import queue
from collections import deque
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
from loguru import logger

from backend.asr.utils import SAMPLE_RATE

# ── defaults ─────────────────────────────────────────────────────────────────
WINDOW_SEC  = 3.0    # seconds of audio per inference window
STRIDE_SEC  = 0.5    # seconds of new audio before triggering inference
BLOCK_SIZE  = 320    # samples per sounddevice callback (20 ms)
SILENCE_RMS = 0.008  # RMS threshold — blocks below this are treated as silence


class AudioCapture:
    """
    Continuously captures microphone audio and emits audio windows for inference.

    Usage
    -----
    def on_audio(chunk: np.ndarray):
        # chunk is shape [~48000], float32, 16 kHz
        text = model.transcribe(chunk)
        print(text)

    cap = AudioCapture(on_audio_callback=on_audio)
    cap.start()
    # ... run your application ...
    cap.stop()
    """

    def __init__(
        self,
        on_audio_callback: Callable[[np.ndarray], None],
        window_sec: float = WINDOW_SEC,
        stride_sec: float = STRIDE_SEC,
        sample_rate: int = SAMPLE_RATE,
        device: Optional[int] = None,
    ):
        self.on_audio    = on_audio_callback
        self.window_sec  = window_sec
        self.stride_sec  = stride_sec
        self.sample_rate = sample_rate
        self.device      = device

        self._window_samples = int(window_sec * sample_rate)
        self._stride_samples = int(stride_sec * sample_rate)

        # Ring buffer: holds up to window_sec of audio
        self._ring: deque = deque(maxlen=self._window_samples)

        # Audio queue: filled by sounddevice callback, consumed by worker thread
        self._audio_queue: queue.Queue = queue.Queue()

        self._new_samples   = 0          # count since last inference trigger
        self._running       = False
        self._worker_thread: Optional[threading.Thread] = None
        self._stream:        Optional[sd.InputStream]   = None

    # ── internal ──────────────────────────────────────────────────────────────

    def _sd_callback(
        self,
        indata: np.ndarray,
        frames: int,
        time,
        status,
    ) -> None:
        """Called by sounddevice in a separate thread for each captured block."""
        if status:
            logger.warning(f"sounddevice status: {status}")
        # indata shape: [frames, channels] — take first channel
        mono = indata[:, 0].copy()
        self._audio_queue.put(mono)

    def _worker(self) -> None:
        """Background thread: drains the audio queue and triggers inference."""
        while self._running:
            try:
                chunk = self._audio_queue.get(timeout=0.05)
            except queue.Empty:
                continue

            # Append to ring buffer
            self._ring.extend(chunk.tolist())
            self._new_samples += len(chunk)

            # Check silence
            rms = float(np.sqrt(np.mean(chunk ** 2)))
            is_silent = rms < SILENCE_RMS

            # Trigger inference when enough new non-silent audio has arrived
            if self._new_samples >= self._stride_samples and not is_silent:
                self._new_samples = 0
                window = np.array(self._ring, dtype=np.float32)
                if len(window) > 0:
                    try:
                        self.on_audio(window)
                    except Exception as exc:
                        logger.error(f"on_audio callback error: {exc}")

    # ── public ────────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start microphone capture and worker thread."""
        if self._running:
            return
        self._running = True

        self._worker_thread = threading.Thread(
            target=self._worker,
            name="asr-worker",
            daemon=True,
        )
        self._worker_thread.start()

        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="float32",
            blocksize=BLOCK_SIZE,
            device=self.device,
            callback=self._sd_callback,
        )
        self._stream.start()
        logger.info(
            f"AudioCapture started — device={self.device}, "
            f"window={self.window_sec}s, stride={self.stride_sec}s, "
            f"sr={self.sample_rate} Hz"
        )

    def stop(self) -> None:
        """Stop capture and clean up threads."""
        self._running = False
        if self._stream is not None:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if self._worker_thread is not None:
            self._worker_thread.join(timeout=2.0)
        logger.info("AudioCapture stopped.")

    def list_devices(self) -> None:
        """Print available input devices to help the user choose."""
        print(sd.query_devices())
