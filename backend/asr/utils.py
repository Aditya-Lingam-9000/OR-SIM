"""
backend/asr/utils.py
Audio preprocessing utilities — converts raw PCM to 128-dim log-mel features
compatible with the MedASR int8 ONNX Conformer model.

Model spec (from ONNX inspection):
  Input  x:    [N, T, 128]   float32   (T = number of mel frames)
  Input  mask: [N, T]        int64     (1 = valid frame, 0 = padding)
  Output logits:     [N, T/4, 512]  float32
  Output logits_len: [N]            int64

Audio spec:
  Sample rate  : 16 000 Hz
  n_mels       : 128
  n_fft        : 512
  win_length   : 400  samples  (25 ms)
  hop_length   : 160  samples  (10 ms)
  fmin / fmax  : 0 / 8000 Hz
  Normalisation: per-sample mean-variance (standard for NeMo Conformer)
"""

import numpy as np
from scipy.signal import get_window
from typing import Tuple

# ── constants ────────────────────────────────────────────────────────────────
SAMPLE_RATE   = 16_000
N_MELS        = 128
N_FFT         = 512
WIN_LENGTH    = 400          # 25 ms
HOP_LENGTH    = 160          # 10 ms
F_MIN         = 0.0
F_MAX         = 8_000.0
LOG_FLOOR     = 1e-10        # avoid log(0)


# ── mel filterbank (built once at import time) ────────────────────────────────
def _hz_to_mel(hz: float) -> float:
    return 2595.0 * np.log10(1.0 + hz / 700.0)


def _mel_to_hz(mel: float) -> float:
    return 700.0 * (10.0 ** (mel / 2595.0) - 1.0)


def _build_mel_filterbank(
    n_fft: int,
    n_mels: int,
    sample_rate: int,
    f_min: float,
    f_max: float,
) -> np.ndarray:
    """Return filterbank matrix of shape [n_mels, n_fft // 2 + 1]."""
    n_freqs = n_fft // 2 + 1
    freq_bins = np.linspace(0, sample_rate / 2, n_freqs)

    mel_min = _hz_to_mel(f_min)
    mel_max = _hz_to_mel(f_max)
    mel_points = np.linspace(mel_min, mel_max, n_mels + 2)
    hz_points = np.array([_mel_to_hz(m) for m in mel_points])

    # Nearest FFT bin for each mel centre
    bin_points = np.floor((n_fft + 1) * hz_points / sample_rate).astype(int)

    fbank = np.zeros((n_mels, n_freqs), dtype=np.float32)
    for m in range(1, n_mels + 1):
        lo, centre, hi = bin_points[m - 1], bin_points[m], bin_points[m + 1]
        for k in range(lo, centre):
            if centre != lo:
                fbank[m - 1, k] = (k - lo) / (centre - lo)
        for k in range(centre, hi):
            if hi != centre:
                fbank[m - 1, k] = (hi - k) / (hi - centre)
    return fbank


_MEL_FILTERBANK: np.ndarray = _build_mel_filterbank(
    N_FFT, N_MELS, SAMPLE_RATE, F_MIN, F_MAX
)
_WINDOW: np.ndarray = get_window("hann", WIN_LENGTH, fftbins=True).astype(np.float32)


# ── main feature extractor ────────────────────────────────────────────────────

def audio_to_melfeatures(
    audio: np.ndarray,
    normalize: bool = True,
) -> np.ndarray:
    """
    Convert 1-D float32 PCM (16 kHz) → log-mel spectrogram.

    Parameters
    ----------
    audio : np.ndarray  shape [num_samples], dtype float32, range [-1, 1]
    normalize : bool    apply per-utterance mean-variance normalization

    Returns
    -------
    features : np.ndarray  shape [T, 128], dtype float32
    """
    audio = audio.astype(np.float32)
    n_samples = len(audio)

    # Pad audio so every sample contributes to at least one frame
    pad_len = max(0, WIN_LENGTH - n_samples)
    if pad_len > 0:
        audio = np.pad(audio, (0, pad_len))

    # Frame the signal
    n_frames = 1 + (len(audio) - WIN_LENGTH) // HOP_LENGTH
    frames = np.stack(
        [audio[i * HOP_LENGTH : i * HOP_LENGTH + WIN_LENGTH] for i in range(n_frames)]
    )                                                        # [T, WIN_LENGTH]

    # Apply window
    frames = frames * _WINDOW[np.newaxis, :]                 # [T, WIN_LENGTH]

    # FFT → power spectrum
    fft_out = np.fft.rfft(frames, n=N_FFT, axis=-1)         # [T, N_FFT//2+1]
    power   = (fft_out.real ** 2 + fft_out.imag ** 2)       # [T, N_FFT//2+1]

    # Apply mel filterbank
    mel_spec = power @ _MEL_FILTERBANK.T                     # [T, N_MELS]

    # Log compression
    log_mel = np.log(np.maximum(mel_spec, LOG_FLOOR))        # [T, 128]

    # Per-utterance mean-variance normalization (NeMo convention)
    if normalize and log_mel.shape[0] > 1:
        mean = log_mel.mean(axis=0, keepdims=True)
        std  = log_mel.std(axis=0, keepdims=True) + 1e-8
        log_mel = (log_mel - mean) / std

    return log_mel.astype(np.float32)                        # [T, 128]


def features_to_model_input(
    features: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Add batch dimension and build the integer mask.

    Returns
    -------
    x    : np.ndarray  shape [1, T, 128]  float32
    mask : np.ndarray  shape [1, T]       int64   (all 1s — no padding)
    """
    x    = features[np.newaxis, :, :]                        # [1, T, 128]
    mask = np.ones((1, features.shape[0]), dtype=np.int64)   # [1, T]
    return x, mask
