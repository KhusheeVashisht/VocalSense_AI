"""VOCALSENSE AI: Personalised Voice Cloning and Speech Synthesis.

Gradio Web Application.
"""

import os
import sys

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
from src.voice_engine import VoiceCloningEngine
from src.audio_analysis import (
    validate_and_preprocess_audio,
    analyze_audio,
    generate_visual_acoustic_report,
)
from src.evaluation import compare_recordings, plot_comparative_acoustic_report
from src.nlp_preprocessor import validate_and_preprocess_text, SUPPORTED_LANGUAGES

# Initialize engine instance
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


# Build Gradio UI
custom_css = """
.main-title { text-align: center; font-size: 2.2rem; font-weight: 800; color: #1e3a8a; margin-bottom: 0.2rem; }
.sub-title { text-align: center; font-size: 1.1rem; color: #4b5563; margin-bottom: 1.5rem; }
.badge-container { display: flex; justify-content: center; gap: 10px; margin-bottom: 1.5rem; }
.badge { background: #e0e7ff; color: #3730a3; padding: 4px 12px; border-radius: 9999px; font-size: 0.85rem; font-weight: 600; }
.warning-box { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; border-radius: 4px; margin-bottom: 1rem; }
"""

with gr.Blocks(title="VOCALSENSE AI: Voice Cloning & Speech Synthesis") as demo:
    gr.HTML("""
        <div class="main-title">VOCALSENSE AI</div>
        <div class="sub-title">Personalised Voice Cloning and Speech Synthesis</div>
        <div class="badge-container">
            <span class="badge">Zero-Shot Speaker Adaptation</span>
            <span class="badge">Local CPU Inference</span>
            <span class="badge">SpeechT5 + HiFi-GAN</span>
            <span class="badge">Ethical & Privacy Certified</span>
        </div>
    """)

    with gr.Row():
        # LEFT COLUMN: Inputs
        with gr.Column(scale=1):
            gr.Markdown("### 1. Reference Voice Input")
            sample_dropdown = gr.Dropdown(
                choices=list(SAMPLE_VOICES.keys()),
                value="Authorized Speaker Alpha (Male Tone)",
                label="Select Reference Voice or Upload Your Own",
                info="Pick a pre-configured authorized sample voice or choose 'Custom Upload' below.",
            )

            ref_audio_input = gr.Audio(
                value=SAMPLE_VOICES["Authorized Speaker Alpha (Male Tone)"],
                type="filepath",
                label="Reference Audio Recording (WAV, MP3, FLAC)",
                sources=["upload", "microphone"],
            )

            with gr.Accordion("Instructions for Optimal Reference Sample", open=False):
                gr.Markdown("""
                * **Duration:** 3 to 10 seconds of clear, continuous speech.
                * **Acoustics:** Low background noise, minimal room reverberation/echo.
                * **Language/Tone:** Consistent speaking tone and clear articulation.
                * **Authorization:** Only use your own voice or voices with explicit permission.
                """)

            inspect_btn = gr.Button("🔍 Inspect Reference Audio Properties", size="sm")
            ref_info_output = gr.Markdown()
            ref_plot_output = gr.Image(label="Reference Acoustic Waveform & Spectrogram", type="filepath")

            gr.Markdown("### 2. Text Input & NLP Preprocessing")
            language_selector = gr.Dropdown(
                choices=[("English (Native)", "en")],
                value="en",
                label="Synthesis Language",
                interactive=False,
                info="SpeechT5 model natively supports English phonetics.",
            )

            sample_text_dropdown = gr.Dropdown(
                choices=SAMPLE_TEXTS,
                value=SAMPLE_TEXTS[0],
                label="Sample Sentences",
                info="Click to populate standard test sentences.",
            )

            text_input = gr.Textbox(
                value=SAMPLE_TEXTS[0],
                lines=3,
                max_lines=6,
                label="Sentence to Synthesise",
                placeholder="Enter text to synthesise in the reference voice...",
            )

            generate_btn = gr.Button("🎙️ Generate Cloned Speech", variant="primary", size="lg")

        # RIGHT COLUMN: Outputs
        with gr.Column(scale=1):
            gr.Markdown("### 3. Speech Generation & Playback")
            status_output = gr.Markdown("Ready to generate speech. Select reference audio and click 'Generate Cloned Speech'.")

            gr.HTML("""
                <div class="warning-box">
                    <strong>Notice:</strong> All outputs generated by this system are labeled as <strong>AI-generated synthetic speech</strong>.
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
            eval_output = gr.Markdown("Evaluation results will appear here after speech generation.")
            comp_plot_output = gr.Image(label="Comparative Waveform & Mel-Spectrogram Report", type="filepath")

    # Lower Information Tabs
    with gr.Tabs():
        with gr.TabItem("📖 Deep Learning Pipeline"):
            gr.Markdown("""
            ### Technical Deep Learning & NLP Architecture

            ```mermaid
            flowchart TD
                RefAudio["Reference Audio Recording (WAV/MP3)"] --> Preproc["Audio Preprocessing (16kHz Mono)"]
                Preproc --> SpkEncoder["SpeechBrain TDNN X-Vector Encoder"]
                SpkEncoder --> Embedding["512-dim Speaker Embedding Vector"]

                TextInput["Raw Input Text"] --> NLP["Lexical Normalization & Tokenization"]
                NLP --> TokenSeq["Character/Phoneme Tokens (input_ids)"]

                TokenSeq --> SpeechT5["SpeechT5 Autoregressive Transformer TTS"]
                Embedding --> SpeechT5

                SpeechT5 --> MelSpec["Conditioned Mel-Spectrogram"]
                MelSpec --> Vocoder["HiFi-GAN Neural Vocoder"]
                Vocoder --> SynAudio["Synthesized Audio Waveform (16kHz)"]

                SynAudio --> AcousticEval["Acoustic & Cosine Similarity Evaluation"]
                RefAudio --> AcousticEval
            ```

            * **Speaker Encoder:** Pretrained TDNN (Time-Delay Neural Network) x-vector model (`speechbrain/spkrec-xvect-voxceleb`) maps reference speech into a compact 512-dimensional embedding representing speaker timbre and vocal tract geometry.
            * **Synthesis Model:** Microsoft SpeechT5 (`microsoft/speecht5_tts`), a unified sequence-to-sequence transformer encoder-decoder trained on LibriTTS.
            * **Vocoder:** HiFi-GAN (`microsoft/speecht5_hifigan`), a generative adversarial network vocoder synthesizing high-fidelity waveforms from mel-spectrograms.
            * **NLP Preprocessing:** Rule-based regex expansion (abbreviations, numbers, currencies) ensuring orthographic-to-phonetic alignment.
            """)

        with gr.TabItem("⚖️ Privacy, Ethics & Academic Integrity"):
            gr.Markdown("""
            ### Ethical Guidelines & Academic Transparency
            * **Authorized Use Only:** This application is strictly designated for authorized voice synthesis using the user's own voice or recordings with explicit consent.
            * **Local Processing:** All acoustic analysis, neural embeddings, and audio generation execute locally on the CPU. No audio data or transcripts are transmitted to external cloud APIs or third parties.
            * **Deception & Impersonation Prohibition:** Generating audio intended to mislead, defraud, commit social engineering, or bypass biometric voice authentication systems is explicitly prohibited.
            * **Academic Distinction:** Pretrained models (`SpeechT5`, `SpeechBrain`, `HiFi-GAN`) provide foundational deep neural representations. VocalSense AI implements the engineering integration, audio preprocessing, text normalization, acoustic evaluation, and interactive user interface.
            * **Evaluation Distinction:** Fundamental frequency (pitch) and energy describe physical sound properties; they do not prove legal identity. Identity resemblance is assessed via speaker embedding cosine similarity.
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


if __name__ == "__main__":
    print("[VocalSense AI] Starting Gradio Web Server on local interface...")
    demo.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False,
        show_error=True,
        css=custom_css,
    )
