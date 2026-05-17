from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..database import get_db
from ..models.review import Review
from ..models.product import Product
from ..services.ingestion_service import semantic_search

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.get("/{product_id}")
def list_reviews(
    product_id: UUID,
    source: str | None = Query(None, description="Filter by source: amazon|ihut|social"),
    min_rating: float | None = Query(None, ge=1, le=5),
    max_rating: float | None = Query(None, ge=1, le=5),
    market: str | None = Query(None),
    has_embedding: bool | None = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail={"error": "product_not_found"})

    q = db.query(Review).filter(Review.product_id == product_id)

    if source:
        q = q.filter(Review.source == source)
    if min_rating is not None:
        q = q.filter(Review.rating >= min_rating)
    if max_rating is not None:
        q = q.filter(Review.rating <= max_rating)
    if market:
        q = q.filter(Review.market == market)
    if has_embedding is True:
        q = q.filter(Review.embedding.isnot(None))
    if has_embedding is False:
        q = q.filter(Review.embedding.is_(None))

    total = q.count()
    reviews = q.order_by(desc(Review.review_date), desc(Review.created_at)).offset(offset).limit(limit).all()

    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "reviews": [_serialize(r) for r in reviews],
    }


@router.get("/{product_id}/search")
def search_reviews(
    product_id: UUID,
    q: str = Query(..., min_length=3, description="Semantic search query"),
    top_k: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail={"error": "product_not_found"})

    results = semantic_search(q, product_id, db, top_k=top_k)
    return {"query": q, "results": results}


@router.get("/{product_id}/stats")
def review_stats(product_id: UUID, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail={"error": "product_not_found"})

    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    if not reviews:
        return {"total": 0}

    ratings = [float(r.rating) for r in reviews if r.rating is not None]
    sources = {}
    markets = {}
    embedded = 0
    for r in reviews:
        sources[r.source] = sources.get(r.source, 0) + 1
        if r.market:
            markets[r.market] = markets.get(r.market, 0) + 1
        if r.embedding:
            embedded += 1

    return {
        "total": len(reviews),
        "embedded": embedded,
        "avg_rating": round(sum(ratings) / len(ratings), 2) if ratings else None,
        "by_source": sources,
        "by_market": markets,
    }


def _serialize(r: Review) -> dict:
    return {
        "id": str(r.id),
        "source": r.source,
        "review_text": r.review_text,
        "rating": float(r.rating) if r.rating else None,
        "review_date": r.review_date.isoformat() if r.review_date else None,
        "market": r.market,
        "verified_purchase": r.verified_purchase,
        "helpful_votes": r.helpful_votes,
        "reviewer_type": r.reviewer_type,
        "has_embedding": r.embedding is not None,
    }
