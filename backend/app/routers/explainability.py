from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import VibeScore, DimensionScore, ShapExplanation
from ..schemas.explainability import (
    ShapExplanationResponse,
    ShapContributionResponse,
    WaterfallEntry,
    KeyDriverResponse,
    KeyDriversResponse,
    EvidenceResponse,
)

router = APIRouter(prefix="/explain", tags=["explainability"])

# Inline display names to avoid importing the heavy ML pipeline on every request
_DISPLAY_NAMES: dict[str, str] = {
    "hackability": "Hackability",
    "emotional_intensity": "Emotional Intensity",
    "shareability": "Shareability",
    "novelty": "Novelty",
    "creator_friendliness": "Creator Friendliness",
    "review_momentum": "Review Momentum",
    "recommendation_intent": "Recommendation Intent",
    "price_wow": "Price-to-Wow",
    "social_buzz": "Social Buzz",
}


def _get_current_score_or_404(product_id: UUID, db: Session) -> VibeScore:
    score = (
        db.query(VibeScore)
        .filter(VibeScore.product_id == product_id, VibeScore.is_current == True)
        .first()
    )
    if not score:
        raise HTTPException(
            status_code=404,
            detail={"error": "no_score_computed", "message": "Run /scoring/compute/{product_id} first."},
        )
    return score


def _get_shap_rows(vibe_score_id: UUID, db: Session) -> list[ShapExplanation]:
    rows = db.query(ShapExplanation).filter(ShapExplanation.vibe_score_id == vibe_score_id).all()
    rows.sort(key=lambda r: -abs(float(r.shap_value)))
    return rows


@router.get("/{product_id}/shap", response_model=ShapExplanationResponse)
def get_shap_explanation(product_id: UUID, db: Session = Depends(get_db)):
    score = _get_current_score_or_404(product_id, db)
    shap_rows = _get_shap_rows(score.id, db)

    pos_names = [_DISPLAY_NAMES.get(r.feature_name, r.feature_name) for r in shap_rows if float(r.shap_value) > 0][:3]
    neg_names = [_DISPLAY_NAMES.get(r.feature_name, r.feature_name) for r in shap_rows if float(r.shap_value) < 0][:3]

    pos_str = ", ".join(pos_names) if pos_names else "none"
    neg_str = ", ".join(neg_names) if neg_names else "none"
    narrative = (
        f"VIBE Score of {float(score.vibe_score):.1f} [{score.score_band}]. "
        f"Positive drivers: {pos_str}. "
        f"Negative drag: {neg_str}."
    )

    return ShapExplanationResponse(
        product_id=str(product_id),
        vibe_score=float(score.vibe_score),
        baseline_score=float(score.baseline_score) if score.baseline_score else 0.0,
        narrative=narrative,
        top_positive_drivers=pos_names,
        top_negative_drivers=neg_names,
        model_version=score.model_version or "weighted-formula-v1",
        contributions=[
            ShapContributionResponse(
                dimension=r.feature_name,
                display_name=_DISPLAY_NAMES.get(r.feature_name, r.feature_name),
                shap_value=float(r.shap_value),
                feature_value=float(r.feature_value) if r.feature_value else 0.0,
                feature_value_display=r.feature_value_raw or f"{float(r.feature_value or 0):.3f}",
                direction=r.direction or "neutral",
                rank=int(r.rank_order) if r.rank_order else 0,
            )
            for r in shap_rows
        ],
    )


@router.get("/{product_id}/shap/waterfall", response_model=list[WaterfallEntry])
def get_waterfall_data(product_id: UUID, db: Session = Depends(get_db)):
    score = _get_current_score_or_404(product_id, db)
    shap_rows = db.query(ShapExplanation).filter(ShapExplanation.vibe_score_id == score.id).all()
    # Sort highest positive first, then negatives
    shap_rows.sort(key=lambda r: float(r.shap_value), reverse=True)

    entries: list[WaterfallEntry] = []
    baseline = float(score.baseline_score) if score.baseline_score else 0.0
    cumulative = baseline

    entries.append(WaterfallEntry(
        label="Baseline",
        value=baseline,
        start=0.0,
        end=baseline,
        cumulative=round(baseline, 2),
        type="baseline",
        feature_display=None,
    ))

    for row in shap_rows:
        val = float(row.shap_value)
        start = cumulative
        cumulative = round(cumulative + val, 2)
        entries.append(WaterfallEntry(
            label=_DISPLAY_NAMES.get(row.feature_name, row.feature_name),
            value=round(val, 2),
            start=round(start, 2),
            end=cumulative,
            cumulative=cumulative,
            type="positive" if val > 0 else ("negative" if val < 0 else "neutral"),
            feature_display=row.feature_value_raw,
        ))

    entries.append(WaterfallEntry(
        label="VIBE Score",
        value=float(score.vibe_score),
        start=0.0,
        end=float(score.vibe_score),
        cumulative=float(score.vibe_score),
        type="total",
        feature_display=None,
    ))

    return entries


@router.get("/{product_id}/key-drivers", response_model=KeyDriversResponse)
def get_key_drivers(product_id: UUID, db: Session = Depends(get_db)):
    score = _get_current_score_or_404(product_id, db)
    shap_rows = _get_shap_rows(score.id, db)

    pos = [r for r in shap_rows if float(r.shap_value) > 0]
    neg = sorted([r for r in shap_rows if float(r.shap_value) < 0], key=lambda r: float(r.shap_value))

    def _strength(v: float) -> str:
        return "strong" if abs(v) > 1.0 else ("moderate" if abs(v) > 0.3 else "slight")

    def _make_driver(rank: int, row: ShapExplanation, direction: str) -> KeyDriverResponse:
        name = _DISPLAY_NAMES.get(row.feature_name, row.feature_name)
        val = float(row.shap_value)
        raw = float(row.feature_value or 0)
        if direction == "positive":
            reason = f"{name} is firing above the baseline — raw score {raw:.2f} contributes +{val:.2f} to VIBE."
        else:
            reason = f"{name} is below baseline — raw score {raw:.2f} drags VIBE by {val:.2f}."
        return KeyDriverResponse(
            rank=rank,
            dimension=row.feature_name,
            impact=f"+{val:.2f}" if val > 0 else f"{val:.2f}",
            reason=reason,
            strength=_strength(val),
        )

    pos_drivers = [_make_driver(i + 1, r, "positive") for i, r in enumerate(pos[:5])]
    neg_drivers = [_make_driver(i + 1, r, "negative") for i, r in enumerate(neg[:5])]

    top_pos = pos_drivers[0].dimension if pos_drivers else "—"
    narrative = (
        f"VIBE Score {float(score.vibe_score):.1f} [{score.score_band}]. "
        f"Biggest upside: {_DISPLAY_NAMES.get(top_pos, top_pos)}. "
        f"{len(pos)} dimensions are pulling the score up; {len(neg)} are dragging it down."
    )

    return KeyDriversResponse(
        positive_drivers=pos_drivers,
        negative_drivers=neg_drivers,
        narrative=narrative,
    )


@router.get("/{product_id}/evidence", response_model=list[EvidenceResponse])
def get_evidence(product_id: UUID, db: Session = Depends(get_db)):
    _get_current_score_or_404(product_id, db)

    dim_scores = (
        db.query(DimensionScore)
        .join(VibeScore)
        .filter(VibeScore.product_id == product_id, VibeScore.is_current == True)
        .all()
    )

    return [
        EvidenceResponse(
            dimension=ds.dimension,
            display_name=_DISPLAY_NAMES.get(ds.dimension, ds.dimension),
            quotes=(ds.evidence_texts or [])[:10],
            signal_count=len(ds.top_signals or []),
        )
        for ds in dim_scores
    ]
