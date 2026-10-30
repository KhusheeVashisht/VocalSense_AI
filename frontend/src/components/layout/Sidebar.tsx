import React from 'react';
import {
  LayoutDashboard,
  Mic2,
  FileText,
  History,
  BarChart3,
  Cpu,
  ExternalLink,
  AudioWaveform,
  CheckCircle2,
  AlertCircle,
  X,
} from 'lucide-react';

export type NavTab = 'overview' | 'studio' | 'transcribe' | 'history' | 'analytics' | 'architecture';

interface SidebarProps {
  activeTab: NavTab;
  onTabChange: (tab: NavTab) => void;
  isOnline: boolean;
  isOpenMobile: boolean;
  onCloseMobile: () => void;
}

export const Sidebar: React.FC<SidebarProps> = ({
  activeTab,
  onTabChange,
  isOnline,
  isOpenMobile,
  onCloseMobile,
}) => {
  const navItems = [
    { id: 'overview' as NavTab, label: 'Overview', icon: LayoutDashboard, desc: 'Activity & Quick Actions' },
    { id: 'studio' as NavTab, label: 'Voice Studio', icon: Mic2, desc: 'Zero-Shot Speech Synthesis' },
    { id: 'transcribe' as NavTab, label: 'Transcription', icon: FileText, desc: 'Offline Faster-Whisper ASR' },
    { id: 'history' as NavTab, label: 'Recording History', icon: History, desc: 'Database Logs & Telemetry' },
    { id: 'analytics' as NavTab, label: 'Analytics & Tableau', icon: BarChart3, desc: 'KPIs & Export Pipeline' },
    { id: 'architecture' as NavTab, label: 'Architecture', icon: Cpu, desc: 'Model Specs & Pipelines' },
  ];

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpenMobile && (
        <div
          className="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm lg:hidden"
          onClick={onCloseMobile}
        />
      )}

      {/* Sidebar Container */}
      <aside
        className={`fixed top-0 left-0 bottom-0 z-40 w-72 bg-space-900 border-r border-space-700/80 flex flex-col transition-transform duration-300 ease-in-out lg:translate-x-0 ${
          isOpenMobile ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        {/* Brand Header */}
        <div className="p-5 border-b border-space-700/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-gradient-to-br from-brand-purple to-brand-indigo text-white shadow-lg shadow-brand-purple/20">
              <AudioWaveform className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <h1 className="text-base font-bold text-white tracking-tight">VocalSense</h1>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-brand-purple/20 text-brand-purple border border-brand-purple/30">
                  AI
                </span>
              </div>
              <p className="text-[11px] text-slate-400">Audio Workspace</p>
            </div>
          </div>
          <button
            onClick={onCloseMobile}
            className="p-1.5 text-slate-400 hover:text-white lg:hidden rounded-lg hover:bg-space-800"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Nav Items */}
        <div className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
          <div className="px-3 pb-2 text-[10px] uppercase tracking-wider font-semibold text-slate-500">
            Workspaces
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  onTabChange(item.id);
                  onCloseMobile();
                }}
                className={`w-full flex items-center gap-3 px-3.5 py-3 rounded-xl text-left transition-all group ${
                  isActive
                    ? 'bg-gradient-to-r from-brand-purple/20 to-brand-indigo/10 border border-brand-purple/40 text-white font-medium shadow-sm'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-space-800/60 border border-transparent'
                }`}
              >
                <Icon
                  className={`w-5 h-5 transition-colors ${
                    isActive ? 'text-brand-purple' : 'text-slate-400 group-hover:text-slate-200'
                  }`}
                />
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium leading-none">{item.label}</div>
                  <div className="text-[11px] text-slate-400 mt-1 truncate">{item.desc}</div>
                </div>
              </button>
            );
          })}
        </div>

        {/* Footer / System Status & Fallback */}
        <div className="p-4 border-t border-space-700/80 bg-space-950/40 space-y-3">
          {/* Service Status Badge */}
          <div className="flex items-center justify-between px-3 py-2 rounded-xl bg-space-850 border border-space-700 text-xs">
            <span className="text-slate-400">Local Engine</span>
            <div className="flex items-center gap-1.5">
              {isOnline ? (
                <>
                  <span className="w-2 h-2 rounded-full bg-brand-emerald animate-pulse" />
                  <span className="text-emerald-400 font-medium">Ready (CPU)</span>
                </>
              ) : (
                <>
                  <span className="w-2 h-2 rounded-full bg-brand-rose" />
                  <span className="text-rose-400 font-medium">Offline</span>
                </>
              )}
            </div>
          </div>

          {/* Gradio Fallback Link */}
          <a
            href="/gradio"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center justify-between w-full px-3 py-2 rounded-xl bg-space-800 hover:bg-space-750 text-xs text-slate-300 border border-space-700 transition-colors group"
            title="Open original Gradio interface fallback"
          >
            <span className="text-slate-400 group-hover:text-slate-200">Gradio Classic UI</span>
            <ExternalLink className="w-3.5 h-3.5 text-slate-400 group-hover:text-brand-purple" />
          </a>
        </div>
      </aside>
    </>
  );
};
