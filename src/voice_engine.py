"""Voice Cloning Engine for VocalSense AI.

Architecture & Pretrained Model Documentation:
----------------------------------------------
This engine performs zero-shot, reference-conditioned voice cloning using a dual deep-learning
pipeline:
1. Speaker Encoder: Pretrained TDNN x-vector model (`speechbrain/spkrec-xvect-voxceleb`)
   trained on VoxCeleb to map arbitrary reference audio into a dense 512-dimensional
   speaker embedding vector characterizing vocal tract properties and vocal timbre.
2. Acoustic Synthesis Model: Pretrained transformer-based Text-To-Speech (`microsoft/speecht5_tts`)
   that accepts linguistic phoneme sequence and conditions its autoregressive mel-spectrogram
   generation directly upon the 512-dimensional speaker embedding.
3. Neural Vocoder: Pretrained HiFi-GAN (`microsoft/speecht5_hifigan`) that synthesizes the
   generated mel-spectrogram into high-fidelity 16 kHz time-domain speech waveform.

All inference runs locally on CPU with zero cloud transmission, preserving user privacy.
"""

import os
import time
import hashlib
from typing import Tuple, Dict, Any, Optional

import torch
import soundfile as sf
import numpy as np

# Suppress noisy framework banners
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["USE_TF"] = "0"

from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan
from speechbrain.inference.speaker import EncoderClassifier

from src.nlp_preprocessor import validate_and_preprocess_text
from src.audio_analysis import validate_and_preprocess_audio, TARGET_SAMPLE_RATE


class VoiceCloningEngine:
    """Manages neural models for speaker embedding extraction and reference-conditioned speech synthesis."""

    _instance = None

    def __init__(self, device: str = "cpu"):
        self.device = device
        self.processor: Optional[SpeechT5Processor] = None
        self.tts_model: Optional[SpeechT5ForTextToSpeech] = None
        self.vocoder: Optional[SpeechT5HifiGan] = None
        self.speaker_encoder: Optional[EncoderClassifier] = None
        self.embedding_cache: Dict[str, torch.Tensor] = {}
        self.is_loaded = False

    @classmethod
    def get_instance(cls, device: str = "cpu") -> "VoiceCloningEngine":
        """Singleton accessor to prevent reloading weights repeatedly in web sessions."""
        if cls._instance is None:
            cls._instance = VoiceCloningEngine(device=device)
        return cls._instance

    def load_models(self) -> None:
        """Load pretrained models into memory."""
        if self.is_loaded:
            return

        print("[VocalSense AI] Loading neural models into memory...")
        start_time = time.time()

        # 1. Load SpeechBrain x-vector Speaker Encoder
        self.speaker_encoder = EncoderClassifier.from_hparams(
            source="speechbrain/spkrec-xvect-voxceleb",
            run_opts={"device": self.device},
        )

        # 2. Load SpeechT5 Processor, TTS Model, and Vocoder
        self.processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
        self.tts_model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
        self.tts_model.to(self.device)
        self.tts_model.eval()

        self.vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")
        self.vocoder.to(self.device)
        self.vocoder.eval()

        self.is_loaded = True
        elapsed = time.time() - start_time
        print(f"[VocalSense AI] All neural models loaded successfully in {elapsed:.2f}s on {self.device.upper()}.")

    def _compute_file_hash(self, file_path: str) -> str:
        """Compute MD5 hash of an audio file for caching speaker embeddings."""
        hasher = hashlib.md5()
        with open(file_path, "rb") as f:
            while chunk := f.read(65536):
                hasher.update(chunk)
        return hasher.hexdigest()

    def extract_speaker_embedding(self, audio_path: str) -> Tuple[torch.Tensor, str]:
        """Extract a 512-dimensional speaker embedding from a reference audio file.

        Uses caching to avoid redundant forward passes on the same audio sample.
        """
        if not self.is_loaded:
            self.load_models()

        file_hash = self._compute_file_hash(audio_path)
        if file_hash in self.embedding_cache:
            return self.embedding_cache[file_hash], "Cached speaker embedding reused."

        # Read 16 kHz audio
        sig, sr = sf.read(audio_path)
        if sr != TARGET_SAMPLE_RATE:
            import librosa
            sig = librosa.resample(sig, orig_sr=sr, target_sr=TARGET_SAMPLE_RATE)

        # Prepare tensor (batch_size=1, time)
        sig_tensor = torch.tensor(sig, dtype=torch.float32, device=self.device).unsqueeze(0)

        with torch.no_grad():
            emb = self.speaker_encoder.encode_batch(sig_tensor)  # Shape: (1, 1, 512)
            emb = emb.squeeze(1)  # Shape: (1, 512)
            # L2 normalization ensures stable conditioning in SpeechT5
            emb = torch.nn.functional.normalize(emb, p=2, dim=-1)

        self.embedding_cache[file_hash] = emb
        return emb, "Extracted fresh 512-dim speaker x-vector from reference audio."

    def clone_and_synthesize(
        self,
        text: str,
        reference_audio_path: str,
        language: str = "en",
        output_dir: str = "outputs",
    ) -> Tuple[bool, str, Optional[str], Dict[str, Any]]:
        """Perform end-to-end voice cloning and speech generation.

        Returns:
            (success, message, output_wav_path, metadata)
        """
        start_time = time.time()

        # Step 1: Validate and preprocess text
        is_text_valid, processed_text, text_meta = validate_and_preprocess_text(text, language=language)
        if not is_text_valid:
            return False, f"Text Validation Error: {processed_text}", None, {}

        # Step 2: Validate and preprocess reference audio
        is_audio_valid, processed_audio, audio_meta = validate_and_preprocess_audio(
            reference_audio_path, output_dir=output_dir
        )
        if not is_audio_valid:
            return False, f"Reference Audio Error: {processed_audio}", None, {}

        # Step 3: Ensure models are loaded
        try:
            if not self.is_loaded:
                self.load_models()
        except Exception as e:
            return False, f"Model Initialization Error: {str(e)}", None, {}

        # Step 4: Extract speaker embedding
        try:
            emb_start = time.time()
            speaker_embedding, emb_msg = self.extract_speaker_embedding(processed_audio)
            emb_time = time.time() - emb_start
        except Exception as e:
            return False, f"Speaker Embedding Extraction Failed: {str(e)}", None, {}

        # Step 5: Synthesize speech
        try:
            syn_start = time.time()
            inputs = self.processor(text=processed_text, return_tensors="pt").to(self.device)

            with torch.no_grad():
                speech_tensor = self.tts_model.generate_speech(
                    inputs["input_ids"],
                    speaker_embedding,
                    vocoder=self.vocoder,
                )

            syn_time = time.time() - syn_start
            audio_array = speech_tensor.cpu().numpy()

            # Save synthesized audio
            os.makedirs(output_dir, exist_ok=True)
            timestamp = int(time.time() * 1000)
            output_wav_path = os.path.join(output_dir, f"vocalsense_cloned_{timestamp}.wav")
            sf.write(output_wav_path, audio_array, samplerate=TARGET_SAMPLE_RATE, subtype="PCM_16")

            total_time = time.time() - start_time
            audio_duration = len(audio_array) / TARGET_SAMPLE_RATE
            real_time_factor = total_time / max(audio_duration, 0.01)

            # Persist successful synthesis event into SQLite database
            try:
                from src.database import save_recording
                save_recording(
                    operation_type="voice_cloning",
                    file_name=os.path.basename(output_wav_path),
                    duration_seconds=audio_duration,
                    sample_rate=TARGET_SAMPLE_RATE,
                    processing_duration_ms=total_time * 1000.0,
                    processing_status="success",
                    transcript=processed_text,
                    word_count=text_meta.get("word_count"),
                    character_count=text_meta.get("normalized_character_count"),
                    language_code=language,
                    stage_durations={
                        "embedding_extraction_ms": round(emb_time * 1000.0, 1),
                        "synthesis_ms": round(syn_time * 1000.0, 1),
                    },
                    estimated_wpm=round((text_meta.get("word_count", 0) / (audio_duration / 60.0)), 1) if audio_duration > 0 else None,
                )
            except Exception as db_err:
                print(f"[VocalSense AI Database Warning] Failed to log synthesis: {db_err}")

            metadata = {
                "input_text": processed_text,
                "raw_text": text,
                "reference_audio_path": reference_audio_path,
                "output_audio_path": output_wav_path,
                "audio_duration_seconds": round(audio_duration, 2),
                "sample_rate": TARGET_SAMPLE_RATE,
                "embedding_extraction_time_sec": round(emb_time, 2),
                "synthesis_time_sec": round(syn_time, 2),
                "total_processing_time_sec": round(total_time, 2),
                "real_time_factor": round(real_time_factor, 2),
                "device": self.device,
                "text_meta": text_meta,
                "audio_meta": audio_meta,
                "model_name": "SpeechT5-TTS + HiFi-GAN Vocoder (Microsoft) conditioned on SpeechBrain X-Vector",
            }

            return (
                True,
                f"Speech generated successfully in {total_time:.2f}s ({audio_duration:.2f}s audio duration).",
                output_wav_path,
                metadata,
            )

        except torch.cuda.OutOfMemoryError:
            return False, "Out of GPU memory error during synthesis. Try a shorter sentence.", None, {}
        except Exception as e:
            return False, f"Speech Synthesis Failed: {str(e)}", None, {}
