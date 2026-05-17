from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import VibeScore, Product

router = APIRouter(prefix="/trends", tags=["trends"])


@router.get("/market/{market}")
def get_market_trend(market: str, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.market == market).all()
    result = []
    for product in products:
        scores = (
            db.query(VibeScore)
            .filter(VibeScore.product_id == product.id)
            .order_by(VibeScore.computed_at.asc())
            .all()
        )
        if scores:
            result.append({
                "product_id": str(product.id),
                "product_name": product.name,
                "latest_score": float(scores[-1].vibe_score),
                "score_band": scores[-1].score_band,
                "score_history": [float(s.vibe_score) for s in scores],
            })
    return {"market": market, "products": result}


@router.get("/category/{category}")
def get_category_trend(category: str, db: Session = Depends(get_db)):
    products = db.query(Product).filter(Product.category == category).all()
    scores = []
    for product in products:
        current = (
            db.query(VibeScore)
            .filter(VibeScore.product_id == product.id, VibeScore.is_current == True)
            .first()
        )
        if current:
            scores.append(float(current.vibe_score))

    return {
        "category": category,
        "product_count": len(products),
        "avg_vibe_score": round(sum(scores) / len(scores), 1) if scores else None,
        "min_score": min(scores) if scores else None,
        "max_score": max(scores) if scores else None,
    }


@router.get("/{product_id}")
def get_product_trend(product_id: UUID, db: Session = Depends(get_db)):
    scores = (
        db.query(VibeScore)
        .filter(VibeScore.product_id == product_id)
        .order_by(VibeScore.computed_at.asc())
        .all()
    )
    return {
        "product_id": str(product_id),
        "trend": [
            {
                "computed_at": s.computed_at.isoformat(),
                "vibe_score": float(s.vibe_score),
                "score_band": s.score_band,
                "confidence": s.confidence,
                "model_version": s.model_version,
            }
            for s in scores
        ],
    }
