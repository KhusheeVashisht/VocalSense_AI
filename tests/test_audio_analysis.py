"""Unit tests for audio validation and acoustic analysis."""
import os
import pytest
import numpy as np
import soundfile as sf
from src.audio_analysis import (
    validate_and_preprocess_audio,
    compute_pitch_f0,
    analyze_audio,
    generate_visual_acoustic_report,
    TARGET_SAMPLE_RATE,
)


@pytest.fixture
def sine_audio(tmp_path):
    """Fixture providing a known 220 Hz sine wave audio file (A3 note)."""
    duration = 2.0
    sr = 16000
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    # 220 Hz fundamental
    audio = 0.8 * np.sin(2 * np.pi * 220.0 * t).astype(np.float32)
    path = os.path.join(tmp_path, "sine_220.wav")
    sf.write(path, audio, sr)
    return path


@pytest.fixture
def silent_audio(tmp_path):
    """Fixture providing a silent audio file."""
    duration = 2.0
    sr = 16000
    audio = np.zeros(int(sr * duration), dtype=np.float32)
    path = os.path.join(tmp_path, "silent.wav")
    sf.write(path, audio, sr)
    return path


def test_audio_validation_valid_file(sine_audio):
    is_valid, proc_path, meta = validate_and_preprocess_audio(sine_audio)
    assert is_valid
    assert os.path.exists(proc_path)
    assert meta["processed_sample_rate"] == TARGET_SAMPLE_RATE
    assert meta["duration_seconds"] > 1.9


def test_audio_validation_silent_file(silent_audio):
    is_valid, msg, _ = validate_and_preprocess_audio(silent_audio)
    assert not is_valid
    assert "silent" in msg.lower()


def test_audio_validation_nonexistent_file():
    is_valid, msg, _ = validate_and_preprocess_audio("nonexistent_audio_path_xyz.wav")
    assert not is_valid
    assert "not exist" in msg.lower()


def test_audio_validation_unsupported_extension(tmp_path):
    bad_file = os.path.join(tmp_path, "test.txt")
    with open(bad_file, "w") as f:
        f.write("not an audio file")
    is_valid, msg, _ = validate_and_preprocess_audio(bad_file)
    assert not is_valid
    assert "unsupported" in msg.lower()


def test_pitch_estimation_accuracy(sine_audio):
    y, sr = sf.read(sine_audio)
    mean_f0, min_f0, max_f0, _ = compute_pitch_f0(y, sr)
    # Estimated pitch should be close to 220 Hz (+- 10 Hz)
    assert 210.0 <= mean_f0 <= 230.0


def test_analyze_audio_properties(sine_audio):
    analysis = analyze_audio(sine_audio)
    assert analysis["sample_rate"] == 16000
    assert analysis["duration_sec"] > 1.9
    assert isinstance(analysis["mean_pitch_hz"], (int, float))
    assert analysis["mean_rms_energy"] > 0.1
    assert "scientific_note" in analysis


def test_visual_report_generation(sine_audio, tmp_path):
    out_img = os.path.join(tmp_path, "report.png")
    result_path = generate_visual_acoustic_report(sine_audio, title_prefix="Test", output_image_path=out_img)
    assert os.path.exists(result_path)
    assert os.path.getsize(result_path) > 5000  # Non-empty image
