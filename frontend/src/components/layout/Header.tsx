import React from 'react';
import { Menu, RefreshCw, Database, Sparkles } from 'lucide-react';
import { NavTab } from './Sidebar';

interface HeaderProps {
  activeTab: NavTab;
  onOpenMobile: () => void;
  onRefresh: () => void;
  isRefreshing: boolean;
}

const TAB_METADATA: Record<NavTab, { title: string; subtitle: string }> = {
  overview: {
    title: 'Workspace Overview',
    subtitle: 'High-level operational metrics, quick studio actions, and telemetry.',
  },
  studio: {
    title: 'Voice Studio',
    subtitle: 'Zero-shot reference-conditioned neural speech synthesis via SpeechT5.',
  },
  transcribe: {
    title: 'Speech Transcription',
    subtitle: 'Offline speech-to-text with language detection and speaking pace via Faster-Whisper.',
  },
  history: {
    title: 'Recording History',
    subtitle: 'Audit log and telemetry records persisted in SQLite database.',
  },
  analytics: {
    title: 'Analytics & Tableau Integration',
    subtitle: 'Summary KPIs, duration distributions, and sanitized CSV dataset export.',
  },
  architecture: {
    title: 'System Architecture & Specs',
    subtitle: 'Deep learning pipeline specifications, model provenance, and local deployment.',
  },
};

export const Header: React.FC<HeaderProps> = ({
  activeTab,
  onOpenMobile,
  onRefresh,
  isRefreshing,
}) => {
  const meta = TAB_METADATA[activeTab];

  return (
    <header className="sticky top-0 z-30 bg-space-950/80 backdrop-blur-md border-b border-space-700/80 px-4 sm:px-8 py-4 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <button
          onClick={onOpenMobile}
          className="p-2 -ml-2 text-slate-400 hover:text-white rounded-xl hover:bg-space-800 lg:hidden"
        >
          <Menu className="w-5 h-5" />
        </button>
        <div>
          <h2 className="text-lg sm:text-xl font-bold text-white tracking-tight leading-tight">
            {meta.title}
          </h2>
          <p className="text-xs text-slate-400 hidden sm:block mt-0.5">{meta.subtitle}</p>
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        <div className="hidden md:flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-space-900 border border-space-700 text-xs text-slate-400">
          <Database className="w-3.5 h-3.5 text-brand-purple" />
          <span>SQLite WAL</span>
        </div>

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-space-850 hover:bg-space-800 text-xs font-medium text-slate-300 border border-space-700 transition-colors disabled:opacity-50"
          title="Refresh Data from Backend"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-brand-purple' : ''}`} />
          <span className="hidden sm:inline">Refresh</span>
        </button>
      </div>
    </header>
  );
};
