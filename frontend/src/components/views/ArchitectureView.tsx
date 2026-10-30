import React from 'react';
import {
  Cpu,
  Layers,
  Database,
  ShieldCheck,
  Server,
  FileCode,
  ExternalLink,
  Zap,
} from 'lucide-react';

export const ArchitectureView: React.FC = () => {
  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      {/* Header */}
      <div className="p-6 rounded-2xl bg-space-900 border border-space-750 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-brand-purple text-xs font-semibold uppercase tracking-wider mb-1">
            <Cpu className="w-4 h-4" />
            <span>Deep Learning & Full-Stack Infrastructure</span>
          </div>
          <h2 className="text-xl font-bold text-white tracking-tight">System Architecture & Technical Specifications</h2>
          <p className="text-xs text-slate-400 mt-1 max-w-2xl">
            Detailed breakdown of models, vocoders, embeddings, database migrations, and local CPU inference constraints.
          </p>
        </div>

        <a
          href="/gradio"
          target="_blank"
          rel="noopener noreferrer"
          className="flex items-center gap-2 px-3.5 py-2 rounded-xl bg-space-850 hover:bg-space-800 text-xs font-medium text-slate-300 border border-space-750 transition-colors self-start md:self-auto shrink-0"
        >
          <span>Gradio Classic UI</span>
          <ExternalLink className="w-3.5 h-3.5 text-slate-400" />
        </a>
      </div>

      {/* Layer Architecture Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Layer 1: Frontend */}
        <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-3">
          <div className="p-3 rounded-xl bg-brand-purple/10 text-brand-purple w-fit">
            <FileCode className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-white">1. Modern Frontend Layer</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Built with React 18, TypeScript, Tailwind CSS, and Lucide icons. Bundled with Vite and served directly from FastAPI static routes at root (/). Includes Gradio fallback mounted at /gradio.
          </p>
          <div className="pt-2 text-[11px] text-brand-purple font-mono">
            Vite 9.3 • React 18 • Tailwind CSS
          </div>
        </div>

        {/* Layer 2: Serving */}
        <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-3">
          <div className="p-3 rounded-xl bg-brand-indigo/10 text-brand-indigo w-fit">
            <Server className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-white">2. Unified ASGI Server</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            FastAPI handles REST API endpoints (/api/*), static generated audio/plots (/outputs/*), and sample clips (/samples/*) concurrently on port 7860 via Uvicorn without CORS issues.
          </p>
          <div className="pt-2 text-[11px] text-brand-indigo font-mono">
            FastAPI 0.133 • Uvicorn 0.43 • Port 7860
          </div>
        </div>

        {/* Layer 3: Voice Cloning */}
        <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-3">
          <div className="p-3 rounded-xl bg-brand-violet/10 text-brand-violet w-fit">
            <Zap className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-white">3. Zero-Shot Synthesis Engine</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            SpeechBrain TDNN encoder maps reference audio into 512-dim x-vectors. Microsoft SpeechT5 decodes mel-spectrograms conditioned on the embedding, synthesized to 16 kHz WAV by HiFi-GAN.
          </p>
          <div className="pt-2 text-[11px] text-brand-violet font-mono">
            SpeechT5 • SpeechBrain • HiFi-GAN
          </div>
        </div>

        {/* Layer 4: Transcription */}
        <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-3">
          <div className="p-3 rounded-xl bg-brand-cyan/10 text-brand-cyan w-fit">
            <Cpu className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-white">4. Faster-Whisper ASR</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Lightweight offline speech-to-text using CTranslate2 int8 quantization on CPU. Automatic language detection, timestamping, word counting, and normalized speaking pace (WPM) calculation.
          </p>
          <div className="pt-2 text-[11px] text-brand-cyan font-mono">
            Faster-Whisper tiny • int8 CPU • VAD Filter
          </div>
        </div>

        {/* Layer 5: Signal Analysis */}
        <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-3">
          <div className="p-3 rounded-xl bg-brand-amber/10 text-brand-amber w-fit">
            <Layers className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-white">5. Acoustic Signal Processing</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Probabilistic YIN (pYIN) fundamental frequency (F0) tracking with autocorrelation fallback. Root Mean Square (RMS) energy and spectral centroid brightness computed via Librosa.
          </p>
          <div className="pt-2 text-[11px] text-brand-amber font-mono">
            Librosa 1.0 • SoundFile 0.14 • pYIN F0
          </div>
        </div>

        {/* Layer 6: Persistence & BI */}
        <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-3">
          <div className="p-3 rounded-xl bg-brand-emerald/10 text-brand-emerald w-fit">
            <Database className="w-5 h-5" />
          </div>
          <h3 className="text-sm font-bold text-white">6. SQLite & Tableau Engine</h3>
          <p className="text-xs text-slate-400 leading-relaxed">
            Embedded SQLite persistence with Write-Ahead Logging (WAL) and auto-migrations. Exports sanitized, formula-injection-safe CSV datasets (15 columns) formatted in UTF-8 with BOM for Tableau.
          </p>
          <div className="pt-2 text-[11px] text-brand-emerald font-mono">
            SQLite WAL • vocalsense.db • Tableau Ready
          </div>
        </div>
      </div>

      {/* Model Provenance & Provenance Matrix */}
      <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-4">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">
          Foundation Models Provenance & Integrity
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-space-850 text-slate-400 text-[10px] uppercase border-b border-space-750">
              <tr>
                <th className="px-4 py-3 font-semibold">Pipeline Role</th>
                <th className="px-4 py-3 font-semibold">Model Checkpoint</th>
                <th className="px-4 py-3 font-semibold">Author / License</th>
                <th className="px-4 py-3 font-semibold">Inference Mode</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-space-750 text-slate-300">
              <tr>
                <td className="px-4 py-3 font-medium text-white">Speaker Embedding</td>
                <td className="px-4 py-3 font-mono text-brand-purple">speechbrain/spkrec-xvect-voxceleb</td>
                <td className="px-4 py-3">SpeechBrain (Apache 2.0)</td>
                <td className="px-4 py-3">PyTorch CPU (512-dim)</td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-medium text-white">Acoustic Generator</td>
                <td className="px-4 py-3 font-mono text-brand-purple">microsoft/speecht5_tts</td>
                <td className="px-4 py-3">Microsoft Research (MIT)</td>
                <td className="px-4 py-3">Transformers CPU Seq2Seq</td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-medium text-white">Neural Vocoder</td>
                <td className="px-4 py-3 font-mono text-brand-purple">microsoft/speecht5_hifigan</td>
                <td className="px-4 py-3">Microsoft Research (MIT)</td>
                <td className="px-4 py-3">HiFi-GAN GAN Vocoder 16kHz</td>
              </tr>
              <tr>
                <td className="px-4 py-3 font-medium text-white">Speech-to-Text</td>
                <td className="px-4 py-3 font-mono text-brand-purple">Systran/faster-whisper-tiny</td>
                <td className="px-4 py-3">SYSTRAN / OpenAI (MIT)</td>
                <td className="px-4 py-3">CTranslate2 int8 CPU</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Ethics & Responsible AI */}
      <div className="p-6 rounded-2xl bg-space-900 border border-space-750 space-y-3">
        <div className="flex items-center gap-2 text-brand-emerald text-xs font-semibold uppercase tracking-wider">
          <ShieldCheck className="w-4 h-4" />
          <span>Ethics, Privacy & Biometric Disclaimer</span>
        </div>
        <p className="text-xs text-slate-300 leading-relaxed">
          <strong>1. Authorized Use Only:</strong> VocalSense AI is engineered strictly for assistive speech, accessibility, and authorized voice reproduction with explicit user consent.
          <br />
          <strong>2. 100% Local Inference:</strong> No audio binaries, neural embeddings, or linguistic transcripts are ever transmitted to external cloud servers. All inference runs locally on the host CPU.
          <br />
          <strong>3. Biometric Identity Disclaimer:</strong> Speaker embedding cosine similarity and acoustic metrics (pitch, RMS energy) quantify signal characteristics; they do not constitute legal biometric proof of identity.
        </p>
      </div>
    </div>
  );
};
