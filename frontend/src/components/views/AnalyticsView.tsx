import React from 'react';
import {
  BarChart3,
  Download,
  Clock,
  CheckCircle2,
  TrendingUp,
  FileSpreadsheet,
  Layers,
  Sparkles,
  ExternalLink,
  ShieldCheck,
} from 'lucide-react';
import { AnalyticsSummary, TimeseriesPoint } from '../../types';
import { getExportUrl } from '../../services/api';

interface AnalyticsViewProps {
  summary: AnalyticsSummary | null;
  timeseries: TimeseriesPoint[];
  showToast: (type: 'success' | 'error' | 'info', title: string, message?: string) => void;
}

export const AnalyticsView: React.FC<AnalyticsViewProps> = ({
  summary,
  timeseries,
  showToast,
}) => {
  const exportUrl = getExportUrl();

  const handleExportClick = () => {
    showToast('info', 'Tableau CSV Download Started', 'Exporting sanitized 15-column dataset.');
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* View Header */}
      <div className="p-6 rounded-2xl bg-space-900 border border-space-750 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-brand-purple text-xs font-semibold uppercase tracking-wider mb-1">
            <BarChart3 className="w-4 h-4" />
            <span>Business Intelligence & MLOps</span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">Performance Analytics & Tableau Export</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Real-time aggregate telemetry computed over SQLite persistence records. Formatted for instant ingestion by Tableau Desktop and Tableau Public.
          </p>
        </div>

        <a
          href={exportUrl}
          onClick={handleExportClick}
          download="vocalsense_analytics_export.csv"
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl bg-gradient-to-r from-brand-purple to-brand-indigo hover:from-brand-violet hover:to-brand-indigo text-white font-medium text-xs shadow-lg shadow-brand-purple/20 transition-all self-start md:self-auto shrink-0"
        >
          <Download className="w-4 h-4" />
          <span>Export Tableau CSV</span>
        </a>
      </div>

      {/* KPI Summary Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-space-900 border border-space-750">
          <div className="text-xs text-slate-400 flex items-center justify-between mb-1.5">
            <span>Audio Volume</span>
            <Clock className="w-4 h-4 text-brand-purple" />
          </div>
          <div className="text-2xl font-bold text-white">
            {summary ? `${summary.total_audio_duration_minutes.toFixed(2)} min` : '0 min'}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            {summary ? `${summary.total_audio_duration_seconds.toFixed(0)} total seconds` : 'No audio logged'}
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-space-900 border border-space-750">
          <div className="text-xs text-slate-400 flex items-center justify-between mb-1.5">
            <span>Words Processed</span>
            <TrendingUp className="w-4 h-4 text-brand-cyan" />
          </div>
          <div className="text-2xl font-bold text-white">
            {summary ? summary.total_words_processed.toLocaleString() : '0'}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Across synthesis & transcription
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-space-900 border border-space-750">
          <div className="text-xs text-slate-400 flex items-center justify-between mb-1.5">
            <span>Average Latency</span>
            <Clock className="w-4 h-4 text-brand-amber" />
          </div>
          <div className="text-2xl font-bold text-white">
            {summary ? `${(summary.average_processing_duration_ms / 1000).toFixed(2)}s` : '0s'}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            Real-Time Factor: {summary ? `${summary.average_real_time_factor.toFixed(2)}x` : '1.0x'}
          </p>
        </div>

        <div className="p-5 rounded-2xl bg-space-900 border border-space-750">
          <div className="text-xs text-slate-400 flex items-center justify-between mb-1.5">
            <span>Overall Success Rate</span>
            <CheckCircle2 className="w-4 h-4 text-brand-emerald" />
          </div>
          <div className="text-2xl font-bold text-brand-emerald">
            {summary ? `${summary.success_rate_percent.toFixed(1)}%` : '100%'}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">
            {summary ? `${summary.successful_recordings} of ${summary.total_recordings} jobs` : '0 jobs'}
          </p>
        </div>
      </div>

      {/* Visual Distributions & Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Operations Breakdown Bar */}
        <div className="lg:col-span-6 p-6 rounded-2xl bg-space-900 border border-space-750 space-y-4">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <Layers className="w-4 h-4 text-brand-purple" />
            Operations Volume Distribution
          </h3>
          <div className="space-y-3 pt-2">
            {summary && Object.keys(summary.operations_breakdown).length > 0 ? (
              Object.entries(summary.operations_breakdown).map(([op, count]) => {
                const total = summary.total_recordings || 1;
                const pct = Math.round((count / total) * 100);
                return (
                  <div key={op} className="space-y-1.5">
                    <div className="flex justify-between text-xs">
                      <span className="font-medium text-slate-200 capitalize">{op.replace('_', ' ')}</span>
                      <span className="text-slate-400">{count} events ({pct}%)</span>
                    </div>
                    <div className="w-full h-2.5 rounded-full bg-space-800 overflow-hidden">
                      <div
                        className="h-full bg-gradient-to-r from-brand-purple to-brand-indigo rounded-full transition-all"
                        style={{ width: `${pct}%` }}
                      />
                    </div>
                  </div>
                );
              })
            ) : (
              <p className="text-xs text-slate-500 py-6 text-center">No operations recorded yet.</p>
            )}
          </div>
        </div>

        {/* Daily Timeseries Trend */}
        <div className="lg:col-span-6 p-6 rounded-2xl bg-space-900 border border-space-750 space-y-4">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <TrendingUp className="w-4 h-4 text-brand-cyan" />
            Daily Activity & Throughput Log
          </h3>
          {timeseries.length === 0 ? (
            <p className="text-xs text-slate-500 py-6 text-center">No daily activity logged yet.</p>
          ) : (
            <div className="space-y-3 pt-2">
              {timeseries.slice(-5).map((point) => (
                <div
                  key={point.date}
                  className="flex items-center justify-between p-3 rounded-xl bg-space-850 border border-space-750 text-xs"
                >
                  <div>
                    <span className="font-semibold text-white block">{point.date}</span>
                    <span className="text-[11px] text-slate-400">
                      Duration: {(point.total_duration_sec / 60).toFixed(1)} mins
                    </span>
                  </div>
                  <div className="text-right">
                    <span className="font-bold text-brand-purple block">{point.count} operations</span>
                    <span className="text-[11px] text-slate-400">
                      Avg: {point.avg_processing_ms.toFixed(0)} ms
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>

      {/* Tableau Export & Security Section */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-space-900 to-space-850 border border-space-750 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-space-750 pb-4">
          <div className="flex items-center gap-3">
            <div className="p-3 rounded-xl bg-brand-amber/10 text-brand-amber border border-brand-amber/20">
              <FileSpreadsheet className="w-6 h-6" />
            </div>
            <div>
              <h3 className="text-base font-bold text-white">Tableau Data Pipeline Specification</h3>
              <p className="text-xs text-slate-400">15 Standard Dimensions & Measures (UTF-8 with BOM)</p>
            </div>
          </div>

          <a
            href={exportUrl}
            onClick={handleExportClick}
            download="vocalsense_analytics_export.csv"
            className="flex items-center gap-2 px-4 py-2 rounded-xl bg-brand-amber hover:bg-amber-500 text-space-950 font-semibold text-xs transition-colors shrink-0"
          >
            <Download className="w-4 h-4" />
            <span>Download CSV for Tableau</span>
          </a>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-1">
          <div className="p-3.5 rounded-xl bg-space-800/60 border border-space-750 text-xs space-y-1">
            <div className="flex items-center gap-1.5 font-semibold text-slate-200">
              <ShieldCheck className="w-4 h-4 text-brand-emerald" />
              <span>Anti-CSV Injection</span>
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Formulas beginning with =, +, -, @ are escaped with single-quotes (') to protect against spreadsheet formula execution.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-space-800/60 border border-space-750 text-xs space-y-1">
            <div className="flex items-center gap-1.5 font-semibold text-slate-200">
              <ShieldCheck className="w-4 h-4 text-brand-emerald" />
              <span>Zero-PII Privacy Protection</span>
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              Full sentence transcripts, audio waveforms, and raw binary buffers are strictly excluded from export.
            </p>
          </div>

          <div className="p-3.5 rounded-xl bg-space-800/60 border border-space-750 text-xs space-y-1">
            <div className="flex items-center gap-1.5 font-semibold text-slate-200">
              <FileSpreadsheet className="w-4 h-4 text-brand-purple" />
              <span>Tableau Dashboards Ready</span>
            </div>
            <p className="text-slate-400 text-[11px] leading-relaxed">
              See TABLEAU_GUIDE.md for formulas for Speech Activity, Acoustic Analysis, and MLOps dashboards.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
