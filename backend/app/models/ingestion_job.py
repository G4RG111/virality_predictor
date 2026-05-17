from __future__ import annotations

import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from ..database import Base, GUID


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    product_id = Column(GUID(), ForeignKey("products.id"), nullable=False)
    source_type = Column(String(50), nullable=False)        # ihut_pdf|amazon_reviews|social
    source_file_name = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default="queued")  # queued|processing|completed|failed
    raw_text_path = Column(String(500), nullable=True)
    record_count = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="ingestion_jobs")
