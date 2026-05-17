from __future__ import annotations

import uuid
from sqlalchemy import Column, String, Integer, BigInteger, Numeric, Boolean, Date, JSON, ForeignKey
from sqlalchemy.orm import relationship

from ..database import Base, GUID


class SocialMetric(Base):
    __tablename__ = "social_metrics"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    product_id = Column(GUID(), ForeignKey("products.id"), nullable=False)
    platform = Column(String(50), nullable=False)           # tiktok|instagram|youtube
    metric_date = Column(Date, nullable=True)
    hashtag_count = Column(Integer, nullable=False, default=0)
    view_count = Column(BigInteger, nullable=False, default=0)
    engagement_rate = Column(Numeric(8, 6), nullable=False, default=0)
    creator_post_count = Column(Integer, nullable=False, default=0)
    viral_threshold_hit = Column(Boolean, nullable=False, default=False)
    raw_payload = Column(JSON, nullable=True)

    product = relationship("Product", back_populates="social_metrics")
