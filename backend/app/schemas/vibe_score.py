from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DimensionScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    dimension: str
    normalized_score: float
    weight: float
    weighted_contribution: float
    top_signals: list[dict] | None = None
    feature_vector: dict | None = None
    evidence_texts: list[str] | None = None


class VibeScoreResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    product_id: UUID
    vibe_score: float
    score_band: str
    confidence: str
    confidence_value: float
    baseline_score: float | None
    model_version: str
    computed_at: datetime
    is_current: bool
    dimension_scores: list[DimensionScoreResponse] = []


class VibeScoreHistoryResponse(BaseModel):
    product_id: UUID
    history: list[VibeScoreResponse]


class LeaderboardEntry(BaseModel):
    rank: int
    product_id: UUID
    product_name: str
    market: str | None
    vibe_score: float
    score_band: str
    confidence: str


class CompareRequest(BaseModel):
    product_ids: list[UUID]


class CompareResponse(BaseModel):
    products: list[VibeScoreResponse]
