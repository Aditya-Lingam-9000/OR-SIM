"""
backend/asr/audio.py
Real-time microphone capture using sounddevice — VAD endpoint detection.

Strategy (Voice Activity Detection):
  ─────────────────────────────────────────────────────────────────────
  Instead of a sliding window (which causes repeated re-transcription
  and hallucinations), we use utterance-based endpoint detection:

    1. IDLE state    : listening for speech to start
    2. SPEAKING state: RMS rises above SPEECH_RMS_THRESHOLD
                       → accumulate audio samples
    3. SILENCE state : RMS drops below SILENCE_RMS_THRESHOLD
                       → if silence lasts ≥ SILENCE_DURATION_SEC,
                         emit the accumulated utterance for inference
                         and return to IDLE

  A short pre-roll buffer (PRE_ROLL_SEC) is kept so the very beginning
  of each command (which often has a slightly lower RMS) is not clipped.

  This ensures:
    • Each command is transcribed ONCE, not dozens of times
    • No hallucinated repetition from reprocessed audio
    • Clean per-utterance output

  Tunable constants:
    SPEECH_RMS_THRESHOLD  = 0.012  — RMS above which speech is detected
    SILENCE_RMS_THRESHOLD = 0.007  — RMS below which silence is declared
    SILENCE_DURATION_SEC  = 0.75   — how long silence must last to end utterance
    MIN_SPEECH_SEC        = 0.30   — minimum utterance length (filter noise)
    MAX_SPEECH_SEC        = 10.0   — hard cap to avoid infinite accumulation
    PRE_ROLL_SEC          = 0.50   — pre-speech audio kept to avoid clipping
    BLOCK_SIZE            = 320    — 20 ms blocks (16000 × 0.02)
"""

import threading
import queue
from collections import deque
from enum import Enum, auto
from typing import Callable, Optional

import numpy as np
import sounddevice as sd
from loguru import logger

from backend.asr.utils import SAMPLE_RATE

# ── VAD tuning constants ──────────────────────────────────────────────────────
SPEECH_RMS_THRESHOLD  = 0.012   # RMS above this → speech  (lower = catch softer starts)
SILENCE_RMS_THRESHOLD = 0.007   # RMS below this → silence  (hysteresis gap)
SILENCE_DURATION_SEC  = 0.75    # seconds of silence before utterance ends
MIN_SPEECH_SEC        = 0.30    # minimum utterance length to send for inference
MAX_SPEECH_SEC        = 10.0    # hard cap — emit even if still speaking
PRE_ROLL_SEC          = 0.50    # seconds of pre-speech buffer to avoid start clipping
BLOCK_SIZE            = 320     # sounddevice block size: 20 ms at 16 kHz


class _VadState(Enum):
    IDLE     = auto()   # waiting for speech
    SPEAKING = auto()   # accumulating speech
    TRAILING = auto()   # speech ended, counting silence frames


class AudioCapture:
    """
    Continuously captures microphone audio and emits complete utterances
    for inference using Voice Activity Detection (VAD).

    Usage
    -----
    def on_audio(chunk: np.ndarray):
        # chunk is ONE clean utterance, e.g. "turn on the patient monitor"
        text = model.transcribe(chunk)
        print(text)

    cap = AudioCapture(on_audio_callback=on_audio)
    cap.start()
    # ... run ...
    cap.stop()
    """

    def __init__(
        self,
        on_audio_callback: Callable[[np.ndarray], None],
        sample_rate: int = SAMPLE_RATE,
        device: Optional[int] = None,
    ):
        self.on_audio    = on_audio_callback
        self.sample_rate = sample_rate
        self.device      = device

        # Derived frame counts
        self._silence_frames_needed = int(
            SILENCE_DURATION_SEC * sample_rate / BLOCK_SIZE
        )
        self._min_speech_samples = int(MIN_SPEECH_SEC * sample_rate)
        self._max_speech_samples = int(MAX_SPEECH_SEC * sample_rate)
        self._pre_roll_samples   = int(PRE_ROLL_SEC * sample_rate)

        # Pre-roll ring buffer — always holds last PRE_ROLL_SEC of audio
        self._pre_roll: deque = deque(maxlen=self._pre_roll_samples)

        # Utterance accumulation buffer
        self._speech_buf: list = []

        # VAD state
        self._state              = _VadState.IDLE
        self._silence_frame_count = 0

        # sounddevice → worker queue
        self._audio_queue: queue.Queue = queue.Queue()

        self._running        = False
        self._worker_thread: Optional[threading.Thread] = None
        self._stream:        Optional[sd.InputStream]   = None

    # ── internal ──────────────────────────────────────────────────────────────

    def _sd_callback(self, indata: np.ndarray, frames: int, time, status) -> None:
        """Called by sounddevice for every BLOCK_SIZE-sample block."""
        if status:
            logger.warning(f"sounddevice status: {status}")
        self._audio_queue.put(indata[:, 0].copy())

    def _emit_utterance(self) -> None:
        """Assemble pre-roll + speech buffer and send to inference callback."""
        pre   = np.array(list(self._pre_roll), dtype=np.float32)
        utt   = np.array(self._speech_buf, dtype=np.float32)
        audio = np.concatenate([pre, utt]) if len(pre) > 0 else utt

        # Trim to MAX_SPEECH_SEC just in case
        audio = audio[: self._max_speech_samples]

        if len(audio) >= self._min_speech_samples:
            try:
                self.on_audio(audio)
            except Exception as exc:
                logger.error(f"on_audio callback error: {exc}")
        else:
            logger.debug(
                f"Utterance too short ({len(audio)/self.sample_rate:.2f}s), skipped."
            )

    def _worker(self) -> None:
        """Background thread: VAD state machine."""
        while self._running:
            try:
                block = self._audio_queue.get(timeout=0.05)
            except queue.Empty:
                # When in TRAILING state, a long silence in the queue also ends utt
                if self._state == _VadState.TRAILING:
                    self._silence_frame_count += 1
                    if self._silence_frame_count >= self._silence_frames_needed:
                        self._emit_utterance()
                        self._speech_buf = []
                        self._silence_frame_count = 0
                        self._state = _VadState.IDLE
                continue

            rms = float(np.sqrt(np.mean(block ** 2)))

            if self._state == _VadState.IDLE:
                # Always update pre-roll
                self._pre_roll.extend(block.tolist())

                if rms >= SPEECH_RMS_THRESHOLD:
                    # Speech started
                    self._state      = _VadState.SPEAKING
                    self._speech_buf = []
                    self._speech_buf.extend(block.tolist())
                    logger.debug("VAD: speech START")

            elif self._state == _VadState.SPEAKING:
                self._speech_buf.extend(block.tolist())

                # Hard cap check
                if len(self._speech_buf) >= self._max_speech_samples:
                    logger.debug("VAD: hard cap reached, emitting")
                    self._emit_utterance()
                    self._speech_buf          = []
                    self._pre_roll            = deque(maxlen=self._pre_roll_samples)
                    self._silence_frame_count = 0
                    self._state               = _VadState.IDLE
                    continue

                if rms < SILENCE_RMS_THRESHOLD:
                    # Possible end of speech
                    self._state               = _VadState.TRAILING
                    self._silence_frame_count = 1
                    logger.debug("VAD: trailing silence started")

            elif self._state == _VadState.TRAILING:
                self._speech_buf.extend(block.tolist())

                if rms >= SPEECH_RMS_THRESHOLD:
                    # Speech resumed — false alarm, continue accumulating
                    self._state               = _VadState.SPEAKING
                    self._silence_frame_count = 0
                    logger.debug("VAD: speech RESUMED")
                else:
                    self._silence_frame_count += 1
                    if self._silence_frame_count >= self._silence_frames_needed:
                        logger.debug(
                            f"VAD: speech END — {len(self._speech_buf)/self.sample_rate:.2f}s accumulated"
                        )
                        self._emit_utterance()
                        # Reset
                        self._speech_buf          = []
                        self._pre_roll            = deque(maxlen=self._pre_roll_samples)
                        self._silence_frame_count = 0
                        self._state               = _VadState.IDLE

    # ── public ────────────────────────────────────────────────────────────────

    def push_block(self, block: np.ndarray) -> None:
        """
        Feed a raw audio block directly into the VAD queue.

        Use this in server / headless mode (no microphone) when audio arrives
        from an external source e.g. the browser's getUserMedia stream over
        the /ws/audio WebSocket.  The block is re-chunked into BLOCK_SIZE
        pieces so the VAD silence-frame counter stays accurate.

        Parameters
        ----------
        block : 1-D float32 numpy array at SAMPLE_RATE (16 kHz)
        """
        for i in range(0, len(block), BLOCK_SIZE):
            chunk = block[i : i + BLOCK_SIZE]
            if len(chunk) == BLOCK_SIZE:
                self._audio_queue.put(chunk)

    def start(self, use_microphone: bool = True) -> None:
        """Start VAD worker thread, and optionally open the local microphone."""
        if self._running:
            return
        self._running = True

        self._worker_thread = threading.Thread(
            target=self._worker,
            name="asr-vad-worker",
            daemon=True,
        )
        self._worker_thread.start()

        if use_microphone:
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
                f"AudioCapture (VAD) started — device={self.device}, "
                f"speech_thresh={SPEECH_RMS_THRESHOLD}, silence_thresh={SILENCE_RMS_THRESHOLD}, "
                f"silence_dur={SILENCE_DURATION_SEC}s, pre_roll={PRE_ROLL_SEC}s, "
                f"sr={self.sample_rate} Hz"
            )
        else:
            logger.info(
                "AudioCapture (VAD) started in server mode — "
                "waiting for audio via push_block() (no local microphone used)"
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
        """Print available input devices."""
        print(sd.query_devices())
