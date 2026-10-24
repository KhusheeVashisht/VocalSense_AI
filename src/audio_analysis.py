"""Acoustic Analysis and Audio Validation Module for VocalSense AI.

Acoustic Integrity & Scientific Limitations:
--------------------------------------------
Acoustic measurements (such as fundamental frequency F0, RMS energy, and spectral
centroid) characterize signal-level physical properties of an acoustic recording.
They DO NOT independently establish or verify speaker biometric identity. Similar
pitch or energy can occur across completely distinct speakers, while the same
speaker's pitch varies naturally across pitch register, prosody, emotion, and recording
equipment. Speaker identity conditioning is handled separately by high-dimensional
neural speaker embedding vectors.
"""

import os
import numpy as np
import soundfile as sf
import librosa
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend suitable for web servers
import matplotlib.pyplot as plt
from typing import Tuple, Dict, Any, Optional


SUPPORTED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac", ".m4a"}
TARGET_SAMPLE_RATE = 16000


def validate_and_preprocess_audio(
    file_path: str,
    output_dir: str = "outputs",
    min_duration: float = 0.5,
    max_duration: float = 60.0,
    target_sr: int = TARGET_SAMPLE_RATE,
) -> Tuple[bool, str, Dict[str, Any]]:
    """Validate an uploaded audio file and preprocess it for neural voice cloning.

    Checks format, readability, duration, and silence. Converts stereo to mono
    and resamples to 16 kHz WAV format required by SpeechT5 and SpeechBrain.

    Returns:
        (is_valid, processed_file_path_or_error_msg, metadata_dict)
    """
    if not file_path or not os.path.exists(file_path):
        return False, "Audio file does not exist or was not received.", {}

    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_AUDIO_EXTENSIONS:
        return (
            False,
            f"Unsupported file format '{ext}'. Supported formats: {', '.join(sorted(SUPPORTED_AUDIO_EXTENSIONS))}.",
            {},
        )

    try:
        # Load audio using librosa (handles various formats, converts to float32)
        y, orig_sr = librosa.load(file_path, sr=None, mono=False)
    except Exception as e:
        return False, f"Failed to read audio file. File may be corrupted. Error: {str(e)}", {}

    # Check channels and convert to mono if stereo
    if y.ndim > 1:
        channels = y.shape[0]
        y_mono = librosa.to_mono(y)
    else:
        channels = 1
        y_mono = y

    # Resample if necessary
    if orig_sr != target_sr:
        y_resampled = librosa.resample(y_mono, orig_sr=orig_sr, target_sr=target_sr)
    else:
        y_resampled = y_mono

    duration = len(y_resampled) / target_sr

    if duration < min_duration:
        return (
            False,
            f"Voice recording is too short ({duration:.2f}s). Minimum required duration is {min_duration:.1f} seconds to capture vocal characteristics.",
            {},
        )

    if duration > max_duration:
        return (
            False,
            f"Voice recording is too long ({duration:.1f}s). Maximum allowed duration is {max_duration:.0f} seconds.",
            {},
        )

    # Check for empty/silent recording
    rms = float(np.sqrt(np.mean(y_resampled**2)))
    if rms < 1e-4:
        return (
            False,
            "Audio recording is almost completely silent. Please provide a clear voice sample with audible speech.",
            {},
        )

    # Normalize audio amplitude to [-0.95, 0.95]
    peak = np.max(np.abs(y_resampled))
    if peak > 0:
        y_norm = (y_resampled / peak) * 0.95
    else:
        y_norm = y_resampled

    os.makedirs(output_dir, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    processed_path = os.path.join(output_dir, f"prep_{base_name}.wav")
    sf.write(processed_path, y_norm, samplerate=target_sr, subtype="PCM_16")

    metadata = {
        "original_sample_rate": orig_sr,
        "processed_sample_rate": target_sr,
        "original_channels": channels,
        "duration_seconds": round(duration, 2),
        "total_samples": len(y_norm),
        "rms_energy": round(rms, 4),
        "peak_amplitude": round(float(peak), 4),
        "processed_path": processed_path,
    }

    return True, processed_path, metadata


def compute_pitch_f0(y: np.ndarray, sr: int) -> Tuple[float, float, float, np.ndarray]:
    """Estimate fundamental frequency (F0/pitch) using pYIN with robust fallback.

    Returns:
        (mean_f0, min_f0, max_f0, f0_contour)
    """
    try:
        # Standard human vocal fundamental frequency range (~65 Hz C2 to ~1046 Hz C6)
        fmin = librosa.note_to_hz("C2")
        fmax = librosa.note_to_hz("C6")
        f0, voiced_flag, _ = librosa.pyin(y, fmin=fmin, fmax=fmax, sr=sr, frame_length=1024)
        voiced_f0 = f0[~np.isnan(f0)]

        if len(voiced_f0) > 0:
            return (
                float(np.mean(voiced_f0)),
                float(np.min(voiced_f0)),
                float(np.max(voiced_f0)),
                f0,
            )
    except Exception:
        pass

    # Fallback: estimate using autocorrelation on short voiced segment
    try:
        autocorr = np.correlate(y, y, mode="full")
        autocorr = autocorr[len(autocorr) // 2 :]
        d = np.diff(autocorr)
        start = np.where(d > 0)[0]
        if len(start) > 0:
            peak = np.argmax(autocorr[start[0] :]) + start[0]
            if peak > 0:
                est_f0 = sr / peak
                if 50.0 <= est_f0 <= 800.0:
                    return float(est_f0), float(est_f0), float(est_f0), np.array([est_f0])
    except Exception:
        pass

    # When pitch detection is impossible (unvoiced or whisper)
    return 0.0, 0.0, 0.0, np.array([])


def analyze_audio(file_path: str) -> Dict[str, Any]:
    """Perform comprehensive acoustic analysis on an audio recording.

    Calculates duration, sample rate, F0 (pitch), RMS energy, spectral centroid,
    and zero-crossing rate.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file '{file_path}' does not exist.")

    y, sr = librosa.load(file_path, sr=None)
    duration = float(len(y) / sr)

    # Fundamental frequency (pitch)
    mean_pitch, min_pitch, max_pitch, _ = compute_pitch_f0(y, sr)

    # RMS Energy
    rms_frames = librosa.feature.rms(y=y)[0]
    mean_rms = float(np.mean(rms_frames))
    max_rms = float(np.max(rms_frames))

    # Spectral Centroid (perceived acoustic brightness)
    centroid_frames = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
    mean_centroid = float(np.mean(centroid_frames))

    # Zero Crossing Rate (noise / noisiness / sibilance indicator)
    zcr_frames = librosa.feature.zero_crossing_rate(y=y)[0]
    mean_zcr = float(np.mean(zcr_frames))

    return {
        "file_name": os.path.basename(file_path),
        "duration_sec": round(duration, 2),
        "sample_rate": sr,
        "mean_pitch_hz": round(mean_pitch, 2) if mean_pitch > 0 else "Unvoiced / Undetected",
        "min_pitch_hz": round(min_pitch, 2) if min_pitch > 0 else "N/A",
        "max_pitch_hz": round(max_pitch, 2) if max_pitch > 0 else "N/A",
        "mean_rms_energy": round(mean_rms, 4),
        "max_rms_energy": round(max_rms, 4),
        "spectral_centroid_hz": round(mean_centroid, 2),
        "zero_crossing_rate": round(mean_zcr, 4),
        "scientific_note": "Acoustic measurements describe physical recording properties. Pitch and energy vary naturally across sentences and emotions; they do not uniquely establish speaker identity.",
    }


def generate_visual_acoustic_report(
    audio_path: str,
    title_prefix: str = "Audio",
    output_image_path: Optional[str] = None,
) -> str:
    """Generate waveform and mel-spectrogram visualization for an audio recording.

    Returns the path to the saved visualization image file.
    """
    y, sr = librosa.load(audio_path, sr=TARGET_SAMPLE_RATE)
    duration = len(y) / sr
    time_axis = np.linspace(0, duration, len(y))

    # Compute mel-spectrogram
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr, n_fft=1024, hop_length=256, n_mels=80)
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)

    fig, axes = plt.subplots(2, 1, figsize=(10, 5), constrained_layout=True)

    # 1. Waveform plot
    axes[0].plot(time_axis, y, color="#2563eb", linewidth=0.8, alpha=0.9)
    axes[0].set_title(f"{title_prefix}: Waveform (Time Domain)", fontsize=11, fontweight="bold")
    axes[0].set_xlabel("Time (seconds)", fontsize=9)
    axes[0].set_ylabel("Amplitude", fontsize=9)
    axes[0].set_xlim([0, duration])
    axes[0].set_ylim([-1.05, 1.05])
    axes[0].grid(True, linestyle="--", alpha=0.5)

    # 2. Spectrogram plot
    img = librosa.display.specshow(
        mel_spec_db,
        sr=sr,
        hop_length=256,
        x_axis="time",
        y_axis="mel",
        ax=axes[1],
        cmap="magma",
    )
    axes[1].set_title(f"{title_prefix}: Mel-Spectrogram (Frequency Domain)", fontsize=11, fontweight="bold")
    axes[1].set_xlabel("Time (seconds)", fontsize=9)
    axes[1].set_ylabel("Frequency (Hz)", fontsize=9)
    fig.colorbar(img, ax=axes[1], format="%+2.0f dB", pad=0.02)

    if output_image_path is None:
        base_name = os.path.splitext(os.path.basename(audio_path))[0]
        output_image_path = os.path.join("outputs", f"plot_{base_name}.png")

    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    fig.savefig(output_image_path, dpi=120, bbox_inches="tight")
    plt.close(fig)

    return output_image_path
