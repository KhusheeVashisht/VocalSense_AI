"""VOCALSENSE AI: Personalised Voice Cloning, Speech Processing & Analytics.

Full-Stack Application with Gradio UI & Mounted FastAPI REST API.
"""

import os
import sys
import time

# Ensure local imports and ABI shims
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
try:
    import brotli
except ImportError:
    try:
        import brotlicffi as brotli
        sys.modules["brotli"] = brotli
    except ImportError:
        pass

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["USE_TF"] = "0"

import gradio as gr
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.voice_engine import VoiceCloningEngine
from src.audio_analysis import (
    validate_and_preprocess_audio,
    analyze_audio,
    generate_visual_acoustic_report,
)
from src.evaluation import compare_recordings, plot_comparative_acoustic_report
from src.nlp_preprocessor import validate_and_preprocess_text, SUPPORTED_LANGUAGES
from src.transcription import transcribe_audio
from src.database import (
    init_database,
    save_recording,
    list_recordings,
    get_recording_by_id,
)
from src.analytics import (
    get_analytics_summary,
    get_analytics_timeseries,
    export_tableau_csv_file,
)
from src.api import router as api_router

# Initialize database schema
init_database()

# Initialize voice cloning engine singleton
engine = VoiceCloningEngine.get_instance(device="cpu")

SAMPLE_VOICES = {
    "Authorized Speaker Alpha (Male Tone)": os.path.abspath("samples/sample_speaker_male.wav"),
    "Authorized Speaker Beta (Female Tone)": os.path.abspath("samples/sample_speaker_female.wav"),
    "Custom Upload / Microphone": None,
}

SAMPLE_TEXTS = [
    "Welcome to VocalSense AI. Your personalized voice cloning system is active.",
    "Artificial intelligence and deep learning allow zero-shot voice synthesis from brief reference recordings.",
    "The quick brown fox jumps over the lazy dog near the quiet riverbank.",
    "Dr. Smith explained that acoustic measurements alone cannot legally establish biometric identity.",
]


def load_sample_audio(selection):
    """Load sample audio into the reference audio player when selected."""
    path = SAMPLE_VOICES.get(selection)
    if path and os.path.exists(path):
        return path
    return None


def inspect_reference_audio(audio_path):
    """Analyze and display properties of the reference audio recording."""
    if not audio_path or not os.path.exists(audio_path):
        return "No valid reference audio selected.", None

    is_valid, msg, meta = validate_and_preprocess_audio(audio_path)
    if not is_valid:
        return f"⚠️ **Audio Validation Error:** {msg}", None

    analysis = analyze_audio(audio_path)
    report_img = generate_visual_acoustic_report(audio_path, title_prefix="Reference Voice")

    summary_md = f"""
### Reference Audio Inspection:
* **File:** `{analysis['file_name']}`
* **Duration:** `{analysis['duration_sec']} s`
* **Sample Rate:** `{analysis['sample_rate']} Hz` (resampled to 16,000 Hz for neural processing)
* **Mean Pitch (F0):** `{analysis['mean_pitch_hz']}{' Hz' if isinstance(analysis['mean_pitch_hz'], (int, float)) else ''}`
* **RMS Energy:** `{analysis['mean_rms_energy']}`
* **Spectral Centroid:** `{analysis['spectral_centroid_hz']} Hz`

> *Note:* Recording acoustic properties describe signal characteristics, not legal biometric identity.
"""
    return summary_md, report_img


def run_voice_cloning(reference_audio, custom_text, language_code, progress=gr.Progress()):
    """Execute end-to-end reference-conditioned speech generation and evaluation."""
    if not reference_audio:
        return (
            "❌ **Error:** Please upload or record an authorized reference audio sample.",
            None,
            None,
            None,
            None,
        )

    if not custom_text or not custom_text.strip():
        return (
            "❌ **Error:** Please enter the text sentence you wish to synthesise.",
            None,
            None,
            None,
            None,
        )

    progress(0.1, desc="Validating inputs and normalizing text...")
    is_valid_text, norm_text, text_meta = validate_and_preprocess_text(custom_text, language=language_code)
    if not is_valid_text:
        return f"❌ **Text Validation Error:** {norm_text}", None, None, None, None

    progress(0.3, desc="Extracting reference speaker embedding (x-vector)...")
    success, msg, out_path, gen_meta = engine.clone_and_synthesize(
        text=norm_text,
        reference_audio_path=reference_audio,
        language=language_code,
        output_dir="outputs",
    )

    if not success or not out_path or not os.path.exists(out_path):
        return f"❌ **Voice Synthesis Failed:** {msg}", None, None, None, None

    progress(0.7, desc="Computing acoustic analysis & comparative evaluation...")
    eval_stats = compare_recordings(reference_audio, out_path, engine=engine)
    comp_plot = plot_comparative_acoustic_report(reference_audio, out_path)

    progress(1.0, desc="Completed!")

    status_md = f"""
### ✅ Speech Generation Successful!
* **Processing Status:** {msg}
* **Generated Audio Duration:** `{gen_meta['audio_duration_seconds']} s`
* **Synthesis Time:** `{gen_meta['synthesis_time_sec']} s` | **Real-Time Factor:** `{gen_meta['real_time_factor']}x`
* **Output Path:** `{out_path}`
* **Model Pipeline:** `SpeechT5 (Microsoft) + HiFi-GAN Vocoder` conditioned on `SpeechBrain VoxCeleb X-Vector`
* **Disclaimer:** *AI-generated synthetic speech. For authorized educational and assistive use only.*
"""

    eval_md = f"""
### 📊 Comparative Evaluation & Acoustic Resemblance:
| Metric | Reference Voice | Generated Voice | Difference / Ratio |
| :--- | :--- | :--- | :--- |
| **Speaker Embedding Cosine Similarity** | `1.000` | `{eval_stats['speaker_embedding_similarity']}` | **{eval_stats['similarity_interpretation']}** |
| **Mean Fundamental Frequency (F0)** | `{eval_stats['reference_pitch_hz']} Hz` | `{eval_stats['generated_pitch_hz']} Hz` | `Δ {eval_stats['pitch_difference_hz']} Hz` |
| **Mean RMS Energy** | `{eval_stats['reference_energy_rms']}` | `{eval_stats['generated_energy_rms']}` | `Ratio: {eval_stats['energy_ratio_gen_to_ref']}x` |
| **Spectral Centroid (Brightness)** | `{eval_stats['reference_centroid_hz']} Hz` | `{eval_stats['generated_centroid_hz']} Hz` | `Timbral resonance` |
| **Audio Duration** | `{eval_stats['reference_duration_sec']} s` | `{eval_stats['generated_duration_sec']} s` | Synthesized sentence length |

> **Evaluation Methodology:**
> Speaker embedding cosine similarity quantifies how closely the neural vocal characteristics cluster in the 512-dim embedding space.
> Differences in pitch and energy represent natural prosodic variation across distinct linguistic sentences and do not imply failure.
"""

    return status_md, out_path, out_path, eval_md, comp_plot


def run_transcription(audio_file, progress=gr.Progress()):
    """Execute speech-to-text transcription and persist recording metadata."""
    if not audio_file:
        return "❌ **Error:** Please provide an audio recording to transcribe.", None, None

    progress(0.2, desc="Loading audio and faster-whisper model...")
    success, transcript, meta = transcribe_audio(audio_file)

    if not success:
        save_recording(
            operation_type="transcription",
            file_name=os.path.basename(audio_file),
            duration_seconds=0.0,
            sample_rate=16000,
            processing_duration_ms=meta.get("processing_duration_ms", 0.0),
            processing_status="failed",
            error_message=transcript,
        )
        return f"❌ **Transcription Error:** {transcript}", None, None

    progress(0.8, desc="Persisting metadata and metrics to SQLite...")
    rec_id = save_recording(
        operation_type="transcription",
        file_name=meta["file_name"],
        duration_seconds=meta["audio_duration_seconds"],
        sample_rate=meta["sample_rate"],
        processing_duration_ms=meta["processing_duration_ms"],
        processing_status="success",
        transcript=transcript,
        word_count=meta["word_count"],
        character_count=meta["character_count"],
        language_code=meta["detected_language"],
        estimated_wpm=meta["estimated_wpm"],
    )

    metrics_md = f"""
### 🎙️ Transcription Metrics & Processing Summary
* **Recording ID:** `{rec_id}`
* **Detected Language:** `{meta['detected_language'].upper()}` (Confidence: `{meta['language_confidence']*100:.1f}%`)
* **Audio Duration:** `{meta['audio_duration_seconds']} s`
* **Word Count:** `{meta['word_count']} words` | **Character Count:** `{meta['character_count']} chars`
* **Estimated Speaking Pace:** `{meta['estimated_wpm']} WPM` *(Estimated over total audio length)*
* **Processing Latency:** `{meta['processing_duration_ms']:.1f} ms` (Inference: `{meta['inference_duration_ms']:.1f} ms`)
* **Persistence:** Saved to SQLite database (`vocalsense.db`).
"""

    return transcript, metrics_md, audio_file


def fetch_history_table(op_filter="All", status_filter="All"):
    """Fetch formatted recording history for the data table."""
    op = None if op_filter == "All" else op_filter.lower().replace(" ", "_")
    st = None if status_filter == "All" else status_filter.lower()

    records, total = list_recordings(limit=100, operation_type=op, status=st)

    table_data = []
    for r in records:
        table_data.append([
            r["recording_id"][:8] + "...",
            r["created_at"][:19].replace("T", " "),
            r["operation_type"].replace("_", " ").title(),
            r["file_name"],
            f"{r['duration_seconds']:.1f}s",
            r["word_count"] or 0,
            r["language_code"] or "N/A",
            "✅ " + r["processing_status"].title() if r["processing_status"] == "success" else "❌ Failed",
            f"{r['processing_duration_ms']:.0f} ms",
        ])

    status_text = f"Showing {len(table_data)} of {total} total recordings from `vocalsense.db`."
    return table_data, status_text


def fetch_analytics_view():
    """Compute aggregate analytics KPIs and generate multi-panel distribution plots."""
    summary = get_analytics_summary()
    timeseries = get_analytics_timeseries()

    fig, axes = plt.subplots(2, 2, figsize=(11, 7), constrained_layout=True)

    records, _ = list_recordings(limit=200, status="success")
    if records:
        durs = [r["duration_seconds"] for r in records if r["duration_seconds"] > 0]
        latencies = [r["processing_duration_ms"] / 1000.0 for r in records if r["duration_seconds"] > 0]
        axes[0, 0].scatter(durs, latencies, color="#2563eb", alpha=0.7, edgecolors="none")
        max_d = max(durs) if durs else 10
        axes[0, 0].plot([0, max_d], [0, max_d], "r--", alpha=0.6, label="1.0x RTF (Real-Time)")
        axes[0, 0].set_title("Processing Latency vs Audio Duration", fontsize=10, fontweight="bold")
        axes[0, 0].set_xlabel("Audio Duration (seconds)", fontsize=8)
        axes[0, 0].set_ylabel("Processing Time (seconds)", fontsize=8)
        axes[0, 0].legend(fontsize=8)
        axes[0, 0].grid(True, linestyle="--", alpha=0.4)
    else:
        axes[0, 0].text(0.5, 0.5, "No recording data yet", ha="center", va="center")

    wpms = [r["estimated_words_per_minute"] for r in records if r["estimated_words_per_minute"]]
    if wpms:
        axes[0, 1].hist(wpms, bins=10, color="#059669", alpha=0.8, edgecolor="white")
        axes[0, 1].set_title("Speaking Pace Distribution (Estimated WPM)", fontsize=10, fontweight="bold")
        axes[0, 1].set_xlabel("Words Per Minute (WPM)", fontsize=8)
        axes[0, 1].set_ylabel("Count", fontsize=8)
        axes[0, 1].grid(True, linestyle="--", alpha=0.4)
    else:
        axes[0, 1].text(0.5, 0.5, "No speech records with transcripts", ha="center", va="center")

    ops = summary.get("operations_breakdown", {})
    if ops:
        labels = [k.replace("_", " ").title() for k in ops.keys()]
        counts = list(ops.values())
        axes[1, 0].bar(labels, counts, color=["#6366f1", "#06b6d4", "#f59e0b"][:len(labels)], width=0.5)
        axes[1, 0].set_title("Operations Volume Breakdown", fontsize=10, fontweight="bold")
        axes[1, 0].set_ylabel("Recordings Count", fontsize=8)
        axes[1, 0].grid(True, linestyle="--", alpha=0.4)
    else:
        axes[1, 0].text(0.5, 0.5, "No operations recorded", ha="center", va="center")

    if timeseries:
        dates = [t["date"] for t in timeseries]
        counts = [t["count"] for t in timeseries]
        axes[1, 1].plot(dates, counts, marker="o", color="#d97706", linewidth=1.5)
        axes[1, 1].set_title("Daily Processing Activity Over Time", fontsize=10, fontweight="bold")
        axes[1, 1].set_xlabel("Date", fontsize=8)
        axes[1, 1].set_ylabel("Total Jobs", fontsize=8)
        axes[1, 1].tick_params(axis="x", rotation=30)
        axes[1, 1].grid(True, linestyle="--", alpha=0.4)
    else:
        axes[1, 1].text(0.5, 0.5, "No timeline data", ha="center", va="center")

    os.makedirs("outputs", exist_ok=True)
    plot_path = os.path.join("outputs", "analytics_dashboard_plot.png")
    fig.savefig(plot_path, dpi=120, bbox_inches="tight")
    plt.close(fig)

    kpi_md = f"""
### 📈 Real-Time Application Metrics & KPIs
| Total Recordings | Success Rate | Total Audio | Total Words | Avg Latency | Avg Speaking Pace |
| :---: | :---: | :---: | :---: | :---: | :---: |
| **{summary['total_recordings']}** | **{summary['success_rate_percent']}%** | **{summary['total_audio_duration_minutes']} min** | **{summary['total_words_processed']}** | **{summary['average_processing_duration_ms']:.0f} ms** | **{summary['average_speaking_pace_wpm']} WPM** |
"""
    return kpi_md, plot_path


def generate_and_download_csv():
    """Generate the Tableau export CSV file and return its path for download."""
    export_path = export_tableau_csv_file("outputs/vocalsense_analytics_export.csv")
    summary = get_analytics_summary()
    status_md = f"""
✅ **Tableau CSV Dataset Exported Successfully!**
* **File:** `outputs/vocalsense_analytics_export.csv`
* **Total Rows:** `{summary['total_recordings']}`
* **Encoding:** UTF-8 with BOM (`utf-8-sig`) — *Ready for immediate open in Tableau Desktop, Tableau Public, or Excel*.
* **Formula Injection:** *Protected (leading symbols sanitized).*
* **Privacy:** *Full transcripts and raw audio are excluded.*
"""
    return export_path, export_path, status_md


custom_css = """
.main-title { text-align: center; font-size: 2.2rem; font-weight: 800; color: #1e3a8a; margin-bottom: 0.2rem; }
.sub-title { text-align: center; font-size: 1.1rem; color: #4b5563; margin-bottom: 1.2rem; }
.badge-container { display: flex; justify-content: center; gap: 10px; margin-bottom: 1.2rem; flex-wrap: wrap; }
.badge { background: #e0e7ff; color: #3730a3; padding: 4px 12px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; }
.warning-box { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 10px; border-radius: 4px; margin-bottom: 0.8rem; font-size: 0.9rem; }
"""

with gr.Blocks(title="VOCALSENSE AI: Voice Cloning, Speech Processing & Analytics") as demo:
    gr.HTML("""
        <div class="main-title">VOCALSENSE AI</div>
        <div class="sub-title">Personalised Voice Cloning, Speech Processing & Tableau Analytics</div>
        <div class="badge-container">
            <span class="badge">SpeechT5 + HiFi-GAN</span>
            <span class="badge">SpeechBrain X-Vector</span>
            <span class="badge">Faster-Whisper STT</span>
            <span class="badge">SQLite Persistence</span>
            <span class="badge">Tableau Integration</span>
            <span class="badge">FastAPI REST API</span>
        </div>
    """)

    with gr.Tabs():
        # TAB 1: Voice Cloning & Speech Synthesis
        with gr.TabItem("🎙️ Voice Cloning & Synthesis"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 1. Reference Voice Input")
                    sample_dropdown = gr.Dropdown(
                        choices=list(SAMPLE_VOICES.keys()),
                        value="Authorized Speaker Alpha (Male Tone)",
                        label="Select Reference Voice or Upload Your Own",
                        info="Pick an authorized sample voice or upload a custom recording below.",
                    )

                    ref_audio_input = gr.Audio(
                        value=SAMPLE_VOICES["Authorized Speaker Alpha (Male Tone)"],
                        type="filepath",
                        label="Reference Audio Recording (WAV, MP3, FLAC)",
                        sources=["upload", "microphone"],
                    )

                    with gr.Accordion("Guidelines for Best Reference Quality", open=False):
                        gr.Markdown("""
                        * **Duration:** 3 to 10 seconds of clear, uninterrupted speech.
                        * **Acoustics:** Quiet environment with low room reverberation.
                        * **Authorization:** Only reproduce your own voice or voices with explicit consent.
                        """)

                    inspect_btn = gr.Button("🔍 Inspect Reference Audio Properties", size="sm")
                    ref_info_output = gr.Markdown()
                    ref_plot_output = gr.Image(label="Reference Acoustic Waveform & Spectrogram", type="filepath")

                    gr.Markdown("### 2. Text Input & NLP Normalization")
                    language_selector = gr.Dropdown(
                        choices=[("English (Native)", "en")],
                        value="en",
                        label="Synthesis Language",
                        interactive=False,
                        info="SpeechT5 natively supports English phonetics.",
                    )

                    sample_text_dropdown = gr.Dropdown(
                        choices=SAMPLE_TEXTS,
                        value=SAMPLE_TEXTS[0],
                        label="Sample Sentences",
                    )

                    text_input = gr.Textbox(
                        value=SAMPLE_TEXTS[0],
                        lines=3,
                        max_lines=6,
                        label="Sentence to Synthesise",
                    )

                    generate_btn = gr.Button("🎙️ Generate Cloned Speech", variant="primary", size="lg")

                with gr.Column(scale=1):
                    gr.Markdown("### 3. Speech Generation & Playback")
                    status_output = gr.Markdown("Ready. Select reference audio and click 'Generate Cloned Speech'.")

                    gr.HTML("""
                        <div class="warning-box">
                            <strong>Notice:</strong> Output generated by this system is watermarked as <strong>AI-generated synthetic speech</strong>.
                        </div>
                    """)

                    audio_playback = gr.Audio(
                        label="Generated Speech Playback",
                        type="filepath",
                        interactive=False,
                    )

                    download_file = gr.File(
                        label="Download Synthesized Audio File",
                        interactive=False,
                    )

                    gr.Markdown("### 4. Acoustic Evaluation & Identity Comparison")
                    eval_output = gr.Markdown("Evaluation metrics will appear here after speech generation.")
                    comp_plot_output = gr.Image(label="Comparative Waveform & Spectrogram", type="filepath")

        # TAB 2: Speech Processing & Transcription
        with gr.TabItem("📝 Speech-to-Text Transcription"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Audio Input for Transcription")
                    transcribe_audio_input = gr.Audio(
                        type="filepath",
                        label="Speech Recording to Transcribe",
                        sources=["upload", "microphone"],
                    )
                    transcribe_btn = gr.Button("Transcribe Speech (Faster-Whisper)", variant="primary", size="lg")

                with gr.Column(scale=1):
                    gr.Markdown("### Transcript & Metrics Output")
                    transcript_output = gr.Textbox(
                        label="Transcribed Text",
                        lines=5,
                        placeholder="Transcript will appear here...",
                    )
                    transcribe_metrics_output = gr.Markdown("Transcription metadata will appear here.")
                    transcribe_playback = gr.Audio(label="Audio Playback", type="filepath", interactive=False)

        # TAB 3: Recording History
        with gr.TabItem("🗄️ Recording History"):
            gr.Markdown("### Persisted Recording Log (`vocalsense.db`)")
            with gr.Row():
                op_filter = gr.Dropdown(
                    choices=["All", "Voice Cloning", "Transcription"],
                    value="All",
                    label="Filter by Operation",
                )
                status_filter = gr.Dropdown(
                    choices=["All", "Success", "Failed"],
                    value="All",
                    label="Filter by Status",
                )
                refresh_history_btn = gr.Button("🔄 Refresh History", size="sm")

            history_status = gr.Markdown("Loading records...")
            history_table = gr.Dataframe(
                headers=["ID", "Timestamp (UTC)", "Operation", "File", "Duration", "Words", "Lang", "Status", "Latency"],
                datatype=["str", "str", "str", "str", "str", "number", "str", "str", "str"],
                interactive=False,
            )

        # TAB 4: Data Analytics & Tableau Export
        with gr.TabItem("📊 Data Analytics & Tableau Export"):
            gr.Markdown("### Application-Wide Speech Analytics & Tableau Integration")
            refresh_analytics_btn = gr.Button("🔄 Recompute Live Analytics", size="sm")

            kpi_display = gr.Markdown("Loading KPIs...")
            analytics_plot = gr.Image(label="Application Analytics Dashboard", type="filepath")

            gr.Markdown("---")
            gr.Markdown("### 📥 Export Dataset for Tableau Desktop / Public")
            gr.Markdown("""
            Export all persisted speech events as a sanitized, UTF-8 CSV dataset ready to connect into Tableau.
            Detailed calculated fields, chart types, and dashboard guides are in `TABLEAU_GUIDE.md`.
            """)
            export_csv_btn = gr.Button("📊 Export Tableau Analytics Dataset (CSV)", variant="primary", size="lg")
            export_status_output = gr.Markdown()
            csv_download_file = gr.File(label="Download Tableau-Ready CSV Export", interactive=False)

        # TAB 5: Deep Learning & Ethics Documentation
        with gr.TabItem("📖 Architecture & Governance"):
            gr.Markdown("""
            ### Technical Deep Learning & NLP Architecture

            ```mermaid
            flowchart TD
                UserAudio["Audio Input (Upload/Microphone)"] --> Preproc["Audio Preprocessing (16kHz Mono)"]
                
                Preproc --> Whisper["Faster-Whisper (Speech-to-Text)"]
                Whisper --> Transcript["Transcript & WPM Metrics"]
                Transcript --> SQLite[("SQLite Database (vocalsense.db)")]

                Preproc --> SpkEncoder["SpeechBrain TDNN X-Vector Encoder"]
                SpkEncoder --> Embedding["512-dim Speaker Embedding Vector"]

                TextInput["Raw Input Text"] --> NLP["Lexical Normalization"]
                NLP --> SpeechT5["SpeechT5 Autoregressive Transformer"]
                Embedding --> SpeechT5
                SpeechT5 --> Vocoder["HiFi-GAN Neural Vocoder"]
                Vocoder --> SynAudio["Synthesized Speech Waveform"]

                SynAudio --> AcousticEval["Acoustic & Cosine Similarity Evaluation"]
                AcousticEval --> SQLite

                SQLite --> Analytics["Analytics & KPI Aggregation Layer"]
                Analytics --> CSVExport["Tableau CSV Dataset (outputs/vocalsense_analytics_export.csv)"]
                CSVExport --> Tableau["Tableau Desktop / Public Dashboards"]
            ```

            * **Speaker Encoder:** Pretrained TDNN x-vector model (`speechbrain/spkrec-xvect-voxceleb`) maps reference speech into a 512-dim vector.
            * **Synthesis Model:** Microsoft SpeechT5 (`microsoft/speecht5_tts`) transformer conditioned on the speaker embedding.
            * **Vocoder:** HiFi-GAN (`microsoft/speecht5_hifigan`) neural vocoder.
            * **Transcription:** Faster-Whisper int8 on CPU for lightweight speech-to-text.
            * **Persistence:** SQLite (`vocalsense.db`) with parameterized transactions and safe schema migrations.
            * **Tableau Integration:** Structured CSV export conforming to `TABLEAU_GUIDE.md`.
            * **REST API:** Built-in FastAPI endpoints mounted at `/api/*` for health, history, and analytics.
            """)

    # Interactive Event Handlers
    sample_dropdown.change(
        fn=load_sample_audio,
        inputs=[sample_dropdown],
        outputs=[ref_audio_input],
    )

    sample_text_dropdown.change(
        fn=lambda t: t,
        inputs=[sample_text_dropdown],
        outputs=[text_input],
    )

    inspect_btn.click(
        fn=inspect_reference_audio,
        inputs=[ref_audio_input],
        outputs=[ref_info_output, ref_plot_output],
    )

    generate_btn.click(
        fn=run_voice_cloning,
        inputs=[ref_audio_input, text_input, language_selector],
        outputs=[status_output, audio_playback, download_file, eval_output, comp_plot_output],
    )

    transcribe_btn.click(
        fn=run_transcription,
        inputs=[transcribe_audio_input],
        outputs=[transcript_output, transcribe_metrics_output, transcribe_playback],
    )

    refresh_history_btn.click(
        fn=fetch_history_table,
        inputs=[op_filter, status_filter],
        outputs=[history_table, history_status],
    )

    op_filter.change(
        fn=fetch_history_table,
        inputs=[op_filter, status_filter],
        outputs=[history_table, history_status],
    )

    status_filter.change(
        fn=fetch_history_table,
        inputs=[op_filter, status_filter],
        outputs=[history_table, history_status],
    )

    refresh_analytics_btn.click(
        fn=fetch_analytics_view,
        inputs=[],
        outputs=[kpi_display, analytics_plot],
    )

    export_csv_btn.click(
        fn=generate_and_download_csv,
        inputs=[],
        outputs=[csv_download_file, csv_download_file, export_status_output],
    )

    demo.load(
        fn=fetch_history_table,
        inputs=[op_filter, status_filter],
        outputs=[history_table, history_status],
    )
    demo.load(
        fn=fetch_analytics_view,
        inputs=[],
        outputs=[kpi_display, analytics_plot],
    )


# Unified FastAPI Server exposing REST API, Static Audio Assets, React Frontend, and Gradio Fallback
server = FastAPI(
    title="VocalSense AI API",
    description="Speech Processing, Voice Cloning & Analytics REST API",
    version="1.0.0",
)

# 1. Mount REST API endpoints under /api/*
server.include_router(api_router)

# 2. Mount static outputs & sample directories for audio streaming & spectrogram viewing
os.makedirs("outputs", exist_ok=True)
os.makedirs("samples", exist_ok=True)
server.mount("/outputs", StaticFiles(directory="outputs"), name="outputs")
server.mount("/samples", StaticFiles(directory="samples"), name="samples")

# 3. Mount Gradio interface as fallback under /gradio
gr.mount_gradio_app(server, demo, path="/gradio")

# 4. Mount Production React Frontend at root (/)
frontend_dist = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend", "dist")
if os.path.exists(frontend_dist):
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.exists(assets_dir):
        server.mount("/assets", StaticFiles(directory=assets_dir), name="frontend_assets")

    @server.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        # Do not intercept API, gradio, outputs, samples, docs, redoc
        if full_path.startswith(("api", "gradio", "outputs", "samples", "docs", "redoc", "openapi.json")):
            raise HTTPException(status_code=404, detail="Not Found")
        file_path = os.path.join(frontend_dist, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))

app = server

if __name__ == "__main__":
    print("[VocalSense AI] Starting Unified Server on http://127.0.0.1:7860 ...")
    print("  -> React Premium UI:  http://127.0.0.1:7860/")
    print("  -> Gradio Fallback:   http://127.0.0.1:7860/gradio")
    print("  -> Swagger API Docs:  http://127.0.0.1:7860/docs")
    uvicorn.run(server, host="127.0.0.1", port=7860, log_level="info")
