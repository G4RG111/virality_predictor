from __future__ import annotations

from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Product, VibeScore
from ..schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductWithVibeResponse
from ..schemas.vibe_score import VibeScoreResponse, VibeScoreHistoryResponse

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductWithVibeResponse])
def list_products(
    market: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    score_band: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    query = db.query(Product)
    if market:
        query = query.filter(Product.market == market)
    if category:
        query = query.filter(Product.category == category)

    products = query.offset(offset).limit(limit).all()
    results = []
    for product in products:
        current_score = (
            db.query(VibeScore)
            .filter(VibeScore.product_id == product.id, VibeScore.is_current == True)
            .first()
        )
        data = ProductWithVibeResponse.model_validate(product)
        if current_score:
            data.current_vibe_score = float(current_score.vibe_score)
            data.score_band = current_score.score_band
            data.confidence = current_score.confidence
            if score_band and current_score.score_band != score_band:
                continue
        elif score_band:
            continue
        results.append(data)

    return results


@router.post("/", response_model=ProductResponse, status_code=201)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(**payload.model_dump(exclude_none=True))
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}", response_model=ProductWithVibeResponse)
def get_product(product_id: UUID, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail={"error": "product_not_found", "id": str(product_id)})

    current_score = (
        db.query(VibeScore)
        .filter(VibeScore.product_id == product_id, VibeScore.is_current == True)
        .first()
    )
    data = ProductWithVibeResponse.model_validate(product)
    if current_score:
        data.current_vibe_score = float(current_score.vibe_score)
        data.score_band = current_score.score_band
        data.confidence = current_score.confidence
    return data


@router.patch("/{product_id}", response_model=ProductResponse)
def update_product(product_id: UUID, payload: ProductUpdate, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail={"error": "product_not_found"})

    for field, value in payload.model_dump(exclude_none=True).items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


@router.get("/{product_id}/vibe-history", response_model=VibeScoreHistoryResponse)
def get_vibe_history(product_id: UUID, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail={"error": "product_not_found"})

    scores = (
        db.query(VibeScore)
        .filter(VibeScore.product_id == product_id)
        .order_by(VibeScore.computed_at.desc())
        .all()
    )
    return VibeScoreHistoryResponse(
        product_id=product_id,
        history=[VibeScoreResponse.model_validate(s) for s in scores],
    )
