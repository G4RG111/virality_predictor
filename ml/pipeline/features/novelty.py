"""
Dimension 4: Novelty (weight: 12%)
Measures how different the product feels vs. everything the reviewer has tried before.
"""
from __future__ import annotations

from .base_extractor import (
    BaseDimensionExtractor,
    DimensionFeatures,
    IHUTChunk,
    Review,
    SignalEvidence,
)
from ..utils.lexicons import NOVELTY_PHRASES, get_matched_phrases, contains_any


class NoveltyExtractor(BaseDimensionExtractor):

    @property
    def dimension_name(self) -> str:
        return "novelty"

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

        novelty_count = 0
        for review in reviews:
            matched = get_matched_phrases(review.text, NOVELTY_PHRASES)
            if matched:
                novelty_count += 1
                signals.append(SignalEvidence(
                    signal_type="novelty_phrase",
                    signal_value=matched[0],
                    source_text=review.text[:200],
                    confidence=0.85,
                ))

        novelty_phrase_rate = self._safe_rate(novelty_count, total)
        feature_vector["novelty_phrase_rate"] = novelty_phrase_rate

        # Semantic distance from category centroid (requires embedding model)
        category_distance = 0.0
        try:
            category_distance = _compute_category_distance(reviews)
        except Exception:
            pass
        feature_vector["category_distance_score"] = category_distance

        # iHUT "first use surprise" signals
        ihut_novelty = 0.0
        if ihut_chunks:
            ihut_verbatims = [c for c in ihut_chunks if c.chunk_type == "verbatim"]
            first_use_keywords = ["first time", "i didn't expect", "surprised me", "wow moment", "initial reaction"]
            ihut_novel_hits = sum(
                1 for c in ihut_verbatims if contains_any(c.text, first_use_keywords)
            )
            ihut_novelty = self._safe_rate(ihut_novel_hits, max(len(ihut_verbatims), 1))
        feature_vector["ihut_novelty_score"] = ihut_novelty

        raw_score = self._clamp(
            novelty_phrase_rate * 0.50
            + category_distance * 0.30
            + ihut_novelty * 0.20,
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


def _compute_category_distance(reviews: list[Review]) -> float:
    """
    Compute average cosine distance of review embeddings from a baseline
    'generic product review' centroid. Higher = more novel.
    """
    from ..utils.embeddings import embed_texts, cosine_similarity
    import numpy as np

    # Generic product review centroid (average language for a typical review)
    _GENERIC_CENTROID_SEED = [
        "This product works well and does what it says.",
        "Good quality for the price. Easy to use.",
        "Works as expected. Would recommend.",
        "Does the job. Nothing special but it works.",
    ]

    texts = [r.text[:512] for r in reviews[:100]]
    if not texts:
        return 0.0

    review_embeddings = embed_texts(texts)
    centroid_embeddings = embed_texts(_GENERIC_CENTROID_SEED)
    centroid = centroid_embeddings.mean(axis=0)

    similarities = [cosine_similarity(e, centroid) for e in review_embeddings]
    avg_similarity = float(np.mean(similarities))
    # Distance = 1 - similarity; normalize to [0, 1]
    return self._clamp(1.0 - avg_similarity) if False else max(0.0, 1.0 - avg_similarity)
