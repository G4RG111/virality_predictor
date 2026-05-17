from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class SignalDimensions(BaseModel):
    emotional_pull: float = Field(0.0, ge=0.0, le=1.0)
    creator_magnetism: float = Field(0.0, ge=0.0, le=1.0)
    novelty: float = Field(0.0, ge=0.0, le=1.0)
    social_currency: float = Field(0.0, ge=0.0, le=1.0)
    visual_demonstrability: float = Field(0.0, ge=0.0, le=1.0)
    friction: float = Field(0.0, ge=0.0, le=1.0)
    performative_utility: float = Field(0.0, ge=0.0, le=1.0)
    recommendation_energy: float = Field(0.0, ge=0.0, le=1.0)


class BriefAnalysisResponse(BaseModel):
    vibe_score: float = Field(..., ge=0.0, le=100.0)
    classification: str  # VIRAL_READY | VIRAL_POSSIBLE | NON_VIRAL
    culture_score: float = Field(..., ge=0.0, le=1.0)
    memory_score: float = Field(..., ge=0.0, le=1.0)
    top_matching_clusters: List[str]
    trend_alignment_reason: str
    closest_viral_archetype: str
    why_viral: List[str]
    why_fail: List[str]
    consumer_narrative: str
    consumer_language: List[str]
    signal_dimensions: SignalDimensions
