"""Speech Transcription Module for VocalSense AI.

Integrates lightweight, local CPU speech-to-text using faster-whisper (tiny model, int8 quantization).
Provides fast transcription, language detection, and timing benchmarks without external API calls.
"""

import os
import time
from typing import Dict, Any, Tuple, Optional
import soundfile as sf
import librosa

_whisper_model = None


def get_whisper_model(model_size: str = "tiny", device: str = "cpu", compute_type: str = "int8"):
    """Singleton accessor for local faster-whisper model."""
    global _whisper_model
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            _whisper_model = WhisperModel(model_size, device=device, compute_type=compute_type)
        except Exception as e:
            raise RuntimeError(f"Failed to initialize faster-whisper model: {str(e)}")
    return _whisper_model


def transcribe_audio(
    audio_path: str,
    language: Optional[str] = None,
    beam_size: int = 2,
) -> Tuple[bool, str, Dict[str, Any]]:
    """Transcribe an audio recording into text with language detection and timing metrics.

    Returns:
        (success, transcript_or_error_message, metadata_dict)
    """
    if not audio_path or not os.path.exists(audio_path):
        return False, f"Audio file does not exist: {audio_path}", {}

    start_time = time.perf_counter()

    try:
        # Load audio properties to get exact duration
        y, sr = librosa.load(audio_path, sr=None)
        duration_seconds = float(len(y) / sr)
        if duration_seconds < 0.2:
            return False, "Audio is too short for transcription (minimum 0.2 seconds).", {}

        model = get_whisper_model()
        stage_start = time.perf_counter()

        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=beam_size,
            vad_filter=True,  # Filter out silence
        )

        segment_list = list(segments)
        transcript = " ".join([s.text.strip() for s in segment_list]).strip()
        inference_time_ms = (time.perf_counter() - stage_start) * 1000.0
        total_time_ms = (time.perf_counter() - start_time) * 1000.0

        words = transcript.split()
        word_count = len(words)
        char_count = len(transcript)

        # Calculate estimated words per minute
        estimated_wpm = (word_count / (duration_seconds / 60.0)) if duration_seconds > 0 else 0.0

        metadata = {
            "file_name": os.path.basename(audio_path),
            "audio_duration_seconds": round(duration_seconds, 2),
            "sample_rate": sr,
            "detected_language": info.language if info else "unknown",
            "language_confidence": round(float(info.language_probability), 4) if info else 0.0,
            "word_count": word_count,
            "character_count": char_count,
            "estimated_wpm": round(estimated_wpm, 1),
            "processing_duration_ms": round(total_time_ms, 2),
            "inference_duration_ms": round(inference_time_ms, 2),
            "segments_count": len(segment_list),
        }

        return True, transcript, metadata

    except Exception as e:
        total_time_ms = (time.perf_counter() - start_time) * 1000.0
        return False, f"Transcription error: {str(e)}", {"processing_duration_ms": round(total_time_ms, 2)}
