"""Unit tests for Tableau CSV export generation and data sanitization."""
import os
import csv
import io
import pytest
from src.database import init_database, save_recording
from src.analytics import export_tableau_csv_string, export_tableau_csv_file, TABLEAU_EXPORT_COLUMNS


def test_tableau_csv_headers_and_content(tmp_path):
    db_file = os.path.join(tmp_path, "export_test.db")
    init_database(db_file)

    save_recording(
        operation_type="transcription",
        file_name="meeting_notes.wav",
        duration_seconds=12.5,
        sample_rate=16000,
        processing_duration_ms=850.0,
        processing_status="success",
        transcript="Summary of project status.",
        word_count=4,
        character_count=26,
        language_code="en",
        estimated_wpm=19.2,
        mean_pitch_hz=130.5,
        rms_energy=0.075,
        spectral_centroid_hz=2100.0,
        speaker_similarity=0.82,
        created_at="2026-10-24T12:00:00Z",
        db_path=db_file,
    )

    csv_str = export_tableau_csv_string(db_path=db_file)
    reader = list(csv.reader(io.StringIO(csv_str)))
    headers = reader[0]

    assert headers == TABLEAU_EXPORT_COLUMNS
    assert len(reader) == 2  # 1 header + 1 row
    data_row = reader[1]
    assert data_row[headers.index("file_name")] == "meeting_notes.wav"
    assert data_row[headers.index("duration_seconds")] == "12.5"
    assert data_row[headers.index("word_count")] == "4"


def test_export_tableau_csv_file_creation(tmp_path):
    db_file = os.path.join(tmp_path, "export_file_test.db")
    init_database(db_file)
    out_csv = os.path.join(tmp_path, "tableau_export.csv")

    save_recording(
        operation_type="voice_cloning",
        file_name="cloned_test.wav",
        duration_seconds=4.0,
        sample_rate=16000,
        processing_duration_ms=1200.0,
        db_path=db_file,
    )

    path = export_tableau_csv_file(output_path=out_csv, db_path=db_file)
    assert os.path.exists(path)
    assert os.path.getsize(path) > 50
