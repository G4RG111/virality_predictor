from __future__ import annotations

import uuid
from sqlalchemy import Column, Boolean, Numeric, String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from ..database import Base, GUID


class ProductOutcome(Base):
    __tablename__ = "product_outcomes"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    product_id = Column(GUID(), ForeignKey("products.id"), nullable=False, unique=True)
    viral_proxy = Column(Boolean, nullable=True)
    engagement_signal = Column(Numeric(6, 4), nullable=False)
    label_method = Column(String(50), nullable=False, default="auto_proxy_v1")
    labeled_at = Column(DateTime(timezone=True), server_default=func.now())
    n_reviews_used = Column(Integer, nullable=False, default=0)
    notes = Column(Text, nullable=True)

    product = relationship("Product", back_populates="outcome")
