"""Generate high-quality reference voice samples for VocalSense AI demonstrations."""
import os
import sys

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"
os.environ["USE_TF"] = "0"

import torch
import soundfile as sf
import numpy as np
from transformers import SpeechT5Processor, SpeechT5ForTextToSpeech, SpeechT5HifiGan

os.makedirs("samples", exist_ok=True)

try:
    print("Generating demo reference voices...")
    processor = SpeechT5Processor.from_pretrained("microsoft/speecht5_tts")
    model = SpeechT5ForTextToSpeech.from_pretrained("microsoft/speecht5_tts")
    vocoder = SpeechT5HifiGan.from_pretrained("microsoft/speecht5_hifigan")

    # Sample 1: Reference speaker 1
    torch.manual_seed(42)
    emb_male = torch.randn(1, 512)
    emb_male = torch.nn.functional.normalize(emb_male, p=2, dim=-1)

    text_male = "This is a clean authorized reference recording of speaker alpha for voice cloning testing."
    inputs_male = processor(text=text_male, return_tensors="pt")
    with torch.no_grad():
        speech_male = model.generate_speech(inputs_male["input_ids"], emb_male, vocoder=vocoder)

    male_path = os.path.join("samples", "sample_speaker_male.wav")
    sf.write(male_path, speech_male.numpy(), samplerate=16000)
    print(f"Generated male reference sample: {male_path} ({len(speech_male)/16000:.2f}s)")

    # Sample 2: Reference speaker 2
    torch.manual_seed(202)
    emb_female = torch.randn(1, 512)
    emb_female = torch.nn.functional.normalize(emb_female, p=2, dim=-1)

    text_female = "Hello and welcome. This recording serves as the authorized reference sample for speaker beta."
    inputs_female = processor(text=text_female, return_tensors="pt")
    with torch.no_grad():
        speech_female = model.generate_speech(inputs_female["input_ids"], emb_female, vocoder=vocoder)

    female_path = os.path.join("samples", "sample_speaker_female.wav")
    sf.write(female_path, speech_female.numpy(), samplerate=16000)
    print(f"Generated female reference sample: {female_path} ({len(speech_female)/16000:.2f}s)")

    print("Demo reference samples successfully created!")

except Exception as e:
    import traceback
    traceback.print_exc()
