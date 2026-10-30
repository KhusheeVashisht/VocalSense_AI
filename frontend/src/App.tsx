import React, { useState, useEffect, useCallback } from 'react';
import { Sidebar, NavTab } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { OverviewView } from './components/views/OverviewView';
import { VoiceStudioView } from './components/views/VoiceStudioView';
import { TranscriptionView } from './components/views/TranscriptionView';
import { RecordingHistoryView } from './components/views/RecordingHistoryView';
import { AnalyticsView } from './components/views/AnalyticsView';
import { ArchitectureView } from './components/views/ArchitectureView';
import { RecordDetailModal } from './components/common/RecordDetailModal';
import { Toast, ToastMessage } from './components/common/Toast';
import {
  fetchHealth,
  fetchSamples,
  fetchRecordings,
  fetchAnalyticsSummary,
  fetchAnalyticsTimeseries,
} from './services/api';
import {
  SampleVoice,
  RecordingRecord,
  AnalyticsSummary,
  TimeseriesPoint,
} from './types';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<NavTab>('overview');
  const [isOnline, setIsOnline] = useState(true);
  const [isOpenMobile, setIsOpenMobile] = useState(false);
  const [isRefreshing, setIsRefreshing] = useState(false);

  // Application Data States
  const [samples, setSamples] = useState<SampleVoice[]>([]);
  const [recordings, setRecordings] = useState<RecordingRecord[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);
  const [timeseries, setTimeseries] = useState<TimeseriesPoint[]>([]);

  // Modal & Toast States
  const [selectedRecord, setSelectedRecord] = useState<RecordingRecord | null>(null);
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const showToast = useCallback(
    (type: 'success' | 'error' | 'info', title: string, message?: string) => {
      const id = Date.now().toString() + Math.random().toString(36).substring(2, 6);
      setToasts((prev) => [...prev, { id, type, title, message }]);
      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, 5000);
    },
    [],
  );

  const dismissToast = (id: string) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  // Load all data
  const loadAllData = useCallback(async () => {
    setIsRefreshing(true);
    try {
      const [healthRes, samplesRes, recsRes, summaryRes, tsRes] = await Promise.all([
        fetchHealth().catch(() => ({ status: 'down' })),
        fetchSamples().catch(() => []),
        fetchRecordings({ limit: 100 }).catch(() => ({ total: 0, limit: 100, offset: 0, records: [] })),
        fetchAnalyticsSummary().catch(() => null),
        fetchAnalyticsTimeseries().catch(() => ({ timeseries: [] })),
      ]);

      setIsOnline(healthRes.status === 'healthy');
      setSamples(samplesRes as SampleVoice[]);
      setRecordings(recsRes.records);
      setTotalCount(recsRes.total);
      setSummary(summaryRes);
      setTimeseries(tsRes.timeseries);
    } catch (err: any) {
      console.error('Error refreshing VocalSense AI data:', err);
    } finally {
      setIsRefreshing(false);
    }
  }, []);

  // Polling on mount
  useEffect(() => {
    loadAllData();
    const interval = setInterval(() => {
      fetchHealth()
        .then((h) => setIsOnline(h.status === 'healthy'))
        .catch(() => setIsOnline(false));
    }, 20000);
    return () => clearInterval(interval);
  }, [loadAllData]);

  return (
    <div className="min-h-screen bg-space-950 text-slate-100 flex">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        isOnline={isOnline}
        isOpenMobile={isOpenMobile}
        onCloseMobile={() => setIsOpenMobile(false)}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 lg:pl-72">
        <Header
          activeTab={activeTab}
          onOpenMobile={() => setIsOpenMobile(true)}
          onRefresh={loadAllData}
          isRefreshing={isRefreshing}
        />

        <main className="flex-1 p-4 sm:p-8 max-w-7xl w-full mx-auto">
          {activeTab === 'overview' && (
            <OverviewView
              summary={summary}
              recentRecordings={recordings}
              onNavigate={setActiveTab}
              onSelectRecord={setSelectedRecord}
              isLoading={isRefreshing}
            />
          )}

          {activeTab === 'studio' && (
            <VoiceStudioView
              samples={samples}
              onOperationSuccess={loadAllData}
              showToast={showToast}
            />
          )}

          {activeTab === 'transcribe' && (
            <TranscriptionView
              samples={samples}
              onOperationSuccess={loadAllData}
              showToast={showToast}
            />
          )}

          {activeTab === 'history' && (
            <RecordingHistoryView
              recordings={recordings}
              totalCount={totalCount}
              onRefresh={loadAllData}
              onSelectRecord={setSelectedRecord}
              isRefreshing={isRefreshing}
            />
          )}

          {activeTab === 'analytics' && (
            <AnalyticsView
              summary={summary}
              timeseries={timeseries}
              showToast={showToast}
            />
          )}

          {activeTab === 'architecture' && <ArchitectureView />}
        </main>
      </div>

      {/* Record Details Slide-over / Modal */}
      <RecordDetailModal
        record={selectedRecord}
        onClose={() => setSelectedRecord(null)}
        onCopySuccess={() => showToast('info', 'ID Copied', 'Recording UUID copied to clipboard.')}
      />

      {/* Toast Notification Container */}
      <Toast toasts={toasts} onDismiss={dismissToast} />
    </div>
  );
};

export default App;
