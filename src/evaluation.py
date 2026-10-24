"""Evaluation and Comparative Acoustic Analysis Module for VocalSense AI.

Evaluation Methodology & Academic Integrity:
--------------------------------------------
Evaluating voice cloning requires distinguishing between signal-level acoustic
properties (pitch, energy, duration) and latent speaker identity representations:

1. Speaker Embedding Cosine Similarity:
   Calculates the cosine angle between the 512-dimensional x-vector embedding of the
   reference recording and that of the generated synthesis:
       cos_sim = (e_ref · e_gen) / (||e_ref|| * ||e_gen||)
   Values typically range from 0.40 to 0.85 for successful zero-shot voice cloning.
   Higher values indicate stronger vocal timbre and speaker attribute transfer.

2. Acoustic Discrepancies:
   Compares estimated fundamental frequency (F0) and RMS energy. Differences in F0
   are expected because pitch is inherently sentence- and prosody-dependent; a question
   naturally has different pitch contours than a declarative statement.

3. Scientific Disclaimer:
   Neither acoustic metrics nor embedding similarity constitute biometric legal proof
   of human identity. They quantify neural acoustic resemblance.
"""

import os
from typing import Dict, Any, Optional

import torch
import numpy as np
import librosa
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.audio_analysis import (
    analyze_audio,
    TARGET_SAMPLE_RATE,
)
from src.voice_engine import VoiceCloningEngine


def compute_speaker_similarity(
    ref_audio_path: str,
    gen_audio_path: str,
    engine: Optional[VoiceCloningEngine] = None,
) -> float:
    """Compute cosine similarity between reference and generated speaker embeddings.

    Returns:
        Cosine similarity score between -1.0 and 1.0 (typically 0.40 - 0.85 for neural TTS).
    """
    if engine is None:
        engine = VoiceCloningEngine.get_instance()

    ref_emb, _ = engine.extract_speaker_embedding(ref_audio_path)
    gen_emb, _ = engine.extract_speaker_embedding(gen_audio_path)

    # Normalize vectors
    ref_norm = torch.nn.functional.normalize(ref_emb, p=2, dim=-1)
    gen_norm = torch.nn.functional.normalize(gen_emb, p=2, dim=-1)

    cos_sim = torch.sum(ref_norm * gen_norm).item()
    return float(np.clip(cos_sim, -1.0, 1.0))


def compare_recordings(
    ref_audio_path: str,
    gen_audio_path: str,
    engine: Optional[VoiceCloningEngine] = None,
) -> Dict[str, Any]:
    """Perform side-by-side comparative acoustic and neural evaluation.

    Returns a structured dictionary of comparative statistics and explanations.
    """
    ref_stats = analyze_audio(ref_audio_path)
    gen_stats = analyze_audio(gen_audio_path)

    # Compute speaker embedding similarity
    try:
        similarity_score = compute_speaker_similarity(ref_audio_path, gen_audio_path, engine=engine)
    except Exception as e:
        similarity_score = None
        sim_error = str(e)

    # Compute differences
    ref_pitch = ref_stats["mean_pitch_hz"]
    gen_pitch = gen_stats["mean_pitch_hz"]

    pitch_diff_hz = None
    if isinstance(ref_pitch, (int, float)) and isinstance(gen_pitch, (int, float)):
        pitch_diff_hz = round(abs(gen_pitch - ref_pitch), 2)

    energy_ratio = round(gen_stats["mean_rms_energy"] / max(ref_stats["mean_rms_energy"], 1e-6), 2)

    return {
        "speaker_embedding_similarity": round(similarity_score, 4) if similarity_score is not None else "Error",
        "similarity_interpretation": (
            "High resemblance (>0.70)" if similarity_score and similarity_score >= 0.70
            else "Moderate resemblance (0.50 - 0.70)" if similarity_score and similarity_score >= 0.50
            else "Low resemblance (<0.50)" if similarity_score is not None
            else "Calculation unavailable"
        ),
        "reference_pitch_hz": ref_pitch,
        "generated_pitch_hz": gen_pitch,
        "pitch_difference_hz": pitch_diff_hz if pitch_diff_hz is not None else "N/A (unvoiced)",
        "reference_energy_rms": ref_stats["mean_rms_energy"],
        "generated_energy_rms": gen_stats["mean_rms_energy"],
        "energy_ratio_gen_to_ref": energy_ratio,
        "reference_duration_sec": ref_stats["duration_sec"],
        "generated_duration_sec": gen_stats["duration_sec"],
        "reference_centroid_hz": ref_stats["spectral_centroid_hz"],
        "generated_centroid_hz": gen_stats["spectral_centroid_hz"],
        "evaluation_notes": (
            "1. Speaker embedding similarity measures latent acoustic proximity in the 512-dim x-vector space.\n"
            "2. Pitch and energy differences reflect natural linguistic prosody of differing sentences.\n"
            "3. These metrics describe acoustic resemblance, not legal biometric identity verification."
        ),
    }


def plot_comparative_acoustic_report(
    ref_audio_path: str,
    gen_audio_path: str,
    output_image_path: Optional[str] = None,
) -> str:
    """Generate a 4-panel comparative acoustic visualization:
    1. Reference Waveform
    2. Generated Waveform
    3. Reference Mel-Spectrogram
    4. Generated Mel-Spectrogram
    """
    y_ref, _ = librosa.load(ref_audio_path, sr=TARGET_SAMPLE_RATE)
    y_gen, _ = librosa.load(gen_audio_path, sr=TARGET_SAMPLE_RATE)

    t_ref = np.linspace(0, len(y_ref) / TARGET_SAMPLE_RATE, len(y_ref))
    t_gen = np.linspace(0, len(y_gen) / TARGET_SAMPLE_RATE, len(y_gen))

    # Mel spectrograms
    mel_ref = librosa.power_to_db(
        librosa.feature.melspectrogram(y=y_ref, sr=TARGET_SAMPLE_RATE, n_fft=1024, hop_length=256, n_mels=80),
        ref=np.max,
    )
    mel_gen = librosa.power_to_db(
        librosa.feature.melspectrogram(y=y_gen, sr=TARGET_SAMPLE_RATE, n_fft=1024, hop_length=256, n_mels=80),
        ref=np.max,
    )

    fig, axes = plt.subplots(2, 2, figsize=(14, 6), constrained_layout=True)

    # Reference Waveform
    axes[0, 0].plot(t_ref, y_ref, color="#1e40af", linewidth=0.8, alpha=0.85)
    axes[0, 0].set_title("Reference Voice: Waveform", fontsize=11, fontweight="bold")
    axes[0, 0].set_xlabel("Time (s)", fontsize=9)
    axes[0, 0].set_ylabel("Amplitude", fontsize=9)
    axes[0, 0].set_ylim([-1.05, 1.05])
    axes[0, 0].grid(True, linestyle="--", alpha=0.4)

    # Generated Waveform
    axes[0, 1].plot(t_gen, y_gen, color="#059669", linewidth=0.8, alpha=0.85)
    axes[0, 1].set_title("Generated Speech: Waveform", fontsize=11, fontweight="bold")
    axes[0, 1].set_xlabel("Time (s)", fontsize=9)
    axes[0, 1].set_ylabel("Amplitude", fontsize=9)
    axes[0, 1].set_ylim([-1.05, 1.05])
    axes[0, 1].grid(True, linestyle="--", alpha=0.4)

    # Reference Spectrogram
    img0 = librosa.display.specshow(
        mel_ref,
        sr=TARGET_SAMPLE_RATE,
        hop_length=256,
        x_axis="time",
        y_axis="mel",
        ax=axes[1, 0],
        cmap="magma",
    )
    axes[1, 0].set_title("Reference Voice: Mel-Spectrogram", fontsize=11, fontweight="bold")
    axes[1, 0].set_xlabel("Time (s)", fontsize=9)
    axes[1, 0].set_ylabel("Frequency (Hz)", fontsize=9)
    fig.colorbar(img0, ax=axes[1, 0], format="%+2.0f dB", pad=0.02)

    # Generated Spectrogram
    img1 = librosa.display.specshow(
        mel_gen,
        sr=TARGET_SAMPLE_RATE,
        hop_length=256,
        x_axis="time",
        y_axis="mel",
        ax=axes[1, 1],
        cmap="magma",
    )
    axes[1, 1].set_title("Generated Speech: Mel-Spectrogram", fontsize=11, fontweight="bold")
    axes[1, 1].set_xlabel("Time (s)", fontsize=9)
    axes[1, 1].set_ylabel("Frequency (Hz)", fontsize=9)
    fig.colorbar(img1, ax=axes[1, 1], format="%+2.0f dB", pad=0.02)

    if output_image_path is None:
        output_image_path = os.path.join("outputs", "comparative_acoustic_report.png")

    os.makedirs(os.path.dirname(output_image_path), exist_ok=True)
    fig.savefig(output_image_path, dpi=120, bbox_inches="tight")
    plt.close(fig)

    return output_image_path
