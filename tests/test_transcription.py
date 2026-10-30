"""Unit tests for faster-whisper transcription module."""
import os
import pytest
from src.transcription import transcribe_audio, get_whisper_model


def test_transcription_model_initialization():
    model = get_whisper_model()
    assert model is not None


def test_transcribe_sample_audio():
    sample_path = "samples/sample_speaker_male.wav"
    assert os.path.exists(sample_path)

    success, transcript, meta = transcribe_audio(sample_path)
    assert success, f"Transcription failed: {transcript}"
    assert len(transcript) > 0
    assert meta["word_count"] > 0
    assert meta["detected_language"] in ("en", "english")
    assert meta["language_confidence"] > 0.8
    assert meta["audio_duration_seconds"] > 3.0
    assert meta["processing_duration_ms"] > 0


def test_transcribe_nonexistent_audio():
    success, msg, _ = transcribe_audio("nonexistent_path_xyz.wav")
    assert not success
    assert "not exist" in msg.lower()
