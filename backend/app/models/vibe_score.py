from __future__ import annotations

import uuid
from sqlalchemy import Column, String, Numeric, Boolean, DateTime, ForeignKey, JSON, func
from sqlalchemy.orm import relationship

from ..database import Base, GUID


class VibeScore(Base):
    __tablename__ = "vibe_scores"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    product_id = Column(GUID(), ForeignKey("products.id"), nullable=False)
    score_version = Column(String(50), nullable=False)
    computed_at = Column(DateTime(timezone=True), server_default=func.now())
    vibe_score = Column(Numeric(5, 2), nullable=False)
    score_band = Column(String(20), nullable=False)         # low|moderate|high|viral
    confidence = Column(String(20), nullable=False)         # low|medium|high
    confidence_value = Column(Numeric(5, 4), nullable=False)
    baseline_score = Column(Numeric(5, 2), nullable=True)
    data_source_summary = Column(JSON, nullable=True)
    model_version = Column(String(50), nullable=False, default="weighted-formula-v1")
    ml_score = Column(Numeric(5, 2), nullable=True)
    ml_model_version = Column(String(50), nullable=True)
    is_current = Column(Boolean, nullable=False, default=True)

    product = relationship("Product", back_populates="vibe_scores")
    dimension_scores = relationship("DimensionScore", back_populates="vibe_score", cascade="all, delete-orphan")
    shap_explanations = relationship("ShapExplanation", back_populates="vibe_score", cascade="all, delete-orphan")


class DimensionScore(Base):
    __tablename__ = "dimension_scores"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    vibe_score_id = Column(GUID(), ForeignKey("vibe_scores.id"), nullable=False)
    dimension = Column(String(100), nullable=False)
    raw_score = Column(Numeric(8, 6), nullable=False)
    normalized_score = Column(Numeric(5, 2), nullable=False)
    weight = Column(Numeric(4, 3), nullable=False)
    weighted_contribution = Column(Numeric(5, 2), nullable=False)
    feature_count = Column(String(10), nullable=True)
    top_signals = Column(JSON, nullable=True)
    feature_vector = Column(JSON, nullable=True)
    evidence_texts = Column(JSON, nullable=True)

    vibe_score = relationship("VibeScore", back_populates="dimension_scores")


class ShapExplanation(Base):
    __tablename__ = "shap_explanations"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    vibe_score_id = Column(GUID(), ForeignKey("vibe_scores.id"), nullable=False)
    feature_name = Column(String(200), nullable=False)
    shap_value = Column(Numeric(10, 6), nullable=False)
    feature_value = Column(Numeric(10, 6), nullable=True)
    feature_value_raw = Column(String(500), nullable=True)
    rank_order = Column(String(10), nullable=True)
    direction = Column(String(10), nullable=True)           # positive|negative|neutral
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vibe_score = relationship("VibeScore", back_populates="shap_explanations")
