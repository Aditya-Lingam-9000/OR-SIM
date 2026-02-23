"""
backend/asr/transcriber.py
Live transcription entry point — ties AudioCapture + MedASRModel together.

Run:
    python -m backend.asr.transcriber

Controls:
    Ctrl+C to stop.

Output format:
    [HH:MM:SS.mmm] <transcribed text>
"""

import sys
import time
import signal
import threading
from datetime import datetime
from pathlib import Path

import numpy as np
import numpy as np
from loguru import logger

from backend.asr.model  import MedASRModel
from backend.asr.audio  import AudioCapture


# ── logging config ────────────────────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {message}",
    level="INFO",
)
logger.add(
    Path(__file__).parent.parent.parent / "logs" / "asr.log",
    rotation="10 MB",
    level="DEBUG",
    encoding="utf-8",
)

# ── globals ───────────────────────────────────────────────────────────────────
_stop_event = threading.Event()

# Keep track of latency
_last_audio_end_time: float = 0.0


class LiveTranscriber:
    """
    Connects AudioCapture → MedASRModel and prints timestamped transcriptions.

    Parameters
    ----------
    on_transcription : optional callback(text: str, timestamp: str)
        If provided, called after each inference in addition to console output.
        Used by the pipeline (Phase 4+) to feed text to MedGemma.
    """

    def __init__(self, on_transcription=None):
        logger.info("Initialising MedASR model…")
        self.model = MedASRModel()
        self.on_transcription = on_transcription
        self._capture: AudioCapture = AudioCapture(
            on_audio_callback=self._process_chunk,
        )

    def _process_chunk(self, audio: np.ndarray) -> None:
        """Called by AudioCapture once per complete spoken utterance (VAD endpoint)."""
        t_start = time.perf_counter()

        text = self.model.transcribe(audio)

        t_end   = time.perf_counter()
        latency = (t_end - t_start) * 1000   # ms
        dur_s   = len(audio) / 16_000        # utterance duration in seconds

        if not text:
            return   # silence / noise — nothing to show

        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"[{timestamp}]  {text}   ({latency:.0f} ms | {dur_s:.1f}s audio)")

        if self.on_transcription is not None:
            try:
                self.on_transcription(text, timestamp)
            except Exception as exc:
                logger.error(f"on_transcription callback error: {exc}")

    def start(self, use_microphone: bool = True) -> None:
        self._capture.start(use_microphone=use_microphone)
        if use_microphone:
            logger.info("🎙  Listening… Speak your surgery commands. Press Ctrl+C to stop.")
        else:
            logger.info("LiveTranscriber ready — server mode (browser mic via /ws/audio).")

    def push_audio(self, block: np.ndarray) -> None:
        """
        Feed a raw float32 PCM block (16 kHz) into the VAD pipeline.
        Called from the /ws/audio WebSocket handler for each chunk received
        from the browser's microphone.
        """
        self._capture.push_block(block)

    def stop(self) -> None:
        self._capture.stop()
        logger.info("LiveTranscriber stopped.")

    def list_devices(self) -> None:
        self._capture.list_devices()


# ── standalone entry point ────────────────────────────────────────────────────

def main():
    import argparse

    parser = argparse.ArgumentParser(description="MedASR Live Transcriber")
    parser.add_argument(
        "--list-devices",
        action="store_true",
        help="List available audio input devices and exit.",
    )
    parser.add_argument(
        "--device",
        type=int,
        default=None,
        help="Input device index (from --list-devices). Default: system default.",
    )
    args = parser.parse_args()

    transcriber = LiveTranscriber()

    if args.list_devices:
        transcriber.list_devices()
        return

    if args.device is not None:
        transcriber._capture.device = args.device

    transcriber.start()

    def _signal_handler(sig, frame):
        print("\n\nStopping…")
        _stop_event.set()

    signal.signal(signal.SIGINT, _signal_handler)

    # Block until Ctrl+C
    _stop_event.wait()
    transcriber.stop()


if __name__ == "__main__":
    main()
