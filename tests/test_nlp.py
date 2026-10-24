"""Unit tests for NLP preprocessing and text validation."""
import pytest
from src.nlp_preprocessor import (
    normalize_text,
    validate_and_preprocess_text,
    normalize_numbers_and_symbols,
    SUPPORTED_LANGUAGES,
)


def test_normalize_abbreviations():
    raw = "Dr. Smith and Prof. Jones visited the AI lab with 5 kg of gear."
    expected = "Doctor Smith and Professor Jones visited the A I lab with 5 kilograms of gear."
    normalized = normalize_text(raw)
    assert "Doctor" in normalized
    assert "Professor" in normalized
    assert "A I" in normalized
    assert "kilograms" in normalized


def test_normalize_currency_and_symbols():
    raw = "The cost is $150 & 50% discount."
    normalized = normalize_numbers_and_symbols(raw)
    assert "150 dollars" in normalized
    assert "50 percent" in normalized
    assert " and " in normalized


def test_empty_input_validation():
    is_valid, msg, _ = validate_and_preprocess_text("")
    assert not is_valid
    assert "empty" in msg.lower()

    is_valid, msg, _ = validate_and_preprocess_text("   ")
    assert not is_valid


def test_too_short_input_validation():
    is_valid, msg, _ = validate_and_preprocess_text("a", min_length=2)
    assert not is_valid
    assert "too short" in msg.lower()


def test_too_long_input_validation():
    long_text = "word " * 120  # > 500 chars
    is_valid, msg, _ = validate_and_preprocess_text(long_text, max_length=500)
    assert not is_valid
    assert "exceeds" in msg.lower()


def test_unsupported_language_validation():
    is_valid, msg, _ = validate_and_preprocess_text("Bonjour le monde", language="fr")
    assert not is_valid
    assert "not natively supported" in msg.lower()


def test_valid_text_preprocessing():
    text = "Hello, world! Dr. Watson is here."
    is_valid, processed, meta = validate_and_preprocess_text(text, language="en")
    assert is_valid
    assert "Doctor Watson" in processed
    assert meta["language"] == "en"
    assert meta["word_count"] > 0
