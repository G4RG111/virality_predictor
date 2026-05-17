"""
Dimension 8: Price-to-Wow Excitement (weight: 2%)
Measures value-surprise — the emotional reaction when a product exceeds price expectations.
"""
from __future__ import annotations

from .base_extractor import (
    BaseDimensionExtractor,
    DimensionFeatures,
    IHUTChunk,
    Review,
    SignalEvidence,
)
from ..utils.lexicons import PRICE_WOW_PHRASES, get_matched_phrases
from ..utils.text_preprocessor import extract_price_sentences


class PriceWowExtractor(BaseDimensionExtractor):

    @property
    def dimension_name(self) -> str:
        return "price_wow"

    @property
    def weight(self) -> float:
        return 0.02

    def extract(
        self,
        reviews: list[Review],
        ihut_chunks: list[IHUTChunk] | None = None,
    ) -> DimensionFeatures:
        signals: list[SignalEvidence] = []
        feature_vector: dict[str, float] = {}
        total = len(reviews)

        if total == 0:
            return DimensionFeatures(dimension=self.dimension_name, weight=self.weight, raw_score=0.0, feature_count=0)

        price_wow_count = 0
        for review in reviews:
            matched = get_matched_phrases(review.text, PRICE_WOW_PHRASES)
            if matched:
                price_wow_count += 1
                signals.append(SignalEvidence(
                    signal_type="price_wow",
                    signal_value=matched[0],
                    source_text=review.text[:200],
                    confidence=0.80,
                ))

        price_wow_rate = self._safe_rate(price_wow_count, total)
        feature_vector["price_wow_rate"] = price_wow_rate

        # Sentiment on price-mentioning sentences
        price_sentence_sentiment = 0.5  # neutral default
        all_price_sentences = []
        for review in reviews[:50]:
            all_price_sentences += extract_price_sentences(review.text)

        if all_price_sentences:
            try:
                price_sentence_sentiment = _sentiment_on_sentences(all_price_sentences)
            except Exception:
                pass
        feature_vector["price_sentence_sentiment"] = price_sentence_sentiment

        raw_score = self._clamp(
            price_wow_rate * 0.60
            + price_sentence_sentiment * 0.40,
        )

        return DimensionFeatures(
            dimension=self.dimension_name,
            weight=self.weight,
            raw_score=raw_score,
            feature_count=len(signals),
            top_signals=self._top_n_signals(signals),
            feature_vector=feature_vector,
            evidence_texts=[s.source_text for s in signals[:5]],
        )


def _sentiment_on_sentences(sentences: list[str]) -> float:
    """Returns average positive sentiment (0-1) on price-mentioning sentences."""
    try:
        from transformers import pipeline
        classifier = pipeline(
            "sentiment-analysis",
            model="distilbert-base-uncased-finetuned-sst-2-english",
        )
        results = classifier(sentences[:30])
        scores = [
            r["score"] if r["label"] == "POSITIVE" else 1.0 - r["score"]
            for r in results
        ]
        return sum(scores) / len(scores) if scores else 0.5
    except Exception:
        return 0.5
