import React, { useState } from 'react';
import {
  Mic2,
  Upload,
  Play,
  Download,
  Activity,
  Sparkles,
  Volume2,
  Layers,
  CheckCircle2,
  AlertCircle,
  FileAudio,
  Radio,
  RefreshCw,
} from 'lucide-react';
import { SampleVoice, CloneResult, InspectResult } from '../../types';
import { cloneVoice, inspectAudioFile } from '../../services/api';

interface VoiceStudioViewProps {
  samples: SampleVoice[];
  onOperationSuccess: () => void;
  showToast: (type: 'success' | 'error' | 'info', title: string, message?: string) => void;
}

const PRESET_SENTENCES = [
  'Welcome to VocalSense AI. Your personalized voice cloning system is active.',
  'Artificial intelligence and deep learning allow zero-shot voice synthesis from brief reference recordings.',
  'The quick brown fox jumps over the lazy dog near the quiet riverbank.',
  'Dr. Smith explained that acoustic measurements alone cannot legally establish biometric identity.',
];

export const VoiceStudioView: React.FC<VoiceStudioViewProps> = ({
  samples,
  onOperationSuccess,
  showToast,
}) => {
  // Reference voice state
  const [sourceType, setSourceType] = useState<'preset' | 'upload'>('preset');
  const [selectedSampleId, setSelectedSampleId] = useState<string>('sample_speaker_male');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);

  // Text state
  const [inputText, setInputText] = useState<string>(PRESET_SENTENCES[0]);

  // Inspection state
  const [isInspecting, setIsInspecting] = useState(false);
  const [inspectResult, setInspectResult] = useState<InspectResult | null>(null);

  // Synthesis state
  const [isCloning, setIsCloning] = useState(false);
  const [cloneResult, setCloneResult] = useState<CloneResult | null>(null);

  // File drop handler
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setUploadedFile(file);
      setInspectResult(null);
      showToast('info', 'Audio File Selected', `${file.name} (${(file.size / 1024).toFixed(0)} KB)`);
    }
  };

  // Inspect acoustic properties
  const handleInspect = async () => {
    setIsInspecting(true);
    try {
      const res = await inspectAudioFile(
        sourceType === 'upload' ? uploadedFile : null,
        sourceType === 'preset' ? selectedSampleId : undefined,
      );
      setInspectResult(res);
      showToast('success', 'Acoustic Analysis Complete', `Pitch: ${res.mean_pitch_hz} Hz, Duration: ${res.duration_seconds}s`);
    } catch (err: any) {
      showToast('error', 'Inspection Failed', err.message);
    } finally {
      setIsInspecting(false);
    }
  };

  // Run Voice Cloning
  const handleClone = async () => {
    if (!inputText.trim()) {
      showToast('error', 'Text Required', 'Please enter text to synthesize.');
      return;
    }
    if (sourceType === 'upload' && !uploadedFile) {
      showToast('error', 'Audio Required', 'Please upload a reference audio file.');
      return;
    }

    setIsCloning(true);
    setCloneResult(null);

    try {
      const res = await cloneVoice(
        sourceType === 'upload' ? uploadedFile : null,
        sourceType === 'preset' ? selectedSampleId : null,
        inputText,
        'en',
      );
      setCloneResult(res);
      onOperationSuccess();
      showToast('success', 'Speech Synthesized Successfully', `Similarity: ${res.speaker_embedding_similarity.toFixed(3)} (${res.similarity_interpretation})`);
    } catch (err: any) {
      showToast('error', 'Synthesis Failed', err.message);
    } finally {
      setIsCloning(false);
    }
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Studio Header */}
      <div className="p-6 rounded-2xl bg-space-900 border border-space-750 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-brand-purple text-xs font-semibold uppercase tracking-wider mb-1">
            <Sparkles className="w-4 h-4" />
            <span>Zero-Shot Acoustic Workspace</span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">Voice Cloning & Speech Synthesis</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Condition Microsoft SpeechT5 transformer synthesis with deep 512-dim x-vectors extracted from reference audio by SpeechBrain.
          </p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Reference Voice & Text Input */}
        <div className="lg:col-span-7 space-y-6">
          {/* Step 1: Reference Audio Selection */}
          <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-5">
            <div className="flex items-center justify-between border-b border-space-750 pb-3">
              <div className="flex items-center gap-2.5">
                <span className="w-6 h-6 rounded-full bg-brand-purple/20 text-brand-purple text-xs font-bold flex items-center justify-center">
                  1
                </span>
                <h3 className="text-sm font-semibold text-white">Reference Speaker Audio</h3>
              </div>

              {/* Source Switcher */}
              <div className="flex p-0.5 rounded-lg bg-space-800 border border-space-700 text-xs">
                <button
                  onClick={() => setSourceType('preset')}
                  className={`px-3 py-1 rounded-md font-medium transition-all ${
                    sourceType === 'preset' ? 'bg-brand-purple text-white shadow-sm' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Authorized Samples
                </button>
                <button
                  onClick={() => setSourceType('upload')}
                  className={`px-3 py-1 rounded-md font-medium transition-all ${
                    sourceType === 'upload' ? 'bg-brand-purple text-white shadow-sm' : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Upload Custom
                </button>
              </div>
            </div>

            {sourceType === 'preset' ? (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {samples.map((sample) => (
                  <div
                    key={sample.id}
                    onClick={() => setSelectedSampleId(sample.id)}
                    className={`p-4 rounded-xl border cursor-pointer transition-all ${
                      selectedSampleId === sample.id
                        ? 'bg-brand-purple/10 border-brand-purple text-white shadow-sm ring-1 ring-brand-purple/30'
                        : 'bg-space-850/60 border-space-750 text-slate-300 hover:bg-space-800'
                    }`}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-semibold text-xs text-white">{sample.name}</span>
                      <Radio
                        className={`w-4 h-4 ${
                          selectedSampleId === sample.id ? 'text-brand-purple' : 'text-slate-500'
                        }`}
                      />
                    </div>
                    <p className="text-[11px] text-slate-400 mb-2">{sample.gender_tone}</p>
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
                <label className="border-2 border-dashed border-space-700 hover:border-brand-purple/50 rounded-xl p-6 flex flex-col items-center justify-center cursor-pointer transition-all bg-space-850/40">
                  <Upload className="w-8 h-8 text-brand-purple mb-2" />
                  <span className="text-sm font-medium text-slate-200">
                    {uploadedFile ? uploadedFile.name : 'Click or drag reference audio here'}
                  </span>
                  <span className="text-xs text-slate-400 mt-1">
                    Supports WAV, MP3, OGG, FLAC (Recommended: 3–10s clean speech)
                  </span>
                  <input
                    type="file"
                    accept="audio/*,.wav,.mp3,.ogg,.flac,.m4a"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </label>
                {uploadedFile && (
                  <div className="p-3 bg-space-800 rounded-xl border border-space-700 flex items-center justify-between">
                    <span className="text-xs text-slate-300 truncate max-w-xs">{uploadedFile.name}</span>
                    <audio controls src={URL.createObjectURL(uploadedFile)} className="h-8 max-w-[200px]" />
                  </div>
                )}
              </div>
            )}

            {/* Acoustic Inspection Action */}
            <div className="flex items-center justify-between pt-2">
              <button
                type="button"
                onClick={handleInspect}
                disabled={isInspecting || (sourceType === 'upload' && !uploadedFile)}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-space-800 hover:bg-space-750 text-xs font-medium text-slate-300 border border-space-700 transition-colors disabled:opacity-50"
              >
                <Activity className={`w-3.5 h-3.5 ${isInspecting ? 'animate-spin text-brand-purple' : 'text-brand-purple'}`} />
                <span>{isInspecting ? 'Analyzing Signal...' : 'Inspect Acoustic Properties'}</span>
              </button>

              <span className="text-[11px] text-slate-400">
                16 kHz mono normalized
              </span>
            </div>

            {/* Inspection Results Box */}
            {inspectResult && (
              <div className="p-4 rounded-xl bg-space-850 border border-space-750 space-y-3 animate-in fade-in">
                <div className="text-xs font-semibold text-slate-300 flex items-center justify-between">
                  <span>Acoustic Profile: {inspectResult.file_name}</span>
                  <span className="text-[11px] text-brand-purple">{inspectResult.duration_seconds}s</span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs">
                  <div className="p-2 rounded bg-space-900 border border-space-750">
                    <span className="text-slate-400 block text-[10px]">Pitch (F0)</span>
                    <span className="font-semibold text-white">{inspectResult.mean_pitch_hz} Hz</span>
                  </div>
                  <div className="p-2 rounded bg-space-900 border border-space-750">
                    <span className="text-slate-400 block text-[10px]">RMS Energy</span>
                    <span className="font-semibold text-white">{inspectResult.mean_rms_energy.toFixed(4)}</span>
                  </div>
                  <div className="p-2 rounded bg-space-900 border border-space-750">
                    <span className="text-slate-400 block text-[10px]">Brightness</span>
                    <span className="font-semibold text-white">{inspectResult.spectral_centroid_hz.toFixed(0)} Hz</span>
                  </div>
                </div>
                {inspectResult.plot_url && (
                  <img
                    src={inspectResult.plot_url}
                    alt="Acoustic Report"
                    className="w-full rounded-lg border border-space-750 mt-2"
                  />
                )}
              </div>
            )}
          </div>

          {/* Step 2: Text to Synthesise */}
          <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-4">
            <div className="flex items-center justify-between border-b border-space-750 pb-3">
              <div className="flex items-center gap-2.5">
                <span className="w-6 h-6 rounded-full bg-brand-purple/20 text-brand-purple text-xs font-bold flex items-center justify-center">
                  2
                </span>
                <h3 className="text-sm font-semibold text-white">Target Speech Text</h3>
              </div>

              {/* Template Sentence Selector */}
              <select
                onChange={(e) => setInputText(e.target.value)}
                className="bg-space-800 border border-space-700 text-xs rounded-lg px-2.5 py-1 text-slate-300 focus:outline-none focus:border-brand-purple"
              >
                <option value="">Preset Templates...</option>
                {PRESET_SENTENCES.map((s, idx) => (
                  <option key={idx} value={s}>
                    Template {idx + 1}: {s.slice(0, 32)}...
                  </option>
                ))}
              </select>
            </div>

            <div>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                rows={3}
                placeholder="Enter text to synthesize in reference speaker timbre..."
                className="w-full bg-space-850 border border-space-700 rounded-xl p-3.5 text-sm text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-purple focus:ring-1 focus:ring-brand-purple transition-all resize-none"
              />
              <div className="flex items-center justify-between text-[11px] text-slate-400 mt-1.5 px-1">
                <span>Normalization: Abbreviations & currency expanded automatically</span>
                <span>{inputText.length} characters</span>
              </div>
            </div>

            {/* Synthesize Button */}
            <button
              onClick={handleClone}
              disabled={isCloning || !inputText.trim()}
              className="w-full flex items-center justify-center gap-2 py-3.5 px-6 rounded-xl bg-gradient-to-r from-brand-purple to-brand-indigo hover:from-brand-violet hover:to-brand-indigo text-white font-semibold text-sm shadow-lg shadow-brand-purple/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed hover:scale-[1.01] active:scale-[0.99]"
            >
              {isCloning ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Synthesizing Voice on Local CPU (SpeechT5)...</span>
                </>
              ) : (
                <>
                  <Mic2 className="w-4 h-4" />
                  <span>Generate Cloned Speech</span>
                </>
              )}
            </button>

            {isCloning && (
              <p className="text-center text-xs text-brand-purple/90 animate-pulse">
                Extracting x-vector embedding, decoding mel-spectrogram, and synthesizing with HiFi-GAN...
              </p>
            )}
          </div>
        </div>

        {/* Right Column: Output & Evaluation */}
        <div className="lg:col-span-5 space-y-6">
          <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-5 sticky top-24">
            <div className="border-b border-space-750 pb-3 flex items-center justify-between">
              <h3 className="text-sm font-semibold text-white flex items-center gap-2">
                <Volume2 className="w-4 h-4 text-brand-purple" />
                Synthesized Speech Output
              </h3>
              {cloneResult && (
                <span className="px-2 py-0.5 rounded-full bg-brand-emerald/10 text-brand-emerald border border-brand-emerald/20 text-[10px] font-semibold">
                  Complete
                </span>
              )}
            </div>

            {cloneResult ? (
              <div className="space-y-5 animate-in fade-in duration-300">
                {/* Audio Player Card */}
                <div className="p-4 rounded-xl bg-space-850 border border-space-700 space-y-3">
                  <div className="flex items-center justify-between text-xs text-slate-300">
                    <span className="font-semibold text-white truncate max-w-[200px]">{cloneResult.file_name}</span>
                    <span className="text-brand-purple font-mono">{cloneResult.duration_seconds}s</span>
                  </div>
                  <audio controls src={cloneResult.audio_url} autoPlay className="w-full rounded" />
                  <div className="flex items-center justify-between pt-1">
                    <span className="text-[11px] text-slate-400">
                      Inference: {cloneResult.synthesis_time_sec}s ({cloneResult.real_time_factor}x RTF)
                    </span>
                    <a
                      href={cloneResult.audio_url}
                      download={cloneResult.file_name}
                      className="flex items-center gap-1 text-xs text-brand-purple hover:underline font-medium"
                    >
                      <Download className="w-3.5 h-3.5" />
                      Download WAV
                    </a>
                  </div>
                </div>

                {/* Speaker Resemblance Gauge */}
                <div className="p-4 rounded-xl bg-space-850 border border-space-700 space-y-2">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-400">Speaker Embedding Cosine Similarity</span>
                    <span className="font-bold text-white text-sm">
                      {cloneResult.speaker_embedding_similarity.toFixed(4)}
                    </span>
                  </div>
                  <div className="w-full bg-space-800 h-2.5 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-brand-indigo to-brand-purple rounded-full"
                      style={{
                        width: `${Math.min(100, Math.max(0, cloneResult.speaker_embedding_similarity * 100))}%`,
                      }}
                    />
                  </div>
                  <p className="text-[11px] text-emerald-400 font-medium">
                    {cloneResult.similarity_interpretation}
                  </p>
                </div>

                {/* Comparative Acoustic Table */}
                <div className="space-y-2">
                  <h4 className="text-xs uppercase font-semibold text-slate-400 tracking-wider">
                    Comparative Acoustic Verification
                  </h4>
                  <div className="rounded-xl border border-space-750 overflow-hidden text-xs">
                    <table className="w-full text-left">
                      <thead className="bg-space-800 text-slate-400 text-[10px] uppercase">
                        <tr>
                          <th className="px-3 py-2 font-medium">Metric</th>
                          <th className="px-3 py-2 font-medium">Reference</th>
                          <th className="px-3 py-2 font-medium">Generated</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-space-750 text-slate-300">
                        <tr>
                          <td className="px-3 py-2 text-slate-400">Pitch (F0)</td>
                          <td className="px-3 py-2">{cloneResult.comparison.reference_pitch_hz} Hz</td>
                          <td className="px-3 py-2 font-medium text-white">{cloneResult.comparison.generated_pitch_hz} Hz</td>
                        </tr>
                        <tr>
                          <td className="px-3 py-2 text-slate-400">RMS Energy</td>
                          <td className="px-3 py-2">{cloneResult.comparison.reference_energy_rms.toFixed(3)}</td>
                          <td className="px-3 py-2 font-medium text-white">{cloneResult.comparison.generated_energy_rms.toFixed(3)}</td>
                        </tr>
                        <tr>
                          <td className="px-3 py-2 text-slate-400">Brightness</td>
                          <td className="px-3 py-2">{cloneResult.comparison.reference_centroid_hz.toFixed(0)} Hz</td>
                          <td className="px-3 py-2 font-medium text-white">{cloneResult.comparison.generated_centroid_hz.toFixed(0)} Hz</td>
                        </tr>
                        <tr>
                          <td className="px-3 py-2 text-slate-400">Duration</td>
                          <td className="px-3 py-2">{cloneResult.comparison.reference_duration_sec}s</td>
                          <td className="px-3 py-2 font-medium text-white">{cloneResult.comparison.generated_duration_sec}s</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* 4-Panel Comparative Visualization */}
                {cloneResult.plot_url && (
                  <div className="space-y-2">
                    <h4 className="text-xs uppercase font-semibold text-slate-400 tracking-wider">
                      Dual-Domain Acoustic Spectrograms
                    </h4>
                    <img
                      src={cloneResult.plot_url}
                      alt="Comparative Acoustic Report"
                      className="w-full rounded-xl border border-space-750 shadow-sm"
                    />
                  </div>
                )}
              </div>
            ) : (
              <div className="py-16 text-center space-y-3 text-slate-400">
                <div className="w-12 h-12 rounded-2xl bg-space-850 border border-space-750 flex items-center justify-center mx-auto text-slate-500">
                  <Play className="w-6 h-6 ml-0.5" />
                </div>
                <div>
                  <h4 className="text-sm font-semibold text-slate-300">Ready for Synthesis</h4>
                  <p className="text-xs text-slate-500 max-w-xs mx-auto mt-1">
                    Select a reference voice, enter your sentence, and click Generate Speech to synthesize.
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
