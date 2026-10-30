"""Unit tests for analytics, metric calculation, and sanitization."""
import os
import pytest
from src.database import init_database, save_recording
from src.analytics import (
    calculate_word_count,
    calculate_character_count,
    calculate_estimated_wpm,
    sanitize_for_csv,
    get_analytics_summary,
    get_analytics_timeseries,
)


def test_metric_calculations():
    text = "Artificial intelligence, deep learning, & speech synthesis!"
    words = calculate_word_count(text)
    assert words == 6

    chars_with_ws = calculate_character_count(text, include_whitespace=True)
    chars_no_ws = calculate_character_count(text, include_whitespace=False)
    assert chars_with_ws > chars_no_ws
    assert chars_with_ws == len(text)

    # Speaking pace WPM
    wpm = calculate_estimated_wpm(word_count=150, duration_seconds=60.0)
    assert wpm == 150.0

    # Zero or negative duration handling
    assert calculate_estimated_wpm(100, 0.0) is None
    assert calculate_estimated_wpm(100, -5.0) is None
    assert calculate_estimated_wpm(None, 10.0) is None


def test_csv_injection_sanitization():
    unsafe_formula = "=SUM(A1:A10)"
    sanitized = sanitize_for_csv(unsafe_formula)
    assert sanitized.startswith("'")

    safe_text = "Standard speech transcript text"
    assert sanitize_for_csv(safe_text) == safe_text

    numeric_val = 123.45
    assert sanitize_for_csv(numeric_val) == numeric_val


def test_analytics_summary_and_timeseries(tmp_path):
    db_file = os.path.join(tmp_path, "analytics_test.db")
    init_database(db_file)

    # Empty DB behavior
    empty_summary = get_analytics_summary(db_path=db_file)
    assert empty_summary["total_recordings"] == 0
    assert empty_summary["success_rate_percent"] == 0.0

    # Populate 3 recordings
    save_recording(
        operation_type="transcription",
        file_name="rec1.wav",
        duration_seconds=10.0,
        sample_rate=16000,
        processing_duration_ms=1000.0,
        processing_status="success",
        transcript="Ten seconds of clear speech.",
        word_count=5,
        estimated_wpm=30.0,
        language_code="en",
        created_at="2026-10-24T10:00:00Z",
        db_path=db_file,
    )
    save_recording(
        operation_type="voice_cloning",
        file_name="rec2.wav",
        duration_seconds=20.0,
        sample_rate=16000,
        processing_duration_ms=2000.0,
        processing_status="success",
        transcript="Twenty seconds of cloned speech.",
        word_count=5,
        estimated_wpm=15.0,
        language_code="en",
        created_at="2026-10-24T11:00:00Z",
        db_path=db_file,
    )
    save_recording(
        operation_type="transcription",
        file_name="rec3.wav",
        duration_seconds=5.0,
        sample_rate=16000,
        processing_duration_ms=500.0,
        processing_status="failed",
        error_message="Audio decoding error",
        created_at="2026-10-24T12:00:00Z",
        db_path=db_file,
    )

    summary = get_analytics_summary(db_path=db_file)
    assert summary["total_recordings"] == 3
    assert summary["successful_recordings"] == 2
    assert summary["failed_recordings"] == 1
    assert summary["total_audio_duration_seconds"] == 35.0
    assert summary["total_words_processed"] == 10
    assert summary["average_recording_duration_sec"] == 15.0  # (10 + 20) / 2 success
    assert summary["operations_breakdown"]["transcription"] == 2
    assert summary["operations_breakdown"]["voice_cloning"] == 1

    timeseries = get_analytics_timeseries(db_path=db_file)
    assert len(timeseries) == 1
    assert timeseries[0]["date"] == "2026-10-24"
    assert timeseries[0]["count"] == 3
