"""
Hackability Intelligence Router.
Dedicated endpoints for the Hackability Feed, velocity, and breakout hacks.
"""
from __future__ import annotations

import sys
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import VibeScore, Review
from ..config import settings

router = APIRouter(prefix="/hackability", tags=["hackability"])


@router.get("/{product_id}/feed")
def get_hackability_feed(product_id: UUID, db: Session = Depends(get_db)):
    """
    All discovered use-case clusters from reviews, with verbatim quotes.
    Groups hacks semantically: e.g., 'Frozen Beverages', 'Beauty Treatments'.
    """
    score = (
        db.query(VibeScore)
        .filter(VibeScore.product_id == product_id, VibeScore.is_current == True)
        .first()
    )
    if not score:
        raise HTTPException(status_code=404, detail={"error": "no_score_computed"})

    ml_path = str(settings.ml_pipeline_path.resolve())
    if ml_path not in sys.path:
        sys.path.insert(0, ml_path)

    from pipeline.utils.lexicons import HACKABILITY_PHRASES, get_matched_phrases, contains_any, EXPERIMENT_INTENT_PHRASES
    from pipeline.utils.embeddings import embed_texts, cluster_texts

    db_reviews = db.query(Review).filter(Review.product_id == product_id).all()
    hack_reviews = [
        r for r in db_reviews
        if contains_any(r.review_text, HACKABILITY_PHRASES + EXPERIMENT_INTENT_PHRASES)
    ]

    if not hack_reviews:
        return {"product_id": str(product_id), "hack_clusters": [], "total_hack_mentions": 0}

    texts = [r.review_text for r in hack_reviews]
    n_clusters = min(6, len(texts))

    try:
        labels, centroids = cluster_texts(texts, n_clusters=n_clusters)
    except Exception:
        labels = [0] * len(texts)

    clusters: dict[int, list[str]] = {}
    for i, label in enumerate(labels):
        clusters.setdefault(int(label), []).append(texts[i][:300])

    return {
        "product_id": str(product_id),
        "total_hack_mentions": len(hack_reviews),
        "total_reviews": len(db_reviews),
        "hack_mention_rate": round(len(hack_reviews) / max(len(db_reviews), 1), 3),
        "hack_clusters": [
            {
                "cluster_id": cluster_id,
                "quote_count": len(quotes),
                "sample_quotes": quotes[:5],
                "matched_phrases": list({
                    phrase
                    for q in quotes
                    for phrase in get_matched_phrases(q, HACKABILITY_PHRASES)
                })[:5],
            }
            for cluster_id, quotes in sorted(clusters.items(), key=lambda x: -len(x[1]))
        ],
    }


@router.get("/{product_id}/velocity")
def get_hack_velocity(product_id: UUID, db: Session = Depends(get_db)):
    """
    Hack discovery velocity — new use-case clusters emerging over time.
    Requires date-stamped reviews.
    """
    from datetime import datetime
    from collections import defaultdict

    ml_path = str(settings.ml_pipeline_path.resolve())
    if ml_path not in sys.path:
        sys.path.insert(0, ml_path)

    from pipeline.utils.lexicons import HACKABILITY_PHRASES, EXPERIMENT_INTENT_PHRASES, contains_any

    db_reviews = db.query(Review).filter(Review.product_id == product_id).all()
    hack_reviews = [
        r for r in db_reviews
        if r.review_date and contains_any(r.review_text, HACKABILITY_PHRASES + EXPERIMENT_INTENT_PHRASES)
    ]

    by_month: dict[str, int] = defaultdict(int)
    for r in hack_reviews:
        month_key = str(r.review_date)[:7]  # YYYY-MM
        by_month[month_key] += 1

    return {
        "product_id": str(product_id),
        "total_hack_reviews": len(hack_reviews),
        "monthly_velocity": [
            {"month": month, "hack_mentions": count}
            for month, count in sorted(by_month.items())
        ],
    }


@router.get("/{product_id}/breakout")
def get_breakout_hacks(product_id: UUID, threshold: float = 0.05, db: Session = Depends(get_db)):
    """
    Hacks appearing in >= threshold (default 5%) of all reviews.
    These are the ideas most likely to spawn viral content.
    """
    ml_path = str(settings.ml_pipeline_path.resolve())
    if ml_path not in sys.path:
        sys.path.insert(0, ml_path)

    from pipeline.utils.lexicons import HACKABILITY_PHRASES, get_matched_phrases

    db_reviews = db.query(Review).filter(Review.product_id == product_id).all()
    total = len(db_reviews)
    if total == 0:
        return {"product_id": str(product_id), "breakout_hacks": []}

    phrase_counts: dict[str, int] = {}
    phrase_examples: dict[str, list[str]] = {}

    for review in db_reviews:
        matched = get_matched_phrases(review.review_text, HACKABILITY_PHRASES)
        for phrase in matched:
            phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
            if phrase not in phrase_examples:
                phrase_examples[phrase] = []
            if len(phrase_examples[phrase]) < 3:
                phrase_examples[phrase].append(review.review_text[:250])

    breakouts = [
        {
            "phrase": phrase,
            "mention_count": count,
            "mention_rate": round(count / total, 3),
            "sample_quotes": phrase_examples.get(phrase, []),
            "is_breakout": count / total >= threshold,
        }
        for phrase, count in sorted(phrase_counts.items(), key=lambda x: -x[1])
        if count / total >= threshold
    ]

    return {
        "product_id": str(product_id),
        "threshold": threshold,
        "total_reviews": total,
        "breakout_hacks": breakouts,
    }


@router.get("/compare")
def compare_hackability(
    product_ids: str,  # comma-separated UUIDs
    db: Session = Depends(get_db),
):
    """Hackability index comparison across products."""
    ids = [UUID(pid.strip()) for pid in product_ids.split(",") if pid.strip()]

    ml_path = str(settings.ml_pipeline_path.resolve())
    if ml_path not in sys.path:
        sys.path.insert(0, ml_path)

    from pipeline.utils.lexicons import HACKABILITY_PHRASES, EXPERIMENT_INTENT_PHRASES, contains_any
    from ..models import Product as ProductModel

    results = []
    for pid in ids:
        product = db.query(ProductModel).filter(ProductModel.id == pid).first()
        reviews = db.query(Review).filter(Review.product_id == pid).all()
        hack_count = sum(
            1 for r in reviews
            if contains_any(r.review_text, HACKABILITY_PHRASES + EXPERIMENT_INTENT_PHRASES)
        )
        total = len(reviews)
        results.append({
            "product_id": str(pid),
            "product_name": product.name if product else "Unknown",
            "total_reviews": total,
            "hack_mention_count": hack_count,
            "hackability_rate": round(hack_count / max(total, 1), 3),
        })

    return {"comparison": sorted(results, key=lambda x: -x["hackability_rate"])}
