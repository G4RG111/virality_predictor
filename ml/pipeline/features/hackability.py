"""
Dimension 1: Hackability (weight: 25%)
SharkNinja's primary viral vector — community-discovered alternative uses.
Canonical example: Slushie machine used for cocktails, snow cones, frozen drinks.

Sub-signals:
  1. hack_phrase_rate         — fraction of reviews with hackability phrases
  2. experiment_intent_score  — first-person discovery language
  3. use_case_diversity_index — semantic cluster count of described uses
  4. cross_category_score     — mentions of items from other product categories
  5. ihut_unexpected_uses     — pre-launch signal from iHUT tester verbatims
"""
from __future__ import annotations

import re

from .base_extractor import (
    BaseDimensionExtractor,
    DimensionFeatures,
    IHUTChunk,
    Review,
    SignalEvidence,
)
from ..utils.lexicons import (
    HACKABILITY_PHRASES,
    EXPERIMENT_INTENT_PHRASES,
    contains_any,
    count_matches,
    get_matched_phrases,
)
from ..utils.text_preprocessor import normalize, sentence_split

# Cross-category keywords — product types that indicate alternative use context
_CROSS_CATEGORY_TERMS = [
    "blender", "juicer", "food processor", "cocktail shaker", "ice maker",
    "snow cone", "slushie", "smoothie", "margarita",
    "vacuum", "air purifier", "steamer", "humidifier",
    "hair dryer", "straightener", "curling iron",
    "pressure cooker", "slow cooker", "air fryer", "instant pot",
    "coffee maker", "espresso", "tea kettle",
    "like a", "acts as a", "functions as a", "works like a",
]

_MIN_CLUSTER_TEXTS = 8   # below this, skip embedding clustering (not enough data)
_N_CLUSTERS = 5          # target number of use-case clusters


class HackabilityExtractor(BaseDimensionExtractor):

    @property
    def dimension_name(self) -> str:
        return "hackability"

    @property
    def weight(self) -> float:
        return 0.23

    def extract(
        self,
        reviews: list[Review],
        ihut_chunks: list[IHUTChunk] | None = None,
    ) -> DimensionFeatures:
        signals: list[SignalEvidence] = []
        feature_vector: dict[str, float] = {}

        all_texts = [r.text for r in reviews]
        total = len(reviews)

        # ── Sub-signal 1: Hack phrase rate ──────────────────────────────────
        hack_texts: list[str] = []
        for review in reviews:
            matched = get_matched_phrases(review.text, HACKABILITY_PHRASES)
            if matched:
                hack_texts.append(review.text)
                signals.append(SignalEvidence(
                    signal_type="hack_phrase",
                    signal_value=", ".join(matched[:3]),
                    source_text=review.text[:200],
                    confidence=min(1.0, len(matched) * 0.3),
                ))

        hack_phrase_rate = self._safe_rate(len(hack_texts), total)
        feature_vector["hack_phrase_rate"] = hack_phrase_rate

        # ── Sub-signal 2: Experiment intent ──────────────────────────────────
        experiment_count = 0
        for review in reviews:
            if contains_any(review.text, EXPERIMENT_INTENT_PHRASES):
                experiment_count += 1
                signals.append(SignalEvidence(
                    signal_type="experiment_intent",
                    signal_value=get_matched_phrases(review.text, EXPERIMENT_INTENT_PHRASES)[0],
                    source_text=review.text[:200],
                    confidence=0.8,
                ))

        experiment_intent_score = self._safe_rate(experiment_count, total)
        feature_vector["experiment_intent_score"] = experiment_intent_score

        # ── Sub-signal 3: Cross-category mentions ────────────────────────────
        cross_cat_count = 0
        for review in reviews:
            lowered = review.text.lower()
            hits = [t for t in _CROSS_CATEGORY_TERMS if t in lowered]
            if hits:
                cross_cat_count += 1
                signals.append(SignalEvidence(
                    signal_type="cross_category",
                    signal_value=hits[0],
                    source_text=review.text[:200],
                    confidence=0.7,
                ))

        cross_category_score = self._safe_rate(cross_cat_count, total)
        feature_vector["cross_category_score"] = cross_category_score

        # ── Sub-signal 4: Use-case diversity (embedding clustering) ──────────
        use_case_diversity = 0.0
        if len(all_texts) >= _MIN_CLUSTER_TEXTS:
            try:
                from ..utils.embeddings import cluster_texts
                # Focus clustering on hack-mentioning texts for signal density
                cluster_source = hack_texts if len(hack_texts) >= _MIN_CLUSTER_TEXTS else all_texts
                labels, _ = cluster_texts(cluster_source, n_clusters=_N_CLUSTERS)
                n_distinct = len(set(labels))
                # Normalize: 1 cluster = 0, max clusters = 1.0
                use_case_diversity = (n_distinct - 1) / max(_N_CLUSTERS - 1, 1)
            except Exception:
                use_case_diversity = 0.0

        feature_vector["use_case_diversity_index"] = use_case_diversity

        # ── Sub-signal 5: iHUT pre-launch hackability ────────────────────────
        ihut_hack_score = 0.0
        if ihut_chunks:
            ihut_verbatims = [c for c in ihut_chunks if c.chunk_type == "verbatim"]
            ihut_hack_hits = [
                c for c in ihut_verbatims
                if contains_any(c.text, HACKABILITY_PHRASES + EXPERIMENT_INTENT_PHRASES)
            ]
            ihut_hack_score = self._safe_rate(len(ihut_hack_hits), max(len(ihut_verbatims), 1))
            for chunk in ihut_hack_hits[:5]:
                matched = get_matched_phrases(chunk.text, HACKABILITY_PHRASES)
                signals.append(SignalEvidence(
                    signal_type="ihut_hack_signal",
                    signal_value=", ".join(matched[:2]) if matched else "experiment_intent",
                    source_text=chunk.text[:200],
                    confidence=0.9,  # iHUT verbatims are high-quality pre-launch signal
                ))

        feature_vector["ihut_hack_score"] = ihut_hack_score

        # ── Composite raw score ───────────────────────────────────────────────
        # Weighted combination of sub-signals
        raw_score = self._clamp(
            hack_phrase_rate * 0.35
            + experiment_intent_score * 0.20
            + use_case_diversity * 0.20
            + cross_category_score * 0.15
            + ihut_hack_score * 0.10,
        )

        evidence_texts = [s.source_text for s in signals[:10]]

        return DimensionFeatures(
            dimension=self.dimension_name,
            weight=self.weight,
            raw_score=raw_score,
            feature_count=len(signals),
            top_signals=self._top_n_signals(signals),
            feature_vector=feature_vector,
            evidence_texts=evidence_texts,
        )
