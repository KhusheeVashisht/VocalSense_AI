export interface RecordingRecord {
  recording_id: string;
  created_at: string;
  operation_type: 'voice_cloning' | 'transcription' | 'acoustic_analysis' | string;
  file_name: string;
  duration_seconds: number;
  sample_rate: number;
  transcript: string | null;
  word_count: number | null;
  character_count: number | null;
  language_code: string | null;
  processing_status: 'success' | 'failed' | string;
  processing_duration_ms: number;
  stage_durations_json?: string | null;
  estimated_words_per_minute: number | null;
  mean_pitch_hz: number | null;
  rms_energy: number | null;
  spectral_centroid_hz: number | null;
  speaker_similarity: number | null;
  error_message: string | null;
}

export interface AnalyticsSummary {
  total_recordings: number;
  successful_recordings: number;
  failed_recordings: number;
  success_rate_percent: number;
  total_audio_duration_seconds: number;
  total_audio_duration_minutes: number;
  total_words_processed: number;
  average_recording_duration_sec: number;
  average_words_per_recording: number;
  average_processing_duration_ms: number;
  average_real_time_factor: number;
  average_speaking_pace_wpm: number;
  operations_breakdown: Record<string, number>;
  languages_distribution: Record<string, number>;
}

export interface TimeseriesPoint {
  date: string;
  count: number;
  total_duration_sec: number;
  avg_processing_ms: number;
  success_count: number;
  fail_count: number;
}

export interface SampleVoice {
  id: string;
  name: string;
  gender_tone: string;
  file_name: string;
  audio_url: string;
  duration_seconds: number;
  sample_rate: number;
}

export interface InspectResult {
  file_name: string;
  duration_seconds: number;
  sample_rate: number;
  mean_pitch_hz: number | string;
  min_pitch_hz: number | string;
  max_pitch_hz: number | string;
  mean_rms_energy: number;
  spectral_centroid_hz: number;
  zero_crossing_rate: number;
  plot_url: string;
  audio_url: string;
}

export interface CloneResult {
  status: string;
  message: string;
  file_name: string;
  audio_url: string;
  plot_url: string;
  reference_file: string;
  synthesized_text: string;
  duration_seconds: number;
  synthesis_time_sec: number;
  real_time_factor: number;
  speaker_embedding_similarity: number;
  similarity_interpretation: string;
  comparison: {
    speaker_embedding_similarity: number;
    similarity_interpretation: string;
    reference_pitch_hz: number;
    generated_pitch_hz: number;
    pitch_difference_hz: number;
    reference_energy_rms: number;
    generated_energy_rms: number;
    energy_ratio_gen_to_ref: number;
    reference_centroid_hz: number;
    generated_centroid_hz: number;
    reference_duration_sec: number;
    generated_duration_sec: number;
  };
}

export interface TranscriptionResult {
  recording_id: string;
  transcript: string;
  detected_language: string;
  language_confidence: number;
  audio_duration_seconds: number;
  word_count: number;
  character_count: number;
  estimated_words_per_minute: number;
  processing_duration_ms: number;
  inference_duration_ms: number;
  audio_url: string;
}
