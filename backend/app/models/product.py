from __future__ import annotations

import uuid
from datetime import datetime, date

from sqlalchemy import Column, String, Date, Numeric, Text, DateTime, func
from sqlalchemy.orm import relationship

from ..database import Base, GUID


class Product(Base):
    __tablename__ = "products"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    sku = Column(String(100), unique=True, nullable=True)
    category = Column(String(100), nullable=True)
    launch_date = Column(Date, nullable=True)
    market = Column(String(50), nullable=True)
    price_usd = Column(Numeric(10, 2), nullable=True)
    msrp_usd = Column(Numeric(10, 2), nullable=True)
    description = Column(Text, nullable=True)
    asin = Column(String(10), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    vibe_scores = relationship("VibeScore", back_populates="product", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    ingestion_jobs = relationship("IngestionJob", back_populates="product", cascade="all, delete-orphan")
    social_metrics = relationship("SocialMetric", back_populates="product", cascade="all, delete-orphan")
    outcome = relationship("ProductOutcome", back_populates="product", uselist=False, cascade="all, delete-orphan")
