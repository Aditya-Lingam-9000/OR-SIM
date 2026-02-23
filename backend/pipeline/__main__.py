"""
backend/pipeline/__main__.py
CLI entry point for the OR end-to-end pipeline.

Run:
    python -m backend.pipeline --surgery heart
    python -m backend.pipeline --surgery liver --cpu
    python -m backend.pipeline --surgery kidney --list-devices

Surgery choices      : heart | liver | kidney
Device selection     : pass --device <index> (see --list-devices)
GPU / CPU control    : default=GPU (-1 layers), use --cpu to force CPU
"""

import argparse
import signal
import sys
import threading

from loguru import logger

from backend.data.surgeries import SurgeryType
from backend.pipeline.pipeline import ORPipeline


# ── pretty logging ────────────────────────────────────────────────────────────
logger.remove()
logger.add(
    sys.stderr,
    format="<green>{time:HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | {message}",
    level="INFO",
)


# ── surgery name → enum ───────────────────────────────────────────────────────
_SURGERY_MAP = {
    "heart":  SurgeryType.HEART_TRANSPLANT,
    "liver":  SurgeryType.LIVER_RESECTION,
    "kidney": SurgeryType.KIDNEY_PCNL,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        prog        = "python -m backend.pipeline",
        description = "OR-SIM end-to-end pipeline: Mic → MedASR → MedGemma → machine_states.json",
    )
    parser.add_argument(
        "--surgery",
        choices = list(_SURGERY_MAP.keys()),
        default = "heart",
        help    = "Active surgery type (default: heart)",
    )
    parser.add_argument(
        "--cpu",
        action  = "store_true",
        help    = "Force CPU-only inference (n_gpu_layers=0). Slow but works without GPU.",
    )
    parser.add_argument(
        "--list-devices",
        action  = "store_true",
        help    = "Print available microphone input devices and exit.",
    )
    parser.add_argument(
        "--device",
        type    = int,
        default = None,
        help    = "Microphone device index (from --list-devices). Default: system default.",
    )
    args = parser.parse_args()

    # ── list devices mode ─────────────────────────────────────────────────────
    if args.list_devices:
        from backend.asr.audio import AudioCapture
        AudioCapture.list_input_devices()
        return

    surgery      = _SURGERY_MAP[args.surgery]
    n_gpu_layers = 0 if args.cpu else -1

    logger.info(f"Surgery      : {surgery.value}")
    logger.info(f"GPU layers   : {'CPU only' if n_gpu_layers == 0 else 'all (GPU)'}")

    # ── build pipeline ────────────────────────────────────────────────────────
    pipeline = ORPipeline(
        surgery      = surgery,
        n_gpu_layers = n_gpu_layers,
    )

    # Override mic device if requested
    if args.device is not None:
        pipeline.transcriber._capture.device = args.device
        logger.info(f"Microphone   : device index {args.device}")

    # ── graceful shutdown on Ctrl+C ───────────────────────────────────────────
    _stop_event = threading.Event()

    def _signal_handler(sig, frame):
        print("\n\nShutting down pipeline…")
        _stop_event.set()

    signal.signal(signal.SIGINT, _signal_handler)

    pipeline.start()

    # Block main thread until Ctrl+C
    _stop_event.wait()
    pipeline.stop()

    logger.info("Pipeline exited cleanly.")


if __name__ == "__main__":
    main()
