"""Unit tests for speaker similarity and acoustic evaluation."""
import os
import pytest
from src.evaluation import (
    compute_speaker_similarity,
    compare_recordings,
    plot_comparative_acoustic_report,
)
from src.voice_engine import VoiceCloningEngine


@pytest.fixture(scope="module")
def voice_engine():
    engine = VoiceCloningEngine.get_instance(device="cpu")
    engine.load_models()
    return engine


def test_speaker_similarity_identical_audio(voice_engine):
    male_path = os.path.join("samples", "sample_speaker_male.wav")
    assert os.path.exists(male_path)

    # Comparing a file to itself should produce similarity very close to 1.0
    sim = compute_speaker_similarity(male_path, male_path, engine=voice_engine)
    assert 0.99 <= sim <= 1.0001


def test_speaker_similarity_distinct_speakers(voice_engine):
    male_path = os.path.join("samples", "sample_speaker_male.wav")
    female_path = os.path.join("samples", "sample_speaker_female.wav")
    assert os.path.exists(male_path) and os.path.exists(female_path)

    # Comparing two different speakers should produce lower similarity than self-similarity
    sim_diff = compute_speaker_similarity(male_path, female_path, engine=voice_engine)
    sim_same = compute_speaker_similarity(male_path, male_path, engine=voice_engine)
    assert sim_diff < sim_same


def test_compare_recordings_output_structure(voice_engine):
    male_path = os.path.join("samples", "sample_speaker_male.wav")
    female_path = os.path.join("samples", "sample_speaker_female.wav")

    comparison = compare_recordings(male_path, female_path, engine=voice_engine)
    assert "speaker_embedding_similarity" in comparison
    assert "reference_pitch_hz" in comparison
    assert "generated_pitch_hz" in comparison
    assert "energy_ratio_gen_to_ref" in comparison
    assert "evaluation_notes" in comparison


def test_plot_comparative_report(tmp_path):
    male_path = os.path.join("samples", "sample_speaker_male.wav")
    female_path = os.path.join("samples", "sample_speaker_female.wav")
    out_img = os.path.join(tmp_path, "comparative_plot.png")

    result = plot_comparative_acoustic_report(male_path, female_path, output_image_path=out_img)
    assert os.path.exists(result)
    assert os.path.getsize(result) > 10000
