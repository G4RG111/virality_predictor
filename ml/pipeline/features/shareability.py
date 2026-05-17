"""
Dimension 3: Shareability (weight: 17%)
Measures the product's "show it off" potential — performative utility.
"""
from __future__ import annotations

from .base_extractor import (
    BaseDimensionExtractor,
    DimensionFeatures,
    IHUTChunk,
    Review,
    SignalEvidence,
)
from ..utils.lexicons import (
    SOCIAL_PLATFORM_MENTIONS,
    TIKTOK_MADE_ME_BUY_PHRASES,
    SHOW_OTHERS_PHRASES,
    get_matched_phrases,
    contains_any,
)
from ..utils.text_preprocessor import contains_emoji


class ShareabilityExtractor(BaseDimensionExtractor):

    @property
    def dimension_name(self) -> str:
        return "shareability"

    @property
    def weight(self) -> float:
        return 0.16

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

        platform_count = 0
        tiktok_buy_count = 0
        show_others_count = 0
        emoji_count = 0

        for review in reviews:
            text = review.text

            platform_matches = get_matched_phrases(text, SOCIAL_PLATFORM_MENTIONS)
            if platform_matches:
                platform_count += 1
                signals.append(SignalEvidence(
                    signal_type="platform_mention",
                    signal_value=platform_matches[0],
                    source_text=text[:200],
                    confidence=0.95,
                ))

            tiktok_matches = get_matched_phrases(text, TIKTOK_MADE_ME_BUY_PHRASES)
            if tiktok_matches:
                tiktok_buy_count += 1
                signals.append(SignalEvidence(
                    signal_type="tiktok_made_me_buy",
                    signal_value=tiktok_matches[0],
                    source_text=text[:200],
                    confidence=1.0,
                ))

            show_matches = get_matched_phrases(text, SHOW_OTHERS_PHRASES)
            if show_matches:
                show_others_count += 1
                signals.append(SignalEvidence(
                    signal_type="show_others_intent",
                    signal_value=show_matches[0],
                    source_text=text[:200],
                    confidence=0.85,
                ))

            if contains_emoji(text):
                emoji_count += 1

        platform_rate = self._safe_rate(platform_count, total)
        tiktok_buy_rate = self._safe_rate(tiktok_buy_count, total)
        show_others_rate = self._safe_rate(show_others_count, total)
        emoji_rate = self._safe_rate(emoji_count, total)

        feature_vector["platform_mention_rate"] = platform_rate
        feature_vector["tiktok_made_me_buy_rate"] = tiktok_buy_rate
        feature_vector["show_others_intent_rate"] = show_others_rate
        feature_vector["emoji_rate"] = emoji_rate

        # iHUT: testers showing product to household members during test period
        ihut_share_score = 0.0
        if ihut_chunks:
            ihut_verbatims = [c for c in ihut_chunks if c.chunk_type == "verbatim"]
            ihut_share = sum(
                1 for c in ihut_verbatims if contains_any(c.text, SHOW_OTHERS_PHRASES)
            )
            ihut_share_score = self._safe_rate(ihut_share, max(len(ihut_verbatims), 1))
        feature_vector["ihut_share_score"] = ihut_share_score

        raw_score = self._clamp(
            platform_rate * 0.30
            + tiktok_buy_rate * 0.30
            + show_others_rate * 0.25
            + min(emoji_rate * 0.5, 0.10)
            + ihut_share_score * 0.05,
        )

        return DimensionFeatures(
            dimension=self.dimension_name,
            weight=self.weight,
            raw_score=raw_score,
            feature_count=len(signals),
            top_signals=self._top_n_signals(signals),
            feature_vector=feature_vector,
            evidence_texts=[s.source_text for s in signals[:8]],
        )
