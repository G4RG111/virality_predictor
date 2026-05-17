from __future__ import annotations

import uuid
from sqlalchemy import Column, String, Numeric, Boolean, Date, Integer, Text, ForeignKey, DateTime, JSON, func
from sqlalchemy.orm import relationship

from ..database import Base, GUID


class Review(Base):
    __tablename__ = "reviews"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    product_id = Column(GUID(), ForeignKey("products.id"), nullable=False)
    source = Column(String(50), nullable=False, default="amazon")  # amazon|ihut|social
    external_id = Column(String(200), nullable=True)
    review_text = Column(Text, nullable=False)
    rating = Column(Numeric(3, 2), nullable=True)
    reviewer_type = Column(String(50), nullable=True)              # consumer|tester|creator
    review_date = Column(Date, nullable=True)
    market = Column(String(50), nullable=True)
    verified_purchase = Column(Boolean, nullable=False, default=False)
    helpful_votes = Column(Integer, nullable=False, default=0)
    ingestion_job_id = Column(GUID(), ForeignKey("ingestion_jobs.id"), nullable=True)
    embedding = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="reviews")
    signal_extractions = relationship("SignalExtraction", back_populates="review", cascade="all, delete-orphan")


class SignalExtraction(Base):
    __tablename__ = "signal_extractions"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    review_id = Column(GUID(), ForeignKey("reviews.id"), nullable=False)
    signal_type = Column(String(100), nullable=False)
    signal_value = Column(String(500), nullable=False)
    confidence = Column(Numeric(5, 4), nullable=False, default=1.0)
    extractor_version = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    review = relationship("Review", back_populates="signal_extractions")
