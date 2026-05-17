from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class IngestionJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    product_id: UUID
    source_type: str
    source_file_name: str | None
    status: str
    record_count: int | None
    error_message: str | None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime


class UploadResponse(BaseModel):
    job_id: UUID
    product_id: UUID
    source_type: str
    status: str
    message: str
