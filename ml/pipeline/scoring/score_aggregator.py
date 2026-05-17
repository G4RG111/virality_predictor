"""
VIBE Score Aggregator.
Assembles dimension features into the final VIBE Score (0–100).
Phase 1: Weighted formula with analytic SHAP.
Phase 3: XGBoost model (toggled via USE_ML_MODEL env var).
Phase 4: Social Buzz as 9th dimension via build_extractors(social_data).
"""
from __future__ import annotations

import math
import os
from dataclasses import dataclass, field

from ..features.base_extractor import DimensionFeatures, IHUTChunk, Review
from ..features.feature_registry import DIMENSION_WEIGHTS, build_extractors


@dataclass
class VibeScoreResult:
    vibe_score: float                          # 0–100
    score_band: str                            # low | moderate | high | viral
    confidence: str                            # low | medium | high
    confidence_value: float                    # 0.0–1.0
    dimension_scores: dict[str, float]         # dimension → normalized score (0–100)
    dimension_raw: dict[str, float]            # dimension → raw score (0–1)
    dimension_weights: dict[str, float]        # dimension → weight
    weighted_contributions: dict[str, float]   # dimension → contribution to VIBE
    feature_vectors: dict[str, dict]           # dimension → sub-features
    top_signals: dict[str, list]               # dimension → top signal list
    evidence_texts: dict[str, list[str]]       # dimension → verbatim evidence
    total_review_count: int = 0
    model_version: str = "weighted-formula-v1"
    shap_values: dict[str, float] = field(default_factory=dict)
    baseline_score: float = 0.0


# Score bands calibrated to the actual raw-score distribution produced by this
# extractor suite.  The weighted sum of raw scores * 100 has a realistic ceiling
# of ~20 for a fully viral product (all dimensions firing), so bands are set
# relative to that ceiling rather than the theoretical 0-100 range.
_SCORE_BANDS = [
    (11.0, "viral"),
    (7.5, "high"),
    (4.5, "moderate"),
    (0, "low"),
]

# Reference means represent a "typical average SharkNinja product" against which
# SHAP values measure over/under-performance.  These are empirically set to the
# low end of observed raw scores so that viral-language reviews produce positive
# SHAP contributions and functional-only reviews produce near-zero or negative ones.
_REFERENCE_MEANS: dict[str, float] = {
    "hackability": 0.02,
    "emotional_intensity": 0.08,
    "shareability": 0.05,
    "novelty": 0.03,
    "creator_friendliness": 0.05,
    "review_momentum": 0.05,
    "recommendation_intent": 0.01,
    "price_wow": 0.08,
    "social_buzz": 0.10,
}


def _band(score: float) -> str:
    for threshold, band in _SCORE_BANDS:
        if score >= threshold:
            return band
    return "low"


def _confidence(total_reviews: int) -> tuple[str, float]:
    val = min(1.0, math.log10(max(total_reviews, 1)) / math.log10(500))
    if total_reviews < 50:
        return "low", val
    elif total_reviews < 200:
        return "medium", val
    return "high", val


def _normalize_dim_score(raw: float) -> float:
    """Scale raw [0,1] dimension score to [0,100] for display."""
    return round(raw * 100, 1)


def compute_vibe_score(
    reviews: list[Review],
    ihut_chunks: list[IHUTChunk] | None = None,
    social_data: dict | None = None,
) -> VibeScoreResult:
    """
    Run all 9 dimension extractors and compute the VIBE score.
    Pass social_data (from social_buzz_service) to include the Social Buzz dimension.
    Returns a fully populated VibeScoreResult.
    """
    dimension_features: dict[str, DimensionFeatures] = {}

    for extractor in build_extractors(social_data):
        features = extractor.extract(reviews, ihut_chunks)
        dimension_features[extractor.dimension_name] = features

    # Weighted composite
    vibe_raw = sum(
        f.raw_score * f.weight
        for f in dimension_features.values()
    )
    vibe_score = round(vibe_raw * 100, 1)

    # Analytic SHAP (Phase 1) — social_buzz auto-participates via DIMENSION_WEIGHTS
    baseline = sum(
        _REFERENCE_MEANS.get(dim, 0.2) * weight * 100
        for dim, weight in DIMENSION_WEIGHTS.items()
    )
    shap_values = {
        dim: round(
            (f.raw_score - _REFERENCE_MEANS.get(dim, 0.2)) * f.weight * 100, 2
        )
        for dim, f in dimension_features.items()
    }

    total_reviews = len(reviews)
    conf_label, conf_val = _confidence(total_reviews)

    return VibeScoreResult(
        vibe_score=vibe_score,
        score_band=_band(vibe_score),
        confidence=conf_label,
        confidence_value=conf_val,
        dimension_scores={dim: _normalize_dim_score(f.raw_score) for dim, f in dimension_features.items()},
        dimension_raw={dim: f.raw_score for dim, f in dimension_features.items()},
        dimension_weights={dim: f.weight for dim, f in dimension_features.items()},
        weighted_contributions={
            dim: round(f.raw_score * f.weight * 100, 2)
            for dim, f in dimension_features.items()
        },
        feature_vectors={dim: f.feature_vector for dim, f in dimension_features.items()},
        top_signals={
            dim: [
                {"type": s.signal_type, "value": s.signal_value, "confidence": s.confidence}
                for s in f.top_signals
            ]
            for dim, f in dimension_features.items()
        },
        evidence_texts={dim: f.evidence_texts for dim, f in dimension_features.items()},
        total_review_count=total_reviews,
        shap_values=shap_values,
        baseline_score=round(baseline, 1),
    )
