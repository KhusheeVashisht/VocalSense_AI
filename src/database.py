"""Database persistence layer for VocalSense AI.

Uses SQLite with parameterised queries, transactions, and robust error handling.
Stores metadata, processing metrics, and analytical records for speech operations.
Raw audio binary is NOT stored in the database to keep the database lightweight.
"""

import os
import sqlite3
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vocalsense.db")


def get_db_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    """Create a thread-safe connection to the SQLite database with row factory."""
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    conn = sqlite3.connect(db_path, timeout=30.0, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Enable WAL mode for concurrency and foreign keys
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_database(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize database schema safely without dropping existing tables."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recordings (
                recording_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL,
                operation_type TEXT NOT NULL, -- 'voice_cloning', 'transcription', 'acoustic_analysis'
                file_name TEXT NOT NULL,
                duration_seconds REAL NOT NULL,
                sample_rate INTEGER NOT NULL,
                transcript TEXT,
                word_count INTEGER,
                character_count INTEGER,
                language_code TEXT,
                processing_status TEXT NOT NULL, -- 'success', 'failed'
                processing_duration_ms REAL NOT NULL,
                stage_durations_json TEXT, -- JSON string of stage timings
                estimated_words_per_minute REAL,
                mean_pitch_hz REAL,
                rms_energy REAL,
                spectral_centroid_hz REAL,
                speaker_similarity REAL,
                error_message TEXT
            );
        """)
        # Safe schema migration for existing databases
        cursor.execute("PRAGMA table_info(recordings);")
        existing_cols = [row["name"] for row in cursor.fetchall()]
        if existing_cols and "estimated_words_per_minute" not in existing_cols:
            cursor.execute("ALTER TABLE recordings ADD COLUMN estimated_words_per_minute REAL;")

        # Indexes for fast historical queries and analytics
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recordings_created_at ON recordings (created_at);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recordings_operation_type ON recordings (operation_type);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_recordings_status ON recordings (processing_status);")
        conn.commit()


def save_recording(
    operation_type: str,
    file_name: str,
    duration_seconds: float,
    sample_rate: int,
    processing_duration_ms: float,
    processing_status: str = "success",
    transcript: Optional[str] = None,
    word_count: Optional[int] = None,
    character_count: Optional[int] = None,
    language_code: Optional[str] = None,
    stage_durations: Optional[Dict[str, float]] = None,
    estimated_wpm: Optional[float] = None,
    estimated_words_per_minute: Optional[float] = None,
    mean_pitch_hz: Optional[float] = None,
    rms_energy: Optional[float] = None,
    spectral_centroid_hz: Optional[float] = None,
    speaker_similarity: Optional[float] = None,
    error_message: Optional[str] = None,
    recording_id: Optional[str] = None,
    created_at: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH,
) -> str:
    """Persist a recording event and its metrics to SQLite.

    Returns the recording_id.
    """
    init_database(db_path)
    if not recording_id:
        recording_id = str(uuid.uuid4())
    if not created_at:
        created_at = datetime.now(timezone.utc).isoformat()

    if estimated_wpm is None and estimated_words_per_minute is not None:
        estimated_wpm = estimated_words_per_minute

    stage_json = json.dumps(stage_durations) if stage_durations else None

    # Protect against NaN or Inf values in floats
    def clean_float(val: Optional[float]) -> Optional[float]:
        if val is None:
            return None
        try:
            f = float(val)
            return None if (f != f or abs(f) == float("inf")) else f
        except (ValueError, TypeError):
            return None

    clean_dur = clean_float(duration_seconds) or 0.0
    clean_proc = clean_float(processing_duration_ms) or 0.0
    clean_wpm = clean_float(estimated_wpm)
    clean_pitch = clean_float(mean_pitch_hz)
    clean_rms = clean_float(rms_energy)
    clean_centroid = clean_float(spectral_centroid_hz)
    clean_sim = clean_float(speaker_similarity)

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO recordings (
                recording_id, created_at, operation_type, file_name,
                duration_seconds, sample_rate, transcript, word_count,
                character_count, language_code, processing_status,
                processing_duration_ms, stage_durations_json, estimated_words_per_minute,
                mean_pitch_hz, rms_energy, spectral_centroid_hz,
                speaker_similarity, error_message
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(recording_id) DO UPDATE SET
                processing_status=excluded.processing_status,
                processing_duration_ms=excluded.processing_duration_ms,
                transcript=excluded.transcript,
                word_count=excluded.word_count,
                character_count=excluded.character_count,
                estimated_words_per_minute=excluded.estimated_words_per_minute,
                error_message=excluded.error_message;
            """,
            (
                recording_id,
                created_at,
                operation_type,
                file_name,
                clean_dur,
                int(sample_rate),
                transcript,
                word_count,
                character_count,
                language_code,
                processing_status,
                clean_proc,
                stage_json,
                clean_wpm,
                clean_pitch,
                clean_rms,
                clean_centroid,
                clean_sim,
                error_message,
            ),
        )
        conn.commit()
    return recording_id


def get_recording_by_id(recording_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Retrieve a single recording record by ID."""
    init_database(db_path)
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM recordings WHERE recording_id = ?", (recording_id,))
        row = cursor.fetchone()
        if not row:
            return None
        return dict(row)


def list_recordings(
    limit: int = 50,
    offset: int = 0,
    operation_type: Optional[str] = None,
    status: Optional[str] = None,
    db_path: str = DEFAULT_DB_PATH,
) -> Tuple[List[Dict[str, Any]], int]:
    """Retrieve paginated recording history with optional filtering.

    Returns:
        (list_of_records, total_count)
    """
    init_database(db_path)
    where_clauses = []
    params: List[Any] = []

    if operation_type:
        where_clauses.append("operation_type = ?")
        params.append(operation_type)
    if status:
        where_clauses.append("processing_status = ?")
        params.append(status)

    where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) as total FROM recordings {where_sql}", params)
        total_count = cursor.fetchone()["total"]

        query = f"""
            SELECT * FROM recordings
            {where_sql}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [limit, offset])
        rows = [dict(r) for r in cursor.fetchall()]
        return rows, total_count
