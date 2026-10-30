"""Analytics, Metric Calculation, and Tableau Export Module for VocalSense AI.

Calculates application-level metrics, summary statistics, time-series aggregations,
and produces sanitized, Tableau-ready CSV exports from persisted SQLite records.
"""

import os
import re
import csv
import io
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from src.database import get_db_connection, DEFAULT_DB_PATH


def sanitize_for_csv(value: Any) -> Any:
    """Protect against spreadsheet formula injection (CSV Injection).

    If a text field begins with =, +, -, @, or tab/return, prepend an apostrophe (').
    """
    if isinstance(value, str):
        if value and value[0] in ("=", "+", "-", "@", "\t", "\r"):
            return f"'{value}"
    return value


def calculate_word_count(text: Optional[str]) -> int:
    """Calculate word count using whitespace and punctuation tokenization."""
    if not text or not text.strip():
        return 0
    words = re.findall(r"\b\w+\b", text)
    return len(words)


def calculate_character_count(text: Optional[str], include_whitespace: bool = True) -> int:
    """Calculate character count with or without whitespace."""
    if not text:
        return 0
    if include_whitespace:
        return len(text)
    return len(re.sub(r"\s+", "", text))


def calculate_estimated_wpm(word_count: Optional[int], duration_seconds: Optional[float]) -> Optional[float]:
    """Calculate estimated speaking pace in words per minute.

    Returns None if duration is zero, negative, or inputs are missing.
    """
    if word_count is None or duration_seconds is None:
        return None
    if duration_seconds <= 0:
        return None
    wpm = word_count / (duration_seconds / 60.0)
    return round(float(wpm), 1)


def get_analytics_summary(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Compute aggregate analytics from actual persisted database records.

    Handles empty databases, failed records, and missing values safely.
    """
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()

        # 1. Total counts and status rates
        cursor.execute("""
            SELECT 
                COUNT(*) as total_recordings,
                SUM(CASE WHEN processing_status = 'success' THEN 1 ELSE 0 END) as total_success,
                SUM(CASE WHEN processing_status = 'failed' THEN 1 ELSE 0 END) as total_failed,
                SUM(duration_seconds) as total_audio_seconds,
                SUM(word_count) as total_words,
                AVG(CASE WHEN processing_status = 'success' THEN duration_seconds ELSE NULL END) as avg_duration,
                AVG(CASE WHEN processing_status = 'success' THEN word_count ELSE NULL END) as avg_words,
                AVG(CASE WHEN processing_status = 'success' THEN processing_duration_ms ELSE NULL END) as avg_proc_ms,
                AVG(CASE WHEN processing_status = 'success' AND estimated_words_per_minute > 0 THEN estimated_words_per_minute ELSE NULL END) as avg_wpm
            FROM recordings;
        """)
        row = cursor.fetchone()

        total = row["total_recordings"] or 0
        success = row["total_success"] or 0
        failed = row["total_failed"] or 0
        total_audio_sec = float(row["total_audio_seconds"] or 0.0)
        total_words = int(row["total_words"] or 0)
        avg_dur = float(row["avg_duration"] or 0.0)
        avg_words = float(row["avg_words"] or 0.0)
        avg_proc_ms = float(row["avg_proc_ms"] or 0.0)
        avg_wpm = float(row["avg_wpm"] or 0.0)
        success_rate = (success / total * 100.0) if total > 0 else 0.0

        # 2. Operations breakdown
        cursor.execute("""
            SELECT operation_type, COUNT(*) as count
            FROM recordings
            GROUP BY operation_type;
        """)
        ops = {r["operation_type"]: r["count"] for r in cursor.fetchall()}

        # 3. Language distribution
        cursor.execute("""
            SELECT COALESCE(language_code, 'unknown') as lang, COUNT(*) as count
            FROM recordings
            WHERE processing_status = 'success'
            GROUP BY lang;
        """)
        langs = {r["lang"]: r["count"] for r in cursor.fetchall()}

        # 4. Latency / RTF
        # Real-time factor = (processing_duration_sec / duration_sec)
        cursor.execute("""
            SELECT AVG( (processing_duration_ms / 1000.0) / NULLIF(duration_seconds, 0) ) as avg_rtf
            FROM recordings
            WHERE processing_status = 'success' AND duration_seconds > 0;
        """)
        rtf_row = cursor.fetchone()
        avg_rtf = float(rtf_row["avg_rtf"] or 0.0)

        return {
            "total_recordings": total,
            "successful_recordings": success,
            "failed_recordings": failed,
            "success_rate_percent": round(success_rate, 1),
            "total_audio_duration_seconds": round(total_audio_sec, 2),
            "total_audio_duration_minutes": round(total_audio_sec / 60.0, 2),
            "total_words_processed": total_words,
            "average_recording_duration_sec": round(avg_dur, 2),
            "average_words_per_recording": round(avg_words, 1),
            "average_processing_duration_ms": round(avg_proc_ms, 1),
            "average_real_time_factor": round(avg_rtf, 2),
            "average_speaking_pace_wpm": round(avg_wpm, 1),
            "operations_breakdown": ops,
            "languages_distribution": langs,
        }


def get_analytics_timeseries(db_path: str = DEFAULT_DB_PATH) -> List[Dict[str, Any]]:
    """Compute daily timeseries of activity and performance metrics."""
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                SUBSTR(created_at, 1, 10) as date,
                COUNT(*) as count,
                SUM(duration_seconds) as total_duration_sec,
                AVG(processing_duration_ms) as avg_processing_ms,
                SUM(CASE WHEN processing_status = 'success' THEN 1 ELSE 0 END) as success_count,
                SUM(CASE WHEN processing_status = 'failed' THEN 1 ELSE 0 END) as fail_count
            FROM recordings
            GROUP BY date
            ORDER BY date ASC;
        """)
        rows = cursor.fetchall()
        return [
            {
                "date": r["date"],
                "count": r["count"],
                "total_duration_sec": round(float(r["total_duration_sec"] or 0.0), 2),
                "avg_processing_ms": round(float(r["avg_processing_ms"] or 0.0), 1),
                "success_count": r["success_count"],
                "fail_count": r["fail_count"],
            }
            for r in rows
        ]


TABLEAU_EXPORT_COLUMNS = [
    "recording_id",
    "created_at",
    "operation_type",
    "file_name",
    "duration_seconds",
    "word_count",
    "character_count",
    "language_code",
    "processing_status",
    "processing_duration_ms",
    "estimated_words_per_minute",
    "mean_pitch_hz",
    "rms_energy",
    "spectral_centroid_hz",
    "speaker_similarity",
]


def export_tableau_csv_string(db_path: str = DEFAULT_DB_PATH) -> str:
    """Export all recording records as a clean, Tableau-friendly CSV string.

    Sanitizes values against formula injection and formats columns consistently.
    """
    output = io.StringIO()
    writer = csv.writer(output, lineterminator="\n")
    writer.writerow(TABLEAU_EXPORT_COLUMNS)

    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT {', '.join(TABLEAU_EXPORT_COLUMNS)}
            FROM recordings
            ORDER BY created_at ASC;
        """)
        for row in cursor.fetchall():
            row_dict = dict(row)
            row_values = []
            for col in TABLEAU_EXPORT_COLUMNS:
                val = row_dict.get(col)
                if val is None:
                    row_values.append("")
                elif isinstance(val, (int, float)):
                    row_values.append(val)
                else:
                    row_values.append(sanitize_for_csv(str(val)))
            writer.writerow(row_values)

    return output.getvalue()


def export_tableau_csv_file(
    output_path: str = "outputs/vocalsense_analytics_export.csv",
    db_path: str = DEFAULT_DB_PATH,
) -> str:
    """Generate and save the Tableau CSV export file to disk."""
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    csv_content = export_tableau_csv_string(db_path=db_path)
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        # Use utf-8-sig so Tableau and Excel immediately recognise UTF-8 characters
        f.write(csv_content)
    return output_path
