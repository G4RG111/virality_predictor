"""
Social signal router — GET/POST endpoints for Google Trends + Reddit data.
"""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ..database import get_db
from ..models.product import Product
from ..services.social_buzz_service import fetch_social_signals, get_latest_social_signals

router = APIRouter()


class SocialSignalResponse(BaseModel):
    product_id: str
    trend_score: float
    reddit_score: float
    reddit_sentiment: float
    mention_count: int
    top_posts: list[str]
    cached: bool
    fetched_at: str | None


@router.get("/{product_id}", response_model=SocialSignalResponse)
def get_social_signals(product_id: UUID, db: Session = Depends(get_db)):
    """Return latest stored social signals for a product (no live fetch)."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail={"error": "Product not found"})

    data = get_latest_social_signals(product_id, db)
    if data is None:
        raise HTTPException(
            status_code=404,
            detail={"error": "No social signals yet. Score the product first or use POST /refresh."},
        )

    return SocialSignalResponse(product_id=str(product_id), **{k: v for k, v in data.items() if k != "cached" or True})


@router.post("/{product_id}/refresh", response_model=SocialSignalResponse)
def refresh_social_signals(product_id: UUID, db: Session = Depends(get_db)):
    """Force-fetch fresh Google Trends + Reddit signals and store them."""
    product = db.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail={"error": "Product not found"})

    # Bypass cache by deleting today's existing rows before fetching
    from datetime import date
    from ..models.social_metric import SocialMetric
    today = date.today()
    db.query(SocialMetric).filter(
        SocialMetric.product_id == product_id,
        SocialMetric.platform.in_(["google_trends", "reddit"]),
        SocialMetric.metric_date == today,
    ).delete(synchronize_session=False)
    db.commit()

    data = fetch_social_signals(product.name, product_id, db)
    return SocialSignalResponse(product_id=str(product_id), **{k: v for k, v in data.items()})
