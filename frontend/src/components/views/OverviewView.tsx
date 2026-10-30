import React from 'react';
import {
  Mic2,
  FileText,
  History,
  BarChart3,
  ArrowRight,
  Clock,
  CheckCircle2,
  AlertCircle,
  Activity,
  Zap,
  Volume2,
} from 'lucide-react';
import { AnalyticsSummary, RecordingRecord } from '../../types';
import { NavTab } from '../layout/Sidebar';

interface OverviewViewProps {
  summary: AnalyticsSummary | null;
  recentRecordings: RecordingRecord[];
  onNavigate: (tab: NavTab) => void;
  onSelectRecord: (record: RecordingRecord) => void;
  isLoading: boolean;
}

export const OverviewView: React.FC<OverviewViewProps> = ({
  summary,
  recentRecordings,
  onNavigate,
  onSelectRecord,
  isLoading,
}) => {
  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-r from-space-900 via-space-850 to-space-900 border border-space-700/80 p-6 sm:p-8 shadow-xl">
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-brand-purple/10 rounded-full blur-3xl pointer-events-none" />
        <div className="relative z-10 max-w-2xl space-y-4">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-brand-purple/10 border border-brand-purple/20 text-brand-purple text-xs font-semibold">
            <Zap className="w-3.5 h-3.5" />
            <span>AI Speech & Audio Intelligence</span>
          </div>

          <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight leading-tight">
            Your voice. Your intelligence. <br className="hidden sm:inline" />
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-brand-purple via-brand-indigo to-brand-cyan">
              Your studio.
            </span>
          </h1>

          <p className="text-sm text-slate-300 leading-relaxed">
            Zero-shot reference-conditioned neural voice cloning with Microsoft SpeechT5 and HiFi-GAN,
            combined with offline Faster-Whisper transcription, acoustic signal processing, and Tableau BI export.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <button
              onClick={() => onNavigate('studio')}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-brand-purple to-brand-indigo hover:from-brand-violet hover:to-brand-indigo text-white font-medium text-sm shadow-lg shadow-brand-purple/25 transition-all hover:scale-[1.02] active:scale-[0.98]"
            >
              <Mic2 className="w-4 h-4" />
              <span>Launch Voice Studio</span>
              <ArrowRight className="w-4 h-4" />
            </button>

            <button
              onClick={() => onNavigate('transcribe')}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-space-800 hover:bg-space-750 text-slate-200 text-sm font-medium border border-space-700 transition-colors"
            >
              <FileText className="w-4 h-4 text-brand-purple" />
              <span>Transcribe Audio</span>
            </button>
          </div>
        </div>
      </div>

      {/* KPI Stats Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Audio */}
        <div className="p-5 rounded-2xl bg-space-900 border border-space-750 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Processed Audio</span>
            <Clock className="w-4 h-4 text-brand-indigo" />
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {summary ? `${summary.total_audio_duration_minutes.toFixed(1)}m` : '0.0m'}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {summary ? `${summary.total_audio_duration_seconds.toFixed(0)} seconds total` : 'No audio logged'}
          </div>
        </div>

        {/* Total Operations */}
        <div className="p-5 rounded-2xl bg-space-900 border border-space-750 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Total Operations</span>
            <Activity className="w-4 h-4 text-brand-purple" />
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {summary ? summary.total_recordings : 0}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            {summary ? `${summary.successful_recordings} successful / ${summary.failed_recordings} failed` : 'Empty database'}
          </div>
        </div>

        {/* Success Rate */}
        <div className="p-5 rounded-2xl bg-space-900 border border-space-750 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Success Rate</span>
            <CheckCircle2 className="w-4 h-4 text-brand-emerald" />
          </div>
          <div className="text-2xl font-bold text-brand-emerald tracking-tight">
            {summary ? `${summary.success_rate_percent.toFixed(1)}%` : '100%'}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            Execution reliability
          </div>
        </div>

        {/* Speaking Pace */}
        <div className="p-5 rounded-2xl bg-space-900 border border-space-750 shadow-sm relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-medium">Avg Speaking Pace</span>
            <Volume2 className="w-4 h-4 text-brand-cyan" />
          </div>
          <div className="text-2xl font-bold text-white tracking-tight">
            {summary && summary.average_speaking_pace_wpm > 0 ? `${summary.average_speaking_pace_wpm} WPM` : '150 WPM'}
          </div>
          <div className="text-[11px] text-slate-400 mt-1">
            Words per minute normalized
          </div>
        </div>
      </div>

      {/* Quick Action Navigation Cards */}
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
          Quick Workspaces
        </h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div
            onClick={() => onNavigate('studio')}
            className="p-5 rounded-xl bg-space-900 hover:bg-space-850 border border-space-750 hover:border-brand-purple/40 cursor-pointer transition-all group"
          >
            <div className="p-3 rounded-lg bg-brand-purple/10 text-brand-purple w-fit mb-3 group-hover:scale-110 transition-transform">
              <Mic2 className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white group-hover:text-brand-purple transition-colors">
              Voice Studio
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Zero-shot speaker cloning from brief reference recordings.
            </p>
          </div>

          <div
            onClick={() => onNavigate('transcribe')}
            className="p-5 rounded-xl bg-space-900 hover:bg-space-850 border border-space-750 hover:border-brand-indigo/40 cursor-pointer transition-all group"
          >
            <div className="p-3 rounded-lg bg-brand-indigo/10 text-brand-indigo w-fit mb-3 group-hover:scale-110 transition-transform">
              <FileText className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white group-hover:text-brand-indigo transition-colors">
              Transcription
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Fast local speech-to-text with Faster-Whisper int8 on CPU.
            </p>
          </div>

          <div
            onClick={() => onNavigate('history')}
            className="p-5 rounded-xl bg-space-900 hover:bg-space-850 border border-space-750 hover:border-brand-cyan/40 cursor-pointer transition-all group"
          >
            <div className="p-3 rounded-lg bg-brand-cyan/10 text-brand-cyan w-fit mb-3 group-hover:scale-110 transition-transform">
              <History className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white group-hover:text-brand-cyan transition-colors">
              Audit History
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Search and inspect persisted audio operations and telemetry.
            </p>
          </div>

          <div
            onClick={() => onNavigate('analytics')}
            className="p-5 rounded-xl bg-space-900 hover:bg-space-850 border border-space-750 hover:border-brand-amber/40 cursor-pointer transition-all group"
          >
            <div className="p-3 rounded-lg bg-brand-amber/10 text-brand-amber w-fit mb-3 group-hover:scale-110 transition-transform">
              <BarChart3 className="w-5 h-5" />
            </div>
            <h4 className="text-sm font-bold text-white group-hover:text-brand-amber transition-colors">
              Analytics & Tableau
            </h4>
            <p className="text-xs text-slate-400 mt-1">
              Tableau CSV export pipeline, latency metrics, and distributions.
            </p>
          </div>
        </div>
      </div>

      {/* Recent Activity Table */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-400 uppercase tracking-wider">
            Recent Operational Activity
          </h3>
          <button
            onClick={() => onNavigate('history')}
            className="text-xs text-brand-purple hover:underline flex items-center gap-1 font-medium"
          >
            <span>View All Records</span>
            <ArrowRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="rounded-2xl border border-space-750 bg-space-900 overflow-hidden shadow-sm">
          {recentRecordings.length === 0 ? (
            <div className="p-8 text-center text-slate-400">
              <p className="text-sm">No operations recorded yet.</p>
              <p className="text-xs text-slate-500 mt-1">
                Synthesize voice or transcribe audio to generate records.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-space-850 text-slate-400 uppercase tracking-wider border-b border-space-750 text-[10px]">
                  <tr>
                    <th className="px-5 py-3 font-semibold">Timestamp</th>
                    <th className="px-5 py-3 font-semibold">Operation</th>
                    <th className="px-5 py-3 font-semibold">Source File</th>
                    <th className="px-5 py-3 font-semibold">Duration</th>
                    <th className="px-5 py-3 font-semibold">Status</th>
                    <th className="px-5 py-3 font-semibold">Latency</th>
                    <th className="px-5 py-3 font-semibold text-right">Details</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-space-750 text-slate-300">
                  {recentRecordings.slice(0, 5).map((rec) => (
                    <tr
                      key={rec.recording_id}
                      onClick={() => onSelectRecord(rec)}
                      className="hover:bg-space-800/50 cursor-pointer transition-colors"
                    >
                      <td className="px-5 py-3.5 font-mono text-[11px] text-slate-400">
                        {new Date(rec.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                      </td>
                      <td className="px-5 py-3.5 font-medium text-white capitalize">
                        {rec.operation_type.replace('_', ' ')}
                      </td>
                      <td className="px-5 py-3.5 max-w-[180px] truncate text-slate-300">
                        {rec.file_name}
                      </td>
                      <td className="px-5 py-3.5 text-slate-300">
                        {rec.duration_seconds.toFixed(1)}s
                      </td>
                      <td className="px-5 py-3.5">
                        <span
                          className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-medium ${
                            rec.processing_status === 'success'
                              ? 'bg-brand-emerald/10 text-brand-emerald border border-brand-emerald/20'
                              : 'bg-brand-rose/10 text-brand-rose border border-brand-rose/20'
                          }`}
                        >
                          {rec.processing_status}
                        </span>
                      </td>
                      <td className="px-5 py-3.5 text-slate-400">
                        {rec.processing_duration_ms.toFixed(0)} ms
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            onSelectRecord(rec);
                          }}
                          className="text-brand-purple hover:text-white font-medium hover:underline"
                        >
                          Inspect
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
