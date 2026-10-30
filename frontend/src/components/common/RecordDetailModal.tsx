import React from 'react';
import { X, Copy, Check, FileAudio, Clock, Activity, Zap, ShieldAlert } from 'lucide-react';
import { RecordingRecord } from '../../types';

interface RecordDetailModalProps {
  record: RecordingRecord | null;
  onClose: () => void;
  onCopySuccess: () => void;
}

export const RecordDetailModal: React.FC<RecordDetailModalProps> = ({
  record,
  onClose,
  onCopySuccess,
}) => {
  const [copiedId, setCopiedId] = React.useState(false);

  if (!record) return null;

  const handleCopyId = () => {
    navigator.clipboard.writeText(record.recording_id);
    setCopiedId(true);
    onCopySuccess();
    setTimeout(() => setCopiedId(false), 2000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/75 backdrop-blur-sm animate-in fade-in duration-200">
      <div
        className="bg-space-850 border border-space-700 w-full max-w-2xl rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[90vh]"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-space-700 bg-space-900/60">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-brand-purple/10 border border-brand-purple/20 text-brand-purple">
              <FileAudio className="w-5 h-5" />
            </div>
            <div>
              <h3 className="text-base font-semibold text-white">Recording Details</h3>
              <p className="text-xs text-slate-400">Database Record Metadata & Telemetry</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 text-slate-400 hover:text-white rounded-lg hover:bg-space-750 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm">
          {/* UUID Bar */}
          <div className="p-3.5 bg-space-900 rounded-xl border border-space-750 flex items-center justify-between gap-2">
            <div className="min-w-0">
              <span className="text-[11px] uppercase tracking-wider font-semibold text-slate-400 block mb-0.5">
                Recording UUID
              </span>
              <code className="text-xs text-brand-purple font-mono block truncate select-all">
                {record.recording_id}
              </code>
            </div>
            <button
              onClick={handleCopyId}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-space-800 hover:bg-space-700 text-xs font-medium text-slate-300 transition-colors border border-space-700 shrink-0"
            >
              {copiedId ? <Check className="w-3.5 h-3.5 text-brand-emerald" /> : <Copy className="w-3.5 h-3.5" />}
              {copiedId ? 'Copied' : 'Copy ID'}
            </button>
          </div>

          {/* Key Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
            <div className="p-3 bg-space-900/50 rounded-xl border border-space-750">
              <span className="text-xs text-slate-400 block mb-1">Operation Type</span>
              <span className="font-semibold text-white capitalize">
                {record.operation_type.replace('_', ' ')}
              </span>
            </div>

            <div className="p-3 bg-space-900/50 rounded-xl border border-space-750">
              <span className="text-xs text-slate-400 block mb-1">Processing Status</span>
              <span
                className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${
                  record.processing_status === 'success'
                    ? 'bg-brand-emerald/10 text-brand-emerald border border-brand-emerald/30'
                    : 'bg-brand-rose/10 text-brand-rose border border-brand-rose/30'
                }`}
              >
                {record.processing_status.toUpperCase()}
              </span>
            </div>

            <div className="p-3 bg-space-900/50 rounded-xl border border-space-750">
              <span className="text-xs text-slate-400 block mb-1">Audio Duration</span>
              <span className="font-semibold text-white">{record.duration_seconds.toFixed(2)} s</span>
            </div>

            <div className="p-3 bg-space-900/50 rounded-xl border border-space-750">
              <span className="text-xs text-slate-400 block mb-1">Execution Latency</span>
              <span className="font-semibold text-white">{record.processing_duration_ms.toFixed(1)} ms</span>
            </div>

            <div className="p-3 bg-space-900/50 rounded-xl border border-space-750">
              <span className="text-xs text-slate-400 block mb-1">Speaking Pace</span>
              <span className="font-semibold text-white">
                {record.estimated_words_per_minute ? `${record.estimated_words_per_minute} WPM` : 'N/A'}
              </span>
            </div>

            <div className="p-3 bg-space-900/50 rounded-xl border border-space-750">
              <span className="text-xs text-slate-400 block mb-1">Word & Char Count</span>
              <span className="font-semibold text-white">
                {record.word_count ?? 0} words ({record.character_count ?? 0} chars)
              </span>
            </div>
          </div>

          {/* Acoustic Analysis Section */}
          <div className="space-y-2">
            <h4 className="text-xs uppercase font-semibold text-slate-400 tracking-wider flex items-center gap-1.5">
              <Activity className="w-3.5 h-3.5 text-brand-indigo" /> Acoustic Measurements
            </h4>
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-2.5">
              <div className="p-2.5 bg-space-900/30 rounded-lg border border-space-750 text-xs">
                <span className="text-slate-400 block">Mean Pitch (F0)</span>
                <span className="font-medium text-slate-200">
                  {record.mean_pitch_hz ? `${record.mean_pitch_hz} Hz` : 'Unvoiced / N/A'}
                </span>
              </div>
              <div className="p-2.5 bg-space-900/30 rounded-lg border border-space-750 text-xs">
                <span className="text-slate-400 block">RMS Energy</span>
                <span className="font-medium text-slate-200">
                  {record.rms_energy ? record.rms_energy.toFixed(4) : 'N/A'}
                </span>
              </div>
              <div className="p-2.5 bg-space-900/30 rounded-lg border border-space-750 text-xs">
                <span className="text-slate-400 block">Spectral Centroid</span>
                <span className="font-medium text-slate-200">
                  {record.spectral_centroid_hz ? `${record.spectral_centroid_hz} Hz` : 'N/A'}
                </span>
              </div>
              <div className="p-2.5 bg-space-900/30 rounded-lg border border-space-750 text-xs">
                <span className="text-slate-400 block">Cosine Similarity</span>
                <span className="font-medium text-brand-purple">
                  {record.speaker_similarity !== null ? record.speaker_similarity.toFixed(4) : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Transcript / Text Payload */}
          {record.transcript && (
            <div className="space-y-1.5">
              <h4 className="text-xs uppercase font-semibold text-slate-400 tracking-wider">
                Transcript / Text Payload
              </h4>
              <div className="p-3.5 bg-space-900/80 rounded-xl border border-space-750 text-slate-200 text-xs leading-relaxed max-h-32 overflow-y-auto">
                {record.transcript}
              </div>
            </div>
          )}

          {/* Error Message if failed */}
          {record.error_message && (
            <div className="p-3 bg-brand-rose/10 border border-brand-rose/30 rounded-xl text-xs text-rose-200 flex items-start gap-2.5">
              <ShieldAlert className="w-4 h-4 text-brand-rose shrink-0 mt-0.5" />
              <div>
                <span className="font-semibold block">Execution Diagnostic Error</span>
                <p className="mt-0.5">{record.error_message}</p>
              </div>
            </div>
          )}

          {/* Timestamp Footer */}
          <div className="text-[11px] text-slate-500 flex items-center justify-between pt-2 border-t border-space-750">
            <span>Source File: {record.file_name}</span>
            <span>Recorded at: {new Date(record.created_at).toLocaleString()}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
