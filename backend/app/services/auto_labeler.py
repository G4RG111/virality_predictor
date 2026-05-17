"""
Auto-labeling service: derives viral_proxy labels from review engagement signals.

Labels are derived without manual annotation using four signals:
  - avg_helpful_votes_per_review  (35%): community resonance
  - hackability_raw_score         (25%): alternative-use discovery
  - creator_review_fraction       (20%): creator attention
  - review_velocity_30d           (20%): momentum

Products scoring ≥ 0.65 → viral=True; ≤ 0.40 → viral=False; middle band excluded.
"""
from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from ..models import Product, Review, VibeScore, DimensionScore
from ..models.outcome import ProductOutcome

logger = logging.getLogger(__name__)

_SIGNAL_WEIGHTS = {
    "helpful_votes": 0.35,
    "hackability": 0.25,
    "creator_frac": 0.20,
    "velocity_30d": 0.20,
}

_VIRAL_THRESHOLD = 0.65
_STANDARD_THRESHOLD = 0.40


def _percentile_rank(value: float, all_values: list[float]) -> float:
    """Return rank of value in [0, 1] relative to all_values."""
    if not all_values or max(all_values) == min(all_values):
        return 0.5
    mn, mx = min(all_values), max(all_values)
    return (value - mn) / (mx - mn)


def _compute_raw_signals(product_id: UUID, db: Session) -> Optional[dict[str, float]]:
    """Compute raw signal values for one product. Returns None if no reviews."""
    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    if not reviews:
        return None

    n = len(reviews)
    avg_helpful = sum(r.helpful_votes or 0 for r in reviews) / n

    creator_count = sum(1 for r in reviews if r.reviewer_type == "creator")
    creator_frac = creator_count / n

    cutoff = datetime.now(timezone.utc).date() - timedelta(days=30)
    recent = sum(1 for r in reviews if r.review_date and r.review_date >= cutoff)
    velocity_30d = recent / 30.0

    # Hackability raw score from DimensionScore (most recent VibeScore)
    vs = (
        db.query(VibeScore)
        .filter(VibeScore.product_id == product_id, VibeScore.is_current == True)
        .first()
    )
    hack_score = 0.0
    if vs:
        ds = (
            db.query(DimensionScore)
            .filter(
                DimensionScore.vibe_score_id == vs.id,
                DimensionScore.dimension == "hackability",
            )
            .first()
        )
        if ds:
            hack_score = float(ds.raw_score)

    return {
        "helpful_votes": avg_helpful,
        "hackability": hack_score,
        "creator_frac": creator_frac,
        "velocity_30d": velocity_30d,
        "n_reviews": n,
    }


def derive_outcome(product_id: UUID, all_signals: dict[UUID, dict[str, float]], db: Session) -> ProductOutcome:
    """
    Compute viral_proxy label for one product given corpus-wide signal dicts.
    Upserts into product_outcomes table.
    """
    sig = all_signals[product_id]
    corpus = list(all_signals.values())

    engagement_signal = (
        _SIGNAL_WEIGHTS["helpful_votes"] * _percentile_rank(sig["helpful_votes"], [s["helpful_votes"] for s in corpus])
        + _SIGNAL_WEIGHTS["hackability"] * _percentile_rank(sig["hackability"], [s["hackability"] for s in corpus])
        + _SIGNAL_WEIGHTS["creator_frac"] * _percentile_rank(sig["creator_frac"], [s["creator_frac"] for s in corpus])
        + _SIGNAL_WEIGHTS["velocity_30d"] * _percentile_rank(sig["velocity_30d"], [s["velocity_30d"] for s in corpus])
    )

    if engagement_signal >= _VIRAL_THRESHOLD:
        viral_proxy: Optional[bool] = True
    elif engagement_signal <= _STANDARD_THRESHOLD:
        viral_proxy = False
    else:
        viral_proxy = None  # uncertain band — excluded from training

    existing = db.query(ProductOutcome).filter(ProductOutcome.product_id == product_id).first()
    if existing:
        existing.viral_proxy = viral_proxy
        existing.engagement_signal = engagement_signal
        existing.labeled_at = datetime.now(timezone.utc)
        existing.n_reviews_used = sig["n_reviews"]
        return existing

    outcome = ProductOutcome(
        product_id=product_id,
        viral_proxy=viral_proxy,
        engagement_signal=engagement_signal,
        label_method="auto_proxy_v1",
        n_reviews_used=sig["n_reviews"],
    )
    db.add(outcome)
    return outcome


def label_all_products(db: Session) -> int:
    """
    Run auto-labeling on all products that have at least one review.
    Returns the count of products labeled (viral=True or False; excludes uncertain).
    """
    products = db.query(Product).all()
    if not products:
        return 0

    # Gather raw signals for all products first (needed for percentile ranking)
    all_signals: dict[UUID, dict[str, float]] = {}
    for p in products:
        sig = _compute_raw_signals(p.id, db)
        if sig:
            all_signals[p.id] = sig

    if not all_signals:
        return 0

    labeled_count = 0
    for pid in all_signals:
        outcome = derive_outcome(pid, all_signals, db)
        if outcome.viral_proxy is not None:
            labeled_count += 1

    db.commit()
    logger.info("Auto-labeled %d products (of %d with reviews)", labeled_count, len(all_signals))
    return labeled_count
