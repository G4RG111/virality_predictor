"""
Dimension 5: Creator Friendliness (weight: 12%)
Measures how naturally the product lends itself to content creation.
"""
from __future__ import annotations

from .base_extractor import (
    BaseDimensionExtractor,
    DimensionFeatures,
    IHUTChunk,
    Review,
    SignalEvidence,
)
from ..utils.lexicons import CREATOR_PHRASES, get_matched_phrases, contains_any

_VISUAL_APPEAL_TERMS = [
    "aesthetic", "aesthetically", "photogenic", "looks amazing",
    "beautiful", "looks great", "stunning", "gorgeous",
    "great for photos", "camera ready", "on camera", "film",
    "instagram worthy", "instagrammable", "tiktok worthy",
    "sleek", "stylish", "gorgeous design", "love the look",
]

_DEMO_POTENTIAL_TERMS = [
    "you have to see it", "watch it work", "see it in action",
    "results are visible", "dramatic result", "visual result",
    "shows immediately", "instant result", "before and after",
    "transformation", "see the difference",
]


class CreatorFriendlinessExtractor(BaseDimensionExtractor):

    @property
    def dimension_name(self) -> str:
        return "creator_friendliness"

    @property
    def weight(self) -> float:
        return 0.11

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

        creator_count = 0
        visual_count = 0
        demo_count = 0

        for review in reviews:
            text = review.text

            creator_matches = get_matched_phrases(text, CREATOR_PHRASES)
            if creator_matches:
                creator_count += 1
                signals.append(SignalEvidence(
                    signal_type="creator_mention",
                    signal_value=creator_matches[0],
                    source_text=text[:200],
                    confidence=0.9,
                ))

            if contains_any(text, _VISUAL_APPEAL_TERMS):
                visual_count += 1
                signals.append(SignalEvidence(
                    signal_type="visual_appeal",
                    signal_value=get_matched_phrases(text, _VISUAL_APPEAL_TERMS)[0],
                    source_text=text[:200],
                    confidence=0.75,
                ))

            if contains_any(text, _DEMO_POTENTIAL_TERMS):
                demo_count += 1
                signals.append(SignalEvidence(
                    signal_type="demo_potential",
                    signal_value=get_matched_phrases(text, _DEMO_POTENTIAL_TERMS)[0],
                    source_text=text[:200],
                    confidence=0.80,
                ))

        creator_rate = self._safe_rate(creator_count, total)
        visual_rate = self._safe_rate(visual_count, total)
        demo_rate = self._safe_rate(demo_count, total)

        feature_vector["creator_mention_rate"] = creator_rate
        feature_vector["visual_appeal_rate"] = visual_rate
        feature_vector["demo_potential_rate"] = demo_rate

        # iHUT aesthetic ratings (often captured in structured satisfaction tables)
        ihut_aesthetic = 0.0
        if ihut_chunks:
            ihut_verbatims = [c for c in ihut_chunks if c.chunk_type == "verbatim"]
            ihut_visual = sum(
                1 for c in ihut_verbatims
                if contains_any(c.text, _VISUAL_APPEAL_TERMS + ["appearance", "design", "look", "style"])
            )
            ihut_aesthetic = self._safe_rate(ihut_visual, max(len(ihut_verbatims), 1))
        feature_vector["ihut_aesthetic_score"] = ihut_aesthetic

        raw_score = self._clamp(
            creator_rate * 0.40
            + visual_rate * 0.30
            + demo_rate * 0.20
            + ihut_aesthetic * 0.10,
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
