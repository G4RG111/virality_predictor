from __future__ import annotations

from uuid import UUID
from pydantic import BaseModel


class ShapContributionResponse(BaseModel):
    dimension: str
    display_name: str
    shap_value: float
    feature_value: float
    feature_value_display: str
    direction: str
    rank: int


class ShapExplanationResponse(BaseModel):
    product_id: str
    vibe_score: float
    baseline_score: float
    narrative: str
    top_positive_drivers: list[str]
    top_negative_drivers: list[str]
    model_version: str
    contributions: list[ShapContributionResponse]


class WaterfallEntry(BaseModel):
    label: str
    value: float
    start: float | None = None
    end: float | None = None
    cumulative: float
    type: str                    # baseline | positive | negative | neutral | total
    feature_display: str | None = None


class KeyDriverResponse(BaseModel):
    rank: int
    dimension: str
    impact: str
    reason: str
    strength: str                # strong | moderate | slight


class KeyDriversResponse(BaseModel):
    positive_drivers: list[KeyDriverResponse]
    negative_drivers: list[KeyDriverResponse]
    narrative: str


class EvidenceResponse(BaseModel):
    dimension: str
    display_name: str
    quotes: list[str]
    signal_count: int
