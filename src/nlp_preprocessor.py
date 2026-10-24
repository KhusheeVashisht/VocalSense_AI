"""NLP Preprocessing and Text Normalization Module for VocalSense AI.

Distinction between Preprocessing vs Deep Semantic NLP:
------------------------------------------------------
This module performs lexical and morphological text normalization (token expansion,
abbreviation replacement, number transliteration, and regex cleaning). This preparation
maps raw written text into phonetic/orthographic forms suitable for character-level
tokenization by SpeechT5's sentencepiece tokenizer.

This is fundamentally distinct from advanced semantic language understanding (e.g.,
contextual semantics, pragmatic intent parsing, or large language model reasoning),
as its goal is strictly acoustic-phonetic fidelity for text-to-speech synthesis.
"""

import re
from typing import Tuple, Dict, Any


SUPPORTED_LANGUAGES = {
    "en": {
        "name": "English",
        "code": "en",
        "description": "Native SpeechT5 training language (LibriTTS dataset). Full phonetic accuracy."
    }
}

# Common abbreviation expansions
ABBREVIATIONS = {
    r"\bDr\.(?=\s|$)": "Doctor",
    r"\bMr\.(?=\s|$)": "Mister",
    r"\bMrs\.(?=\s|$)": "Missus",
    r"\bMs\.(?=\s|$)": "Miss",
    r"\bProf\.(?=\s|$)": "Professor",
    r"\bvs\.(?=\s|$)": "versus",
    r"\betc\.(?=\s|$)": "etcetera",
    r"\be\.g\.(?=\s|$)": "for example",
    r"\bi\.e\.(?=\s|$)": "that is",
    r"\bAI\b": "A I",
    r"\bML\b": "M L",
    r"\bNLP\b": "N L P",
    r"\bTTS\b": "T T S",
    r"\bkg\b": "kilograms",
    r"\bkm\b": "kilometers",
    r"\bcm\b": "centimeters",
    r"\bapprox\.(?=\s|$)": "approximately",
}


def normalize_numbers_and_symbols(text: str) -> str:
    """Expand simple currency, percentages, and symbols to spoken English equivalents."""
    # Currency
    text = re.sub(r"\$(\d+(?:\.\d+)?)", r"\1 dollars", text)
    text = re.sub(r"£(\d+(?:\.\d+)?)", r"\1 pounds", text)
    text = re.sub(r"€(\d+(?:\.\d+)?)", r"\1 euros", text)
    # Percentage
    text = re.sub(r"(\d+)%", r"\1 percent", text)
    # Ampersand
    text = re.sub(r"\s*&\s*", " and ", text)
    # Plus / minus
    text = re.sub(r"\s*\+\s*", " plus ", text)
    return text


def normalize_text(text: str) -> str:
    """Normalize input text for TTS synthesis.

    Expands common abbreviations, currencies, numbers, strips unpronounceable
    characters, and compresses whitespace.
    """
    if not text:
        return ""

    normalized = text.strip()

    # Expand abbreviations
    for pattern, replacement in ABBREVIATIONS.items():
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

    # Normalize symbols and numbers
    normalized = normalize_numbers_and_symbols(normalized)

    # Remove non-standard unicode / emojis that break tokenizers
    normalized = re.sub(r"[^\w\s.,!?'\";:\-]", " ", normalized)

    # Normalize repeated punctuation and whitespace
    normalized = re.sub(r"\s+", " ", normalized)
    normalized = re.sub(r"\.+", ".", normalized)

    return normalized.strip()


def validate_and_preprocess_text(
    text: str,
    language: str = "en",
    min_length: int = 2,
    max_length: int = 500,
) -> Tuple[bool, str, Dict[str, Any]]:
    """Validate and preprocess input text.

    Returns:
        (is_valid, processed_text_or_error_message, metadata_dict)
    """
    if not text or not text.strip():
        return False, "Input text cannot be empty. Please enter a valid sentence.", {}

    raw_text = text.strip()

    if len(raw_text) < min_length:
        return False, f"Input text is too short ({len(raw_text)} chars). Minimum length is {min_length} characters.", {}

    if len(raw_text) > max_length:
        return (
            False,
            f"Input text exceeds the maximum safe limit ({len(raw_text)} / {max_length} characters) for CPU inference.",
            {},
        )

    # Check language support
    if language.lower() not in SUPPORTED_LANGUAGES:
        return (
            False,
            f"Language '{language}' is not natively supported by the SpeechT5 neural architecture. Currently supported: English ('en').",
            {},
        )

    normalized_text = normalize_text(raw_text)

    if not normalized_text:
        return False, "Input text contains only unsupported symbols or whitespace.", {}

    metadata = {
        "raw_character_count": len(raw_text),
        "normalized_character_count": len(normalized_text),
        "word_count": len(normalized_text.split()),
        "language": language,
        "language_name": SUPPORTED_LANGUAGES[language.lower()]["name"],
        "normalizations_applied": raw_text != normalized_text,
    }

    return True, normalized_text, metadata
