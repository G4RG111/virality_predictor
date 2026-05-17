"""
Text preprocessing utilities shared across all dimension extractors.
"""
from __future__ import annotations

import re
import unicodedata


def normalize(text: str) -> str:
    """Lowercase, strip unicode noise, collapse whitespace."""
    text = unicodedata.normalize("NFKC", text)
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def clean_for_nlp(text: str) -> str:
    """
    Remove URLs, emails, and excessive punctuation while preserving
    emotionally expressive characters (!, ?, emojis) that carry signal.
    """
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = re.sub(r"\S+@\S+\.\S+", "", text)
    text = re.sub(r"[^\w\s!?.,'\"-]", " ", text, flags=re.UNICODE)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def exclamation_density(text: str) -> float:
    """Fraction of characters that are exclamation marks."""
    if not text:
        return 0.0
    return text.count("!") / max(len(text), 1)


def caps_ratio(text: str) -> float:
    """Fraction of alpha characters that are uppercase — measures shouting."""
    alpha = [c for c in text if c.isalpha()]
    if not alpha:
        return 0.0
    return sum(1 for c in alpha if c.isupper()) / len(alpha)


def sentence_split(text: str) -> list[str]:
    """Naive sentence splitter adequate for review text."""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    return [s.strip() for s in sentences if len(s.strip()) > 3]


def word_count(text: str) -> int:
    return len(text.split())


def contains_emoji(text: str) -> bool:
    """Detect presence of any emoji character."""
    emoji_pattern = re.compile(
        "[\U00002600-\U000027BF"
        "\U0001F300-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF]+",
        flags=re.UNICODE,
    )
    return bool(emoji_pattern.search(text))


def superlative_count(text: str) -> int:
    """Count superlative adjective endings (-est, most X)."""
    lowered = text.lower()
    superlatives = re.findall(r"\b\w+est\b|\bbest\b|\bmost \w+\b", lowered)
    return len(superlatives)


def extract_price_sentences(text: str) -> list[str]:
    """Return sentences that mention a price or price-related term."""
    price_keywords = {"price", "cost", "expensive", "cheap", "affordable", "worth", "penny", "value", "deal"}
    sentences = sentence_split(text)
    return [s for s in sentences if any(kw in s.lower() for kw in price_keywords)]


def extract_sentences_with_terms(text: str, terms: list[str]) -> list[str]:
    """Return sentences containing any of the given terms."""
    sentences = sentence_split(text)
    lowered_terms = [t.lower() for t in terms]
    return [s for s in sentences if any(t in s.lower() for t in lowered_terms)]
