import React, { useState } from 'react';
import {
  FileText,
  Upload,
  Copy,
  Check,
  Globe,
  Gauge,
  Clock,
  Radio,
  RefreshCw,
  Sparkles,
  Database,
} from 'lucide-react';
import { SampleVoice, TranscriptionResult } from '../../types';
import { transcribeAudio } from '../../services/api';

interface TranscriptionViewProps {
  samples: SampleVoice[];
  onOperationSuccess: () => void;
  showToast: (type: 'success' | 'error' | 'info', title: string, message?: string) => void;
}

export const TranscriptionView: React.FC<TranscriptionViewProps> = ({
  samples,
  onOperationSuccess,
  showToast,
}) => {
  const [sourceType, setSourceType] = useState<'preset' | 'upload'>('preset');
  const [selectedSampleId, setSelectedSampleId] = useState<string>('sample_speaker_female');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  const [isTranscribing, setIsTranscribing] = useState(false);
  const [result, setResult] = useState<TranscriptionResult | null>(null);
  const [copied, setCopied] = useState(false);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setUploadedFile(file);
      showToast('info', 'Audio File Ready', `${file.name} (${(file.size / 1024).toFixed(0)} KB)`);
    }
  };

  const handleTranscribe = async () => {
    if (sourceType === 'upload' && !uploadedFile) {
      showToast('error', 'Audio Missing', 'Please select or upload an audio file to transcribe.');
      return;
    }

    setIsTranscribing(true);
    setResult(null);

    try {
      const res = await transcribeAudio(
        sourceType === 'upload' ? uploadedFile : null,
        sourceType === 'preset' ? selectedSampleId : null,
      );
      setResult(res);
      onOperationSuccess();
      showToast('success', 'Transcription Complete', `${res.word_count} words recognized at ${res.estimated_words_per_minute} WPM`);
    } catch (err: any) {
      showToast('error', 'Transcription Failed', err.message);
    } finally {
      setIsTranscribing(false);
    }
  };

  const handleCopyTranscript = () => {
    if (!result?.transcript) return;
    navigator.clipboard.writeText(result.transcript);
    setCopied(true);
    showToast('info', 'Copied to Clipboard', 'Transcript text copied.');
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* View Header */}
      <div className="p-6 rounded-2xl bg-space-900 border border-space-750 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-brand-indigo text-xs font-semibold uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4" />
            <span>Automatic Speech Recognition (ASR)</span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">Offline Speech Transcription & Pace Analysis</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Execute local CPU speech-to-text with Faster-Whisper int8 quantization. Generates linguistic transcripts, word counts, and speaking pace benchmarks.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Audio Ingestion */}
        <div className="lg:col-span-5 space-y-6">
          <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-5">
            <div className="flex items-center justify-between border-b border-space-750 pb-3">
              <h3 className="text-sm font-semibold text-white">Source Audio</h3>
              {/* Source Mode Toggle */}
              <div className="flex p-0.5 rounded-lg bg-space-800 border border-space-700 text-xs">
                <button
                  onClick={() => setSourceType('preset')}
                  className={`px-3 py-1 rounded-md font-medium transition-all ${
                    sourceType === 'preset' ? 'bg-brand-indigo text-white shadow-sm' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Presets
                </button>
                <button
                  onClick={() => setSourceType('upload')}
                  className={`px-3 py-1 rounded-md font-medium transition-all ${
                    sourceType === 'upload' ? 'bg-brand-indigo text-white shadow-sm' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Upload File
                </button>
              </div>
            </div>

            {sourceType === 'preset' ? (
              <div className="space-y-3">
                {samples.map((sample) => (
                  <div
                    key={sample.id}
                    onClick={() => setSelectedSampleId(sample.id)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      selectedSampleId === sample.id
                        ? 'bg-brand-indigo/10 border-brand-indigo text-white shadow-sm ring-1 ring-brand-indigo/30'
                        : 'bg-space-850/60 border-space-750 text-slate-300 hover:bg-space-800'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1.5">
                      <span className="font-semibold text-xs text-white">{sample.name}</span>
                      <Radio
                        className={`w-4 h-4 ${
                          selectedSampleId === sample.id ? 'text-brand-indigo' : 'text-slate-500'
                        }`}
                      />
                    </div>
                    <audio
                      controls
                      src={sample.audio_url}
                      className="w-full h-8 rounded opacity-80"
                      onClick={(e) => e.stopPropagation()}
                    />
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                <label className="border-2 border-dashed border-space-700 hover:border-brand-indigo/50 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition-all bg-space-850/40">
                  <Upload className="w-8 h-8 text-brand-indigo mb-2" />
                  <span className="text-sm font-medium text-slate-200">
                    {uploadedFile ? uploadedFile.name : 'Upload voice recording to transcribe'}
                  </span>
                  <span className="text-xs text-slate-400 mt-1">
                    Supports WAV, MP3, OGG, FLAC
                  </span>
                  <input
                    type="file"
                    accept="audio/*,.wav,.mp3,.ogg,.flac,.m4a"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
                {uploadedFile && (
                  <audio controls src={URL.createObjectURL(uploadedFile)} className="w-full h-8" />
                )}
              </div>
            )}

            {/* Run Button */}
            <button
              onClick={handleTranscribe}
              disabled={isTranscribing || (sourceType === 'upload' && !uploadedFile)}
              className="w-full flex items-center justify-center gap-2 py-3 px-5 rounded-xl bg-gradient-to-r from-brand-indigo to-brand-purple hover:from-brand-indigo hover:to-brand-violet text-white font-semibold text-sm shadow-lg shadow-brand-indigo/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.01] active:scale-[0.99]"
            >
              {isTranscribing ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Transcribing with Faster-Whisper...</span>
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  <span>Transcribe Audio</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Right Column: Transcript & Speech Metrics */}
        <div className="lg:col-span-7 space-y-6">
          <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-5">
            <div className="border-b border-space-750 pb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <FileText className="w-4 h-4 text-brand-indigo" />
                Speech-to-Text Results
              </h3>
              {result && (
                <button
                  onClick={handleCopyTranscript}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-space-800 hover:bg-space-750 text-xs font-medium text-slate-300 border border-space-700 transition-colors"
                >
                  {copied ? <Check className="w-3.5 h-3.5 text-brand-emerald" /> : <Copy className="w-3.5 h-3.5" />}
                  <span>{copied ? 'Copied' : 'Copy Text'}</span>
                </button>
              )}
            </div>

            {result ? (
              <div className="space-y-5 animate-in fade-in duration-300">
                {/* Transcript Box */}
                <div className="p-5 rounded-xl bg-space-850 border border-space-700 relative">
                  <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider block mb-2">
                    Linguistic Output
                  </span>
                  <p className="text-base text-slate-100 font-medium leading-relaxed select-text">
                    "{result.transcript}"
                  </p>
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                  <div className="p-3.5 rounded-xl bg-space-850 border border-space-750">
                    <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                      <Globe className="w-3.5 h-3.5 text-brand-indigo" />
                      <span>Language</span>
                    </div>
                    <div className="text-base font-bold text-white uppercase">
                      {result.detected_language}
                    </div>
                    <div className="text-[11px] text-emerald-400">
                      {(result.language_confidence * 100).toFixed(1)}% prob
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-space-850 border border-space-750">
                    <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                      <Gauge className="w-3.5 h-3.5 text-brand-cyan" />
                      <span>Speaking Pace</span>
                    </div>
                    <div className="text-base font-bold text-white">
                      {result.estimated_words_per_minute}
                    </div>
                    <div className="text-[11px] text-slate-400">
                      WPM pace
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-space-850 border border-space-750">
                    <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                      <FileText className="w-3.5 h-3.5 text-brand-purple" />
                      <span>Word Count</span>
                    </div>
                    <div className="text-base font-bold text-white">
                      {result.word_count}
                    </div>
                    <div className="text-[11px] text-slate-400">
                      {result.character_count} chars
                    </div>
                  </div>

                  <div className="p-3.5 rounded-xl bg-space-850 border border-space-750">
                    <div className="flex items-center gap-1.5 text-slate-400 text-xs mb-1">
                      <Clock className="w-3.5 h-3.5 text-brand-amber" />
                      <span>Latency</span>
                    </div>
                    <div className="text-base font-bold text-white">
                      {result.inference_duration_ms.toFixed(0)} ms
                    </div>
                    <div className="text-[11px] text-slate-400">
                      Faster-Whisper
                    </div>
                  </div>
                </div>

                {/* Database Persistence Confirmation */}
                <div className="p-3 rounded-xl bg-space-850 border border-space-750 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2 text-slate-400">
                    <Database className="w-4 h-4 text-brand-purple" />
                    <span>Persisted to SQLite (`vocalsense.db`)</span>
                  </div>
                  <code className="text-[11px] text-brand-purple font-mono">
                    {result.recording_id.slice(0, 13)}...
                  </code>
                </div>
              </div>
            ) : (
              <div className="py-20 text-center space-y-3 text-slate-400">
                <FileText className="w-12 h-12 text-slate-600 mx-auto" />
                <div>
                  <h4 className="text-sm font-semibold text-slate-300">No Transcript Generated Yet</h4>
                  <p className="text-xs text-slate-500 max-w-xs mx-auto mt-1">
                    Select an audio recording on the left and click Transcribe Audio to generate results.
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
