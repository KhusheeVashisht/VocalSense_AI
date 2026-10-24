"""Unit tests for voice cloning engine."""
import os
import pytest
import torch
import soundfile as sf
from src.voice_engine import VoiceCloningEngine


@pytest.fixture(scope="module")
def voice_engine():
    engine = VoiceCloningEngine.get_instance(device="cpu")
    engine.load_models()
    return engine


def test_models_loaded(voice_engine):
    assert voice_engine.is_loaded
    assert voice_engine.speaker_encoder is not None
    assert voice_engine.processor is not None
    assert voice_engine.tts_model is not None
    assert voice_engine.vocoder is not None


def test_speaker_embedding_extraction(voice_engine):
    ref_path = os.path.join("samples", "sample_speaker_male.wav")
    assert os.path.exists(ref_path), "Sample speaker file must exist."

    embedding, msg = voice_engine.extract_speaker_embedding(ref_path)
    assert isinstance(embedding, torch.Tensor)
    assert embedding.shape == torch.Size([1, 512])

    # Check L2 normalization (norm should be ~1.0)
    norm = torch.norm(embedding, p=2, dim=-1).item()
    assert abs(norm - 1.0) < 1e-3

    # Check caching
    cached_emb, cache_msg = voice_engine.extract_speaker_embedding(ref_path)
    assert "Cached" in cache_msg
    assert torch.equal(embedding, cached_emb)


def test_clone_and_synthesize_end_to_end(voice_engine, tmp_path):
    ref_path = os.path.join("samples", "sample_speaker_male.wav")
    text = "VocalSense AI voice cloning verification test."

    success, msg, out_path, meta = voice_engine.clone_and_synthesize(
        text=text,
        reference_audio_path=ref_path,
        language="en",
        output_dir=str(tmp_path),
    )

    assert success, f"Synthesis failed: {msg}"
    assert out_path is not None
    assert os.path.exists(out_path)

    # Verify generated audio file
    sig, sr = sf.read(out_path)
    assert sr == 16000
    assert len(sig) > 0
    duration = len(sig) / sr
    assert duration > 1.0
    assert meta["model_name"] != ""
