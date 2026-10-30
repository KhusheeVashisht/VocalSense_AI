"""FastAPI REST API router for VocalSense AI.

Provides standard endpoints for health, recording history, recording details,
analytics aggregations, CSV export, sample voices, audio inspection,
voice cloning synthesis, and speech transcription.
"""

import os
import shutil
import uuid
import time
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Response, UploadFile, File, Form
from fastapi.responses import JSONResponse, PlainTextResponse

from src.database import get_recording_by_id, list_recordings, save_recording
from src.analytics import get_analytics_summary, get_analytics_timeseries, export_tableau_csv_string
from src.audio_analysis import (
    validate_and_preprocess_audio,
    analyze_audio,
    generate_visual_acoustic_report,
)
from src.nlp_preprocessor import validate_and_preprocess_text
from src.voice_engine import VoiceCloningEngine
from src.evaluation import compare_recordings, plot_comparative_acoustic_report
from src.transcription import transcribe_audio

router = APIRouter(prefix="/api", tags=["VocalSense AI API"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
UPLOAD_DIR = os.path.join(OUTPUTS_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def resolve_audio_input(
    audio_file: Optional[UploadFile] = None,
    sample_id: Optional[str] = None,
) -> tuple[str, str]:
    """Resolve audio path from either uploaded file or bundled sample voice.

    Returns (file_path, display_name).
    """
    if audio_file and audio_file.filename:
        safe_name = os.path.basename(audio_file.filename)
        dest_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4().hex[:8]}_{safe_name}")
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(audio_file.file, f)
        return dest_path, safe_name
    elif sample_id:
        base = sample_id if sample_id.endswith(".wav") else f"{sample_id}.wav"
        cand = os.path.join(SAMPLES_DIR, base)
        if os.path.exists(cand):
            return cand, base
        raise HTTPException(status_code=400, detail=f"Sample voice '{sample_id}' not found.")
    else:
        raise HTTPException(status_code=400, detail="Please provide either an audio file upload or a sample_id.")


@router.get("/health")
def get_health():
    """Health check endpoint providing application status without exposing secrets."""
    return {
        "status": "healthy",
        "service": "VocalSense AI",
        "version": "1.0.0",
        "capabilities": [
            "voice_cloning",
            "speech_synthesis",
            "transcription",
            "audio_analysis",
            "analytics",
            "tableau_export",
        ],
    }


@router.get("/samples")
def get_samples():
    """Retrieve list of authorized sample reference audio recordings."""
    return [
        {
            "id": "sample_speaker_male",
            "name": "Speaker Alpha (Male Register)",
            "gender_tone": "Male Register (F0 ~110-140 Hz)",
            "file_name": "sample_speaker_male.wav",
            "audio_url": "/samples/sample_speaker_male.wav",
            "duration_seconds": 4.13,
            "sample_rate": 16000,
        },
        {
            "id": "sample_speaker_female",
            "name": "Speaker Beta (Female Register)",
            "gender_tone": "Female Register (F0 ~190-230 Hz)",
            "file_name": "sample_speaker_female.wav",
            "audio_url": "/samples/sample_speaker_female.wav",
            "duration_seconds": 3.46,
            "sample_rate": 16000,
        },
    ]


@router.get("/recordings")
def get_recordings(
    limit: int = Query(50, ge=1, le=200, description="Max records to return"),
    offset: int = Query(0, ge=0, description="Records offset"),
    operation_type: Optional[str] = Query(None, description="Filter by operation type"),
    status: Optional[str] = Query(None, description="Filter by status (success/failed)"),
):
    """Retrieve paginated recording history."""
    records, total = list_recordings(limit=limit, offset=offset, operation_type=operation_type, status=status)
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "records": records,
    }


@router.get("/recordings/{recording_id}")
def get_recording_detail(recording_id: str):
    """Retrieve details for a single recording by ID."""
    record = get_recording_by_id(recording_id)
    if not record:
        raise HTTPException(status_code=404, detail=f"Recording '{recording_id}' not found.")
    return record


@router.get("/analytics/summary")
def get_summary():
    """Retrieve high-level aggregate metrics across all recordings."""
    return get_analytics_summary()


@router.get("/analytics/timeseries")
def get_timeseries():
    """Retrieve daily time-series performance and activity statistics."""
    return {
        "timeseries": get_analytics_timeseries()
    }


@router.get("/analytics/export")
def export_csv():
    """Download the Tableau-ready CSV dataset."""
    csv_data = export_tableau_csv_string()
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=vocalsense_analytics_export.csv"},
    )


@router.post("/audio/inspect")
async def inspect_audio(
    audio_file: Optional[UploadFile] = File(None),
    sample_id: Optional[str] = Form(None),
):
    """Inspect and analyze acoustic properties of an uploaded or sample audio file."""
    audio_path, file_name = resolve_audio_input(audio_file, sample_id)

    is_valid, msg, meta = validate_and_preprocess_audio(audio_path)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Audio validation failed: {msg}")

    analysis = analyze_audio(audio_path)

    # Generate visual waveform & mel-spectrogram plot
    plot_filename = f"inspect_plot_{uuid.uuid4().hex[:8]}.png"
    plot_path = os.path.join(OUTPUTS_DIR, plot_filename)
    generate_visual_acoustic_report(audio_path, title_prefix="Acoustic Inspection", output_image_path=plot_path)

    return {
        "file_name": file_name,
        "duration_seconds": analysis["duration_sec"],
        "sample_rate": analysis["sample_rate"],
        "mean_pitch_hz": analysis["mean_pitch_hz"],
        "min_pitch_hz": analysis["min_pitch_hz"],
        "max_pitch_hz": analysis["max_pitch_hz"],
        "mean_rms_energy": analysis["mean_rms_energy"],
        "spectral_centroid_hz": analysis["spectral_centroid_hz"],
        "zero_crossing_rate": analysis["zero_crossing_rate"],
        "plot_url": f"/outputs/{plot_filename}",
        "audio_url": f"/outputs/uploads/{os.path.basename(audio_path)}" if "uploads" in audio_path else f"/samples/{os.path.basename(audio_path)}",
    }


@router.post("/voice/clone")
async def clone_voice(
    audio_file: Optional[UploadFile] = File(None),
    sample_id: Optional[str] = Form(None),
    text: str = Form(...),
    language: str = Form("en"),
):
    """Perform zero-shot reference-conditioned voice cloning and speech synthesis."""
    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Synthesis text cannot be empty.")

    audio_path, ref_name = resolve_audio_input(audio_file, sample_id)

    # Validate audio format
    is_valid_audio, audio_msg, _ = validate_and_preprocess_audio(audio_path)
    if not is_valid_audio:
        raise HTTPException(status_code=400, detail=f"Reference audio error: {audio_msg}")

    # Validate and normalize text
    is_valid_text, norm_text, text_meta = validate_and_preprocess_text(text, language=language)
    if not is_valid_text:
        raise HTTPException(status_code=400, detail=f"Text preprocessing error: {norm_text}")

    engine = VoiceCloningEngine.get_instance(device="cpu")
    success, msg, out_path, gen_meta = engine.clone_and_synthesize(
        text=norm_text,
        reference_audio_path=audio_path,
        language=language,
        output_dir=OUTPUTS_DIR,
    )

    if not success or not out_path or not os.path.exists(out_path):
        raise HTTPException(status_code=500, detail=f"Voice synthesis failed: {msg}")

    # Comparative evaluation
    eval_stats = compare_recordings(audio_path, out_path, engine=engine)

    # Generate 4-panel comparative acoustic plot
    plot_filename = f"comp_report_{uuid.uuid4().hex[:8]}.png"
    plot_path = os.path.join(OUTPUTS_DIR, plot_filename)
    plot_comparative_acoustic_report(audio_path, out_path, output_image_path=plot_path)

    gen_filename = os.path.basename(out_path)

    return {
        "status": "success",
        "message": msg,
        "file_name": gen_filename,
        "audio_url": f"/outputs/{gen_filename}",
        "plot_url": f"/outputs/{plot_filename}",
        "reference_file": ref_name,
        "synthesized_text": norm_text,
        "duration_seconds": gen_meta["audio_duration_seconds"],
        "synthesis_time_sec": gen_meta["synthesis_time_sec"],
        "real_time_factor": gen_meta["real_time_factor"],
        "speaker_embedding_similarity": eval_stats["speaker_embedding_similarity"],
        "similarity_interpretation": eval_stats["similarity_interpretation"],
        "comparison": eval_stats,
    }


@router.post("/transcribe")
async def transcribe_audio_endpoint(
    audio_file: Optional[UploadFile] = File(None),
    sample_id: Optional[str] = Form(None),
    language: Optional[str] = Form(None),
):
    """Transcribe speech audio using local Faster-Whisper model."""
    audio_path, file_name = resolve_audio_input(audio_file, sample_id)

    success, transcript, meta = transcribe_audio(audio_path, language=language)

    if not success:
        save_recording(
            operation_type="transcription",
            file_name=file_name,
            duration_seconds=0.0,
            sample_rate=16000,
            processing_duration_ms=meta.get("processing_duration_ms", 0.0),
            processing_status="failed",
            error_message=transcript,
        )
        raise HTTPException(status_code=400, detail=f"Transcription failed: {transcript}")

    # Persist success record to SQLite
    rec_id = save_recording(
        operation_type="transcription",
        file_name=file_name,
        duration_seconds=meta["audio_duration_seconds"],
        sample_rate=meta["sample_rate"],
        processing_duration_ms=meta["processing_duration_ms"],
        processing_status="success",
        transcript=transcript,
        word_count=meta["word_count"],
        character_count=meta["character_count"],
        language_code=meta["detected_language"],
        estimated_wpm=meta["estimated_wpm"],
    )

    audio_url = f"/outputs/uploads/{os.path.basename(audio_path)}" if "uploads" in audio_path else f"/samples/{os.path.basename(audio_path)}"

    return {
        "recording_id": rec_id,
        "transcript": transcript,
        "detected_language": meta["detected_language"],
        "language_confidence": meta["language_confidence"],
        "audio_duration_seconds": meta["audio_duration_seconds"],
        "word_count": meta["word_count"],
        "character_count": meta["character_count"],
        "estimated_words_per_minute": meta["estimated_wpm"],
        "processing_duration_ms": meta["processing_duration_ms"],
        "inference_duration_ms": meta["inference_duration_ms"],
        "audio_url": audio_url,
    }
