import {
  RecordingRecord,
  AnalyticsSummary,
  TimeseriesPoint,
  SampleVoice,
  InspectResult,
  CloneResult,
  TranscriptionResult,
} from '../types';

const BASE_URL = '';

export async function fetchHealth(): Promise<{ status: string; service: string; version: string; capabilities: string[] }> {
  const res = await fetch(`${BASE_URL}/api/health`);
  if (!res.ok) throw new Error(`Health check failed: HTTP ${res.status}`);
  return res.json();
}

export async function fetchSamples(): Promise<SampleVoice[]> {
  const res = await fetch(`${BASE_URL}/api/samples`);
  if (!res.ok) throw new Error(`Failed to load samples: HTTP ${res.status}`);
  return res.json();
}

export async function fetchRecordings(params?: {
  limit?: number;
  offset?: number;
  operation_type?: string;
  status?: string;
}): Promise<{ total: number; limit: number; offset: number; records: RecordingRecord[] }> {
  const query = new URLSearchParams();
  if (params?.limit) query.set('limit', params.limit.toString());
  if (params?.offset !== undefined) query.set('offset', params.offset.toString());
  if (params?.operation_type && params.operation_type !== 'all') query.set('operation_type', params.operation_type);
  if (params?.status && params.status !== 'all') query.set('status', params.status);

  const res = await fetch(`${BASE_URL}/api/recordings?${query.toString()}`);
  if (!res.ok) throw new Error(`Failed to fetch recordings: HTTP ${res.status}`);
  return res.json();
}

export async function fetchRecordingDetail(recordingId: string): Promise<RecordingRecord> {
  const res = await fetch(`${BASE_URL}/api/recordings/${recordingId}`);
  if (!res.ok) throw new Error(`Recording not found: HTTP ${res.status}`);
  return res.json();
}

export async function fetchAnalyticsSummary(): Promise<AnalyticsSummary> {
  const res = await fetch(`${BASE_URL}/api/analytics/summary`);
  if (!res.ok) throw new Error(`Failed to fetch analytics summary: HTTP ${res.status}`);
  return res.json();
}

export async function fetchAnalyticsTimeseries(): Promise<{ timeseries: TimeseriesPoint[] }> {
  const res = await fetch(`${BASE_URL}/api/analytics/timeseries`);
  if (!res.ok) throw new Error(`Failed to fetch timeseries: HTTP ${res.status}`);
  return res.json();
}

export function getExportUrl(): string {
  return `${BASE_URL}/api/analytics/export`;
}

export async function inspectAudioFile(file: File | null, sampleId?: string): Promise<InspectResult> {
  const formData = new FormData();
  if (file) {
    formData.append('audio_file', file);
  }
  if (sampleId) {
    formData.append('sample_id', sampleId);
  }

  const res = await fetch(`${BASE_URL}/api/audio/inspect`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(err.detail || 'Audio inspection failed');
  }

  return res.json();
}

export async function cloneVoice(
  file: File | null,
  sampleId: string | null,
  text: string,
  language: string = 'en',
): Promise<CloneResult> {
  const formData = new FormData();
  if (file) {
    formData.append('audio_file', file);
  }
  if (sampleId) {
    formData.append('sample_id', sampleId);
  }
  formData.append('text', text);
  formData.append('language', language);

  const res = await fetch(`${BASE_URL}/api/voice/clone`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(err.detail || 'Voice cloning synthesis failed');
  }

  return res.json();
}

export async function transcribeAudio(
  file: File | null,
  sampleId: string | null,
  language?: string,
): Promise<TranscriptionResult> {
  const formData = new FormData();
  if (file) {
    formData.append('audio_file', file);
  }
  if (sampleId) {
    formData.append('sample_id', sampleId);
  }
  if (language) {
    formData.append('language', language);
  }

  const res = await fetch(`${BASE_URL}/api/transcribe`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: `HTTP ${res.status}` }));
    throw new Error(err.detail || 'Speech transcription failed');
  }

  return res.json();
}
