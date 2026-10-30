import React, { useState, useMemo } from 'react';
import {
  History,
  Search,
  Filter,
  RefreshCw,
  ChevronLeft,
  ChevronRight,
  Eye,
  CheckCircle2,
  AlertCircle,
  FileAudio,
  Mic2,
  FileText,
} from 'lucide-react';
import { RecordingRecord } from '../../types';

interface RecordingHistoryViewProps {
  recordings: RecordingRecord[];
  totalCount: number;
  onRefresh: () => void;
  onSelectRecord: (record: RecordingRecord) => void;
  isRefreshing: boolean;
}

export const RecordingHistoryView: React.FC<RecordingHistoryViewProps> = ({
  recordings,
  totalCount,
  onRefresh,
  onSelectRecord,
  isRefreshing,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [operationFilter, setOperationFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  // Client-side filtering over fetched records
  const filteredRecords = useMemo(() => {
    return recordings.filter((r) => {
      const matchesSearch =
        searchQuery === '' ||
        r.file_name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        r.recording_id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (r.transcript && r.transcript.toLowerCase().includes(searchQuery.toLowerCase()));

      const matchesOp =
        operationFilter === 'all' || r.operation_type === operationFilter;

      const matchesStatus =
        statusFilter === 'all' || r.processing_status === statusFilter;

      return matchesSearch && matchesOp && matchesStatus;
    });
  }, [recordings, searchQuery, operationFilter, statusFilter]);

  // Pagination
  const totalPages = Math.max(1, Math.ceil(filteredRecords.length / itemsPerPage));
  const paginatedRecords = useMemo(() => {
    const start = (currentPage - 1) * itemsPerPage;
    return filteredRecords.slice(start, start + itemsPerPage);
  }, [filteredRecords, currentPage]);

  return (
    <div className="space-y-6 animate-in fade-in duration-300">
      {/* Header Bar */}
      <div className="p-6 rounded-2xl bg-space-900 border border-space-750 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
            <History className="w-5 h-5 text-brand-purple" />
            Audit History & Operations Log
          </h2>
          <p className="text-xs text-slate-400 mt-1">
            Persisted recording records, timing benchmarks, and acoustic telemetry. Showing {filteredRecords.length} of {totalCount} total events.
          </p>
        </div>

        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-space-850 hover:bg-space-800 text-xs font-medium text-slate-300 border border-space-700 transition-colors disabled:opacity-50 self-start sm:self-auto"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-brand-purple' : ''}`} />
          <span>Refresh Database</span>
        </button>
      </div>

      {/* Filter and Search Controls */}
      <div className="flex flex-col md:flex-row gap-3 items-stretch md:items-center justify-between">
        {/* Search Input */}
        <div className="relative flex-1 max-w-md">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => {
              setSearchQuery(e.target.value);
              setCurrentPage(1);
            }}
            placeholder="Search by filename, UUID, or transcript..."
            className="w-full pl-10 pr-4 py-2 bg-space-900 border border-space-750 rounded-xl text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-purple transition-colors"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2.5">
          <select
            value={operationFilter}
            onChange={(e) => {
              setOperationFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="bg-space-900 border border-space-750 text-xs text-slate-300 rounded-xl px-3 py-2 focus:outline-none focus:border-brand-purple"
          >
            <option value="all">All Operations</option>
            <option value="voice_cloning">Voice Cloning</option>
            <option value="transcription">Transcription</option>
            <option value="acoustic_analysis">Acoustic Analysis</option>
          </select>

          <select
            value={statusFilter}
            onChange={(e) => {
              setStatusFilter(e.target.value);
              setCurrentPage(1);
            }}
            className="bg-space-900 border border-space-750 text-xs text-slate-300 rounded-xl px-3 py-2 focus:outline-none focus:border-brand-purple"
          >
            <option value="all">All Statuses</option>
            <option value="success">Success Only</option>
            <option value="failed">Failed Only</option>
          </select>

          {(searchQuery || operationFilter !== 'all' || statusFilter !== 'all') && (
            <button
              onClick={() => {
                setSearchQuery('');
                setOperationFilter('all');
                setStatusFilter('all');
                setCurrentPage(1);
              }}
              className="px-3 py-2 text-xs text-slate-400 hover:text-white transition-colors"
            >
              Clear Filters
            </button>
          )}
        </div>
      </div>

      {/* Main Table */}
      <div className="rounded-2xl border border-space-750 bg-space-900 overflow-hidden shadow-sm">
        {paginatedRecords.length === 0 ? (
          <div className="p-12 text-center space-y-2 text-slate-400">
            <History className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-sm font-medium text-slate-300">No matching recording records found.</p>
            <p className="text-xs text-slate-500">Try adjusting your search query or filter settings.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-space-850 text-slate-400 uppercase tracking-wider border-b border-space-750 text-[10px]">
                <tr>
                  <th className="px-5 py-3.5 font-semibold">Recording ID</th>
                  <th className="px-5 py-3.5 font-semibold">Timestamp</th>
                  <th className="px-5 py-3.5 font-semibold">Operation</th>
                  <th className="px-5 py-3.5 font-semibold">File Name</th>
                  <th className="px-5 py-3.5 font-semibold">Duration</th>
                  <th className="px-5 py-3.5 font-semibold">Words</th>
                  <th className="px-5 py-3.5 font-semibold">Status</th>
                  <th className="px-5 py-3.5 font-semibold">Latency</th>
                  <th className="px-5 py-3.5 font-semibold text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-space-750 text-slate-300">
                {paginatedRecords.map((rec) => (
                  <tr
                    key={rec.recording_id}
                    onClick={() => onSelectRecord(rec)}
                    className="hover:bg-space-800/60 cursor-pointer transition-colors group"
                  >
                    <td className="px-5 py-3.5 font-mono text-[11px] text-brand-purple">
                      {rec.recording_id.slice(0, 8)}...
                    </td>
                    <td className="px-5 py-3.5 text-slate-400 whitespace-nowrap">
                      {new Date(rec.created_at).toLocaleDateString([], { month: 'short', day: 'numeric' })}{' '}
                      <span className="text-[10px] text-slate-500">
                        {new Date(rec.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </td>
                    <td className="px-5 py-3.5">
                      <div className="flex items-center gap-1.5 font-medium text-white capitalize">
                        {rec.operation_type === 'voice_cloning' ? (
                          <Mic2 className="w-3.5 h-3.5 text-brand-purple" />
                        ) : (
                          <FileText className="w-3.5 h-3.5 text-brand-indigo" />
                        )}
                        <span>{rec.operation_type.replace('_', ' ')}</span>
                      </div>
                    </td>
                    <td className="px-5 py-3.5 max-w-[180px] truncate font-medium text-slate-200">
                      {rec.file_name}
                    </td>
                    <td className="px-5 py-3.5 text-slate-300">
                      {rec.duration_seconds.toFixed(1)}s
                    </td>
                    <td className="px-5 py-3.5 text-slate-400">
                      {rec.word_count ?? 0}
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
                    <td className="px-5 py-3.5 text-slate-400 font-mono">
                      {rec.processing_duration_ms.toFixed(0)} ms
                    </td>
                    <td className="px-5 py-3.5 text-right">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectRecord(rec);
                        }}
                        className="p-1.5 rounded-lg bg-space-800 group-hover:bg-brand-purple/20 text-slate-400 group-hover:text-brand-purple transition-colors"
                        title="View Full Metadata"
                      >
                        <Eye className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {/* Pagination Bar */}
        <div className="px-5 py-3.5 border-t border-space-750 flex items-center justify-between text-xs text-slate-400 bg-space-900">
          <span>
            Showing {Math.min(filteredRecords.length, (currentPage - 1) * itemsPerPage + 1)} to{' '}
            {Math.min(filteredRecords.length, currentPage * itemsPerPage)} of {filteredRecords.length} records
          </span>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded-lg bg-space-800 hover:bg-space-750 text-slate-300 disabled:opacity-40 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="px-2 text-xs font-medium text-slate-300">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded-lg bg-space-800 hover:bg-space-750 text-slate-300 disabled:opacity-40 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
