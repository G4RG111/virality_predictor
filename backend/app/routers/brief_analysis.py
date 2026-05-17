"""Product brief analysis router — stateless, no DB, synchronous."""
from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi import APIRouter, Form, HTTPException

from ..schemas.brief_analysis import BriefAnalysisResponse
from ..services.brief_analysis import analyze_brief

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/analyze", tags=["brief-analysis"])


@router.post("/brief", response_model=BriefAnalysisResponse)
def run_brief_analysis(
    product_name: str = Form(...),
    description: str = Form(""),
    category: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    target_audience: Optional[str] = Form(None),
    tags: str = Form("[]"),       # JSON-encoded list sent by the frontend
    demo_mode: bool = Form(False),
) -> BriefAnalysisResponse:
    try:
        tags_list: list[str] = json.loads(tags)
    except (json.JSONDecodeError, TypeError):
        tags_list = []

    try:
        return analyze_brief(
            product_name=product_name,
            description=description,
            category=category,
            price=price,
            target_audience=target_audience,
            tags=tags_list,
            demo_mode=demo_mode,
        )
    except Exception as exc:
        logger.exception("Brief analysis failed: %s", exc)
        raise HTTPException(
            status_code=500,
            detail={"error": "analysis_failed", "message": str(exc)},
        )
