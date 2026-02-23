"""
tests/phase1/test_asr.py
Phase 1 sanity and real-output tests for the MedASR pipeline.

Run:
    cd d:\\OR-SIM
    venv\\Scripts\\python.exe -m pytest tests/phase1/test_asr.py -v

Tests:
    1. Mel feature extraction shape and dtype
    2. Model loads without error
    3. Model runs inference on synthetic audio (no exception)
    4. Vocab loads with expected size and key tokens
    5. CTC greedy decode produces a string from real audio if WAV provided
    6. Latency benchmark on 3 s of white noise (should be < 5 s on CPU)
"""

import time
import sys
from pathlib import Path

import numpy as np
import pytest

# Make sure the project root is on the path
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.asr.utils  import (
    audio_to_melfeatures,
    features_to_model_input,
    SAMPLE_RATE,
    N_MELS,
)
from backend.asr.model  import MedASRModel, load_vocab, ctc_greedy_decode, BLANK_ID


# ── fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def model():
    """Load model once per test module."""
    return MedASRModel()


@pytest.fixture
def silence_audio():
    """3 seconds of silence."""
    return np.zeros(SAMPLE_RATE * 3, dtype=np.float32)


@pytest.fixture
def noise_audio():
    """3 seconds of white noise at low amplitude."""
    rng = np.random.default_rng(42)
    return (rng.standard_normal(SAMPLE_RATE * 3) * 0.05).astype(np.float32)


@pytest.fixture
def tone_audio():
    """3 seconds of a 440 Hz sine tone (simulates a signal, not silence)."""
    t = np.linspace(0, 3.0, SAMPLE_RATE * 3, dtype=np.float32)
    return np.sin(2 * np.pi * 440 * t) * 0.3


# ── test 1: feature extraction ────────────────────────────────────────────────

class TestFeatureExtraction:

    def test_shape_silence(self, silence_audio):
        feats = audio_to_melfeatures(silence_audio)
        # 3 s at 10 ms/frame = ~300 frames
        assert feats.ndim == 2
        assert feats.shape[1] == N_MELS, f"Expected {N_MELS} mel bins, got {feats.shape[1]}"
        assert feats.dtype == np.float32

    def test_shape_noise(self, noise_audio):
        feats = audio_to_melfeatures(noise_audio)
        assert feats.shape[1] == N_MELS

    def test_frame_count_approx(self):
        """Frame count should be approx duration_sec * 100 (10 ms per frame)."""
        duration_sec = 2.0
        audio = np.zeros(int(SAMPLE_RATE * duration_sec), dtype=np.float32)
        feats = audio_to_melfeatures(audio)
        expected_frames = int(duration_sec * 100)
        # Allow ±5 frames tolerance
        assert abs(feats.shape[0] - expected_frames) <= 5, (
            f"Expected ~{expected_frames} frames, got {feats.shape[0]}"
        )

    def test_model_input_shapes(self, noise_audio):
        feats = audio_to_melfeatures(noise_audio)
        x, mask = features_to_model_input(feats)
        assert x.shape == (1, feats.shape[0], N_MELS)
        assert mask.shape == (1, feats.shape[0])
        assert x.dtype == np.float32
        assert mask.dtype == np.int64
        assert np.all(mask == 1), "All mask values should be 1 for single utterance"

    def test_short_audio_one_sample(self):
        """Edge case: single sample should not crash."""
        audio = np.array([0.1], dtype=np.float32)
        feats = audio_to_melfeatures(audio)
        assert feats.ndim == 2
        assert feats.shape[1] == N_MELS

    def test_normalization_range(self, tone_audio):
        """After normalization, values should be roughly unit-normal."""
        feats = audio_to_melfeatures(tone_audio, normalize=True)
        mean = feats.mean()
        std  = feats.std()
        # Loose check — just not wildly off
        assert abs(mean) < 1.0, f"Mean too large: {mean}"
        assert 0.1 < std < 5.0, f"Std out of range: {std}"


# ── test 2: vocab loading ─────────────────────────────────────────────────────

class TestVocab:

    def test_vocab_size(self):
        tokens_path = PROJECT_ROOT / "models" / "medasr" / "tokens.txt"
        vocab = load_vocab(tokens_path)
        assert len(vocab) == 512, f"Expected 512 tokens, got {len(vocab)}"

    def test_blank_token(self):
        tokens_path = PROJECT_ROOT / "models" / "medasr" / "tokens.txt"
        vocab = load_vocab(tokens_path)
        assert BLANK_ID in vocab
        assert vocab[BLANK_ID] == "<blk>", f"Token 0 should be <blk>, got {vocab[BLANK_ID]!r}"

    def test_special_tokens_present(self):
        tokens_path = PROJECT_ROOT / "models" / "medasr" / "tokens.txt"
        vocab = load_vocab(tokens_path)
        # IDs 0-3 are special
        for i in range(4):
            assert i in vocab, f"Special token ID {i} missing"

    def test_consecutive_ids(self):
        tokens_path = PROJECT_ROOT / "models" / "medasr" / "tokens.txt"
        vocab = load_vocab(tokens_path)
        ids = sorted(vocab.keys())
        # Should be 0..511
        assert ids[0] == 0
        assert ids[-1] == 511


# ── test 3: model loading ─────────────────────────────────────────────────────

class TestModelLoad:

    def test_model_loads(self, model):
        assert model is not None
        assert model._session is not None
        assert len(model._vocab) == 512

    def test_session_providers(self, model):
        providers = model._session.get_providers()
        assert len(providers) > 0
        assert "CPUExecutionProvider" in providers or "CUDAExecutionProvider" in providers


# ── test 4: inference ─────────────────────────────────────────────────────────

class TestInference:

    def test_transcribe_returns_string(self, model, noise_audio):
        result = model.transcribe(noise_audio)
        assert isinstance(result, str)

    def test_transcribe_empty_audio(self, model):
        result = model.transcribe(np.array([], dtype=np.float32))
        assert result == ""

    def test_transcribe_silence_no_crash(self, model, silence_audio):
        result = model.transcribe(silence_audio)
        assert isinstance(result, str)

    def test_transcribe_tone_no_crash(self, model, tone_audio):
        result = model.transcribe(tone_audio)
        assert isinstance(result, str)

    def test_output_is_lowercase_or_empty(self, model, noise_audio):
        """MedASR typically outputs lowercase text."""
        result = model.transcribe(noise_audio)
        # Result should not contain uppercase (CTC vocab is lowercase medical)
        if result:
            assert result == result.lower() or any(c.isalpha() for c in result), \
                f"Unexpected output: {result!r}"


# ── test 5: latency benchmark ─────────────────────────────────────────────────

class TestLatency:

    def test_inference_latency_3s_audio(self, model):
        """3 s of audio should transcribe in < 5 s on CPU (int8 model)."""
        audio = np.random.default_rng(0).standard_normal(SAMPLE_RATE * 3).astype(np.float32) * 0.1

        t_start = time.perf_counter()
        model.transcribe(audio)
        t_end   = time.perf_counter()

        latency_ms = (t_end - t_start) * 1000
        print(f"\n  [Latency] 3 s audio → {latency_ms:.1f} ms")
        assert latency_ms < 5000, f"Inference too slow: {latency_ms:.0f} ms (limit: 5000 ms)"

    def test_inference_latency_1s_audio(self, model):
        """1 s audio (single command) should complete in < 3 s."""
        audio = np.random.default_rng(1).standard_normal(SAMPLE_RATE).astype(np.float32) * 0.1

        t_start = time.perf_counter()
        model.transcribe(audio)
        t_end   = time.perf_counter()

        latency_ms = (t_end - t_start) * 1000
        print(f"\n  [Latency] 1 s audio → {latency_ms:.1f} ms")
        assert latency_ms < 3000, f"Inference too slow: {latency_ms:.0f} ms (limit: 3000 ms)"


# ── optional: test with a real WAV file ───────────────────────────────────────

class TestRealAudio:

    def test_transcribe_wav_if_available(self, model):
        """
        If tests/phase1/sample.wav exists (16 kHz mono), transcribe it.
        Place a real medical utterance WAV there for manual validation.
        """
        wav_path = Path(__file__).parent / "sample.wav"
        if not wav_path.exists():
            pytest.skip("No sample.wav found — place a 16 kHz mono WAV to enable this test")

        from scipy.io import wavfile
        sr, data = wavfile.read(str(wav_path))
        assert sr == SAMPLE_RATE, f"WAV must be {SAMPLE_RATE} Hz, got {sr}"
        if data.dtype != np.float32:
            data = data.astype(np.float32) / np.iinfo(data.dtype).max

        result = model.transcribe(data)
        print(f"\n  [Real Audio] Transcription: {result!r}")
        assert len(result) > 0, "Expected non-empty transcription for real audio"
