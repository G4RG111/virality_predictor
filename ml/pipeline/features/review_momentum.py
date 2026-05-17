"""
Dimension 6: Review Momentum (weight: 10%)
Measures acceleration of review volume and rating trajectory.
Pre-launch: uses iHUT wave progression. Post-launch: Amazon review velocity.
"""
from __future__ import annotations

from collections import defaultdict
from datetime import datetime

from .base_extractor import (
    BaseDimensionExtractor,
    DimensionFeatures,
    IHUTChunk,
    Review,
    SignalEvidence,
)


class ReviewMomentumExtractor(BaseDimensionExtractor):

    @property
    def dimension_name(self) -> str:
        return "review_momentum"

    @property
    def weight(self) -> float:
        return 0.09

    def extract(
        self,
        reviews: list[Review],
        ihut_chunks: list[IHUTChunk] | None = None,
    ) -> DimensionFeatures:
        signals: list[SignalEvidence] = []
        feature_vector: dict[str, float] = {}

        # ── Temporal velocity (requires date-stamped reviews) ─────────────────
        dated = [r for r in reviews if r.review_date]
        velocity_ratio = 0.0
        rating_trajectory = 0.0

        if len(dated) >= 10:
            velocity_ratio, rating_trajectory = _compute_momentum(dated)

        feature_vector["velocity_ratio"] = velocity_ratio
        feature_vector["rating_trajectory"] = rating_trajectory

        # ── Review volume signal ──────────────────────────────────────────────
        # A large absolute volume is itself a momentum signal
        total = len(reviews)
        import math
        volume_score = min(1.0, math.log10(max(total, 1)) / math.log10(1000))
        feature_vector["volume_score"] = volume_score

        # ── Helpful vote concentration on early reviews ───────────────────────
        early_helpful_rate = 0.0
        if dated:
            sorted_by_date = sorted(dated, key=lambda r: r.review_date or "")
            early = sorted_by_date[:max(len(sorted_by_date) // 5, 1)]
            total_helpful = sum(r.helpful_votes for r in early)
            early_helpful_rate = min(1.0, total_helpful / max(len(early) * 10, 1))
        feature_vector["early_helpful_rate"] = early_helpful_rate

        if velocity_ratio > 1.5:
            signals.append(SignalEvidence(
                signal_type="velocity_acceleration",
                signal_value=f"{velocity_ratio:.2f}x",
                source_text=f"Review velocity ratio: {velocity_ratio:.2f} (recent vs prior period)",
                confidence=0.85,
            ))

        raw_score = self._clamp(
            velocity_ratio * 0.20
            + min(velocity_ratio / 10, 0.20)  # acceleration bonus
            + rating_trajectory * 0.20
            + volume_score * 0.25
            + early_helpful_rate * 0.15,
        )

        return DimensionFeatures(
            dimension=self.dimension_name,
            weight=self.weight,
            raw_score=raw_score,
            feature_count=len(signals),
            top_signals=signals,
            feature_vector=feature_vector,
        )


def _compute_momentum(dated_reviews: list[Review]) -> tuple[float, float]:
    """
    Returns (velocity_ratio, rating_trajectory).
    velocity_ratio: reviews_last_30d / reviews_prev_30d
    rating_trajectory: avg_rating (last 25%) - avg_rating (first 25%)
    """
    # Parse dates
    parsed: list[tuple[datetime, float | None]] = []
    for r in dated_reviews:
        try:
            dt = datetime.fromisoformat(str(r.review_date).replace("Z", "+00:00"))
            parsed.append((dt, r.rating))
        except (ValueError, TypeError):
            continue

    if not parsed:
        return 0.0, 0.0

    parsed.sort(key=lambda x: x[0])
    latest = parsed[-1][0]

    last_30 = sum(1 for dt, _ in parsed if (latest - dt).days <= 30)
    prev_30 = sum(1 for dt, _ in parsed if 30 < (latest - dt).days <= 60)
    velocity_ratio = last_30 / max(prev_30, 1)

    # Rating trajectory
    rated = [(dt, r) for dt, r in parsed if r is not None]
    if len(rated) >= 4:
        q = max(len(rated) // 4, 1)
        early_avg = sum(r for _, r in rated[:q]) / q
        late_avg = sum(r for _, r in rated[-q:]) / q
        # Normalize: +5 change → +1.0, -5 change → -1.0; clamp to [-1, 1]
        rating_trajectory = max(-1.0, min(1.0, (late_avg - early_avg) / 5.0))
        # Shift to [0, 1] for combination
        rating_trajectory = (rating_trajectory + 1.0) / 2.0
    else:
        rating_trajectory = 0.5  # neutral when not enough data

    return min(velocity_ratio, 5.0), rating_trajectory
