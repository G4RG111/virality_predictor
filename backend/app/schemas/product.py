from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    name: str
    sku: str | None = None
    category: str | None = None
    launch_date: date | None = None
    market: str | None = None
    price_usd: float | None = None
    msrp_usd: float | None = None
    description: str | None = None
    asin: str | None = None


class ProductUpdate(BaseModel):
    name: str | None = None
    sku: str | None = None
    category: str | None = None
    launch_date: date | None = None
    market: str | None = None
    price_usd: float | None = None
    msrp_usd: float | None = None
    description: str | None = None
    asin: str | None = None


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    sku: str | None
    category: str | None
    launch_date: date | None
    market: str | None
    price_usd: float | None
    msrp_usd: float | None
    description: str | None
    asin: str | None = None
    created_at: datetime


class ProductWithVibeResponse(ProductResponse):
    """Product with current VIBE score summary."""
    current_vibe_score: float | None = None
    score_band: str | None = None
    confidence: str | None = None
