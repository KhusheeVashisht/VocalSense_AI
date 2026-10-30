"""Unit tests for SQLite database persistence layer."""
import os
import pytest
from src.database import (
    init_database,
    save_recording,
    get_recording_by_id,
    list_recordings,
)


@pytest.fixture
def temp_db(tmp_path):
    """Fixture providing a temporary SQLite database path."""
    db_file = os.path.join(tmp_path, "test_vocalsense.db")
    init_database(db_file)
    return db_file


def test_init_database(temp_db):
    assert os.path.exists(temp_db)


def test_save_and_get_recording(temp_db):
    rec_id = save_recording(
        operation_type="transcription",
        file_name="sample_test.wav",
        duration_seconds=5.2,
        sample_rate=16000,
        processing_duration_ms=450.0,
        processing_status="success",
        transcript="Hello VocalSense AI.",
        word_count=3,
        character_count=20,
        language_code="en",
        estimated_wpm=34.6,
        mean_pitch_hz=145.2,
        rms_energy=0.08,
        speaker_similarity=0.78,
        db_path=temp_db,
    )
    assert rec_id is not None

    record = get_recording_by_id(rec_id, db_path=temp_db)
    assert record is not None
    assert record["recording_id"] == rec_id
    assert record["file_name"] == "sample_test.wav"
    assert record["word_count"] == 3
    assert record["duration_seconds"] == 5.2
    assert record["language_code"] == "en"
    assert record["processing_status"] == "success"


def test_list_recordings_pagination(temp_db):
    for i in range(10):
        save_recording(
            operation_type="voice_cloning" if i % 2 == 0 else "transcription",
            file_name=f"file_{i}.wav",
            duration_seconds=float(i + 1),
            sample_rate=16000,
            processing_duration_ms=100.0 * (i + 1),
            db_path=temp_db,
        )

    # Test limit and offset
    records, total = list_recordings(limit=4, offset=0, db_path=temp_db)
    assert total == 10
    assert len(records) == 4

    records_p2, _ = list_recordings(limit=4, offset=4, db_path=temp_db)
    assert len(records_p2) == 4
    assert records[0]["recording_id"] != records_p2[0]["recording_id"]

    # Test filtering by operation type
    clones, clone_total = list_recordings(operation_type="voice_cloning", db_path=temp_db)
    assert clone_total == 5
    for r in clones:
        assert r["operation_type"] == "voice_cloning"


def test_empty_database_queries(tmp_path):
    empty_db = os.path.join(tmp_path, "empty.db")
    init_database(empty_db)
    record = get_recording_by_id("non_existent_id", db_path=empty_db)
    assert record is None

    records, total = list_recordings(db_path=empty_db)
    assert total == 0
    assert len(records) == 0
