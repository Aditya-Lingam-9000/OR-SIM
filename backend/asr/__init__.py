"""
backend/asr
MedASR real-time transcription package.

Quick start:
    from backend.asr import LiveTranscriber
    t = LiveTranscriber(on_transcription=my_callback)
    t.start()
"""

from backend.asr.model       import MedASRModel
from backend.asr.audio       import AudioCapture
from backend.asr.transcriber import LiveTranscriber

__all__ = ["MedASRModel", "AudioCapture", "LiveTranscriber"]
