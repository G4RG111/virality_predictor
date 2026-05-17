"""
Social Buzz dimension extractor.
Reads pre-fetched Google Trends + Reddit signals injected at instantiation.
Does not process review text — social data comes from the backend service layer.
"""
from __future__ import annotations

from .base_extractor import BaseDimensionExtractor, DimensionFeatures, IHUTChunk, Review, SignalEvidence


class SocialBuzzExtractor(BaseDimensionExtractor):
    """
    9th VIBE dimension: real-time social interest.
    Weighted at 8% — uses Google Trends interest + Reddit mention count/sentiment.
    Falls back to reference mean (0.30) when no social data is available.
    """

    def __init__(self, social_data: dict | None = None) -> None:
        self._data = social_data or {}

    @property
    def dimension_name(self) -> str:
        return "social_buzz"

    @property
    def weight(self) -> float:
        return 0.08

    def extract(
        self,
        reviews: list[Review],
        ihut_chunks: list[IHUTChunk] | None = None,
    ) -> DimensionFeatures:
        # Reference mean fallbacks — neutral contribution to SHAP when data unavailable
        trend_score = float(self._data.get("trend_score", 0.30))
        reddit_score = float(self._data.get("reddit_score", 0.30))
        reddit_sentiment = float(self._data.get("reddit_sentiment", 0.70))
        mention_count = int(self._data.get("mention_count", 0))
        top_posts: list[str] = self._data.get("top_posts", [])

        raw_score = self._clamp(0.6 * trend_score + 0.4 * reddit_score * reddit_sentiment)

        signals: list[SignalEvidence] = []
        if trend_score > 0.5:
            signals.append(SignalEvidence(
                signal_type="google_trends",
                signal_value=f"Trends interest: {round(trend_score * 100)}",
                source_text="Google Trends 12-month interest",
                confidence=trend_score,
            ))
        if reddit_score > 0.2:
            signals.append(SignalEvidence(
                signal_type="reddit_mentions",
                signal_value=f"{mention_count} Reddit mentions",
                source_text="Reddit search (last 30 days)",
                confidence=reddit_score,
            ))

        return DimensionFeatures(
            dimension="social_buzz",
            weight=self.weight,
            raw_score=raw_score,
            feature_count=mention_count,
            top_signals=self._top_n_signals(signals),
            feature_vector={
                "trend_score": round(trend_score, 4),
                "reddit_score": round(reddit_score, 4),
                "reddit_sentiment": round(reddit_sentiment, 4),
            },
            evidence_texts=top_posts[:5],
        )
