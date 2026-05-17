"""
Dimension 7: Recommendation Intent (weight: 5%)
Word-of-mouth spread, gifting intent, NPS proxy.
"""
from __future__ import annotations

from .base_extractor import (
    BaseDimensionExtractor,
    DimensionFeatures,
    IHUTChunk,
    Review,
    SignalEvidence,
)
from ..utils.lexicons import WOM_PHRASES, get_matched_phrases, contains_any


class RecommendationIntentExtractor(BaseDimensionExtractor):

    @property
    def dimension_name(self) -> str:
        return "recommendation_intent"

    @property
    def weight(self) -> float:
        return 0.04

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

        wom_count = 0
        gift_count = 0
        recommend_count = 0

        gift_terms = ["gift", "gifting", "buying for", "perfect present", "birthday", "christmas"]
        recommend_terms = ["would recommend", "highly recommend", "100% recommend", "would buy again", "five stars"]

        for review in reviews:
            text = review.text
            matched = get_matched_phrases(text, WOM_PHRASES)
            if matched:
                wom_count += 1
                signals.append(SignalEvidence(
                    signal_type="wom_phrase",
                    signal_value=matched[0],
                    source_text=text[:200],
                    confidence=0.85,
                ))
            if contains_any(text, gift_terms):
                gift_count += 1
            if contains_any(text, recommend_terms):
                recommend_count += 1

        wom_rate = self._safe_rate(wom_count, total)
        gift_rate = self._safe_rate(gift_count, total)
        recommend_rate = self._safe_rate(recommend_count, total)

        feature_vector["wom_rate"] = wom_rate
        feature_vector["gift_intent_rate"] = gift_rate
        feature_vector["recommend_rate"] = recommend_rate

        ihut_recommend = 0.0
        if ihut_chunks:
            ihut_verbatims = [c for c in ihut_chunks if c.chunk_type == "verbatim"]
            ihut_rec = sum(1 for c in ihut_verbatims if contains_any(c.text, WOM_PHRASES + recommend_terms))
            ihut_recommend = self._safe_rate(ihut_rec, max(len(ihut_verbatims), 1))
        feature_vector["ihut_recommend_score"] = ihut_recommend

        raw_score = self._clamp(
            wom_rate * 0.40
            + gift_rate * 0.25
            + recommend_rate * 0.25
            + ihut_recommend * 0.10,
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
