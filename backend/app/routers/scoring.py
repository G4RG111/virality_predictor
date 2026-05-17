from __future__ import annotations

import logging
import sys
from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from ..database import get_db, SessionLocal
from ..models import Product, Review, VibeScore, DimensionScore, ShapExplanation
from ..schemas.vibe_score import VibeScoreResponse, LeaderboardEntry, CompareRequest, CompareResponse
from ..config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scoring", tags=["scoring"])


@router.post("/compute/{product_id}", status_code=202)
def trigger_scoring(
    product_id: UUID,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail={"error": "product_not_found"})

    reviews = db.query(Review).filter(Review.product_id == product_id).all()
    background_tasks.add_task(_run_scoring, product_id)

    return {"message": "Scoring job queued", "product_id": str(product_id), "review_count": len(reviews)}


def _run_scoring(product_id: UUID) -> None:
    """Run the full VIBE scoring pipeline with its own DB session."""
    db = SessionLocal()
    try:
        ml_path = str(settings.ml_pipeline_path.resolve())
        if ml_path not in sys.path:
            sys.path.insert(0, ml_path)

        from pipeline.features.base_extractor import Review as MLReview
        from pipeline.scoring.score_aggregator import compute_vibe_score
        from pipeline.explainability.shap_explainer import explain

        db_reviews = db.query(Review).filter(Review.product_id == product_id).all()
        ml_reviews = [
            MLReview(
                text=r.review_text,
                rating=float(r.rating) if r.rating else None,
                review_date=str(r.review_date) if r.review_date else None,
                source=r.source,
                market=r.market,
                helpful_votes=r.helpful_votes,
                verified_purchase=r.verified_purchase,
            )
            for r in db_reviews
        ]

        social_data: dict = {}
        try:
            from ..services.social_buzz_service import fetch_social_signals
            product = db.query(Product).filter(Product.id == product_id).first()
            if product:
                social_data = fetch_social_signals(product.name, product_id, db)
        except Exception as social_err:
            logger.warning("Social signal fetch failed, scoring without it: %s", social_err)

        result = compute_vibe_score(ml_reviews, social_data=social_data)

        db.query(VibeScore).filter(
            VibeScore.product_id == product_id,
            VibeScore.is_current == True,
        ).update({"is_current": False})

        ml_score = None
        ml_model_version = None
        try:
            from ..services.xgb_service import predict_ml_score
            ml_score, ml_model_version = predict_ml_score(result.dimension_raw, db)
        except Exception as xgb_err:
            logger.debug("XGBoost prediction skipped: %s", xgb_err)

        vibe_score_row = VibeScore(
            product_id=product_id,
            score_version=result.model_version,
            vibe_score=result.vibe_score,
            score_band=result.score_band,
            confidence=result.confidence,
            confidence_value=result.confidence_value,
            baseline_score=result.baseline_score,
            model_version=result.model_version,
            ml_score=ml_score,
            ml_model_version=ml_model_version,
            is_current=True,
            data_source_summary={"review_count": result.total_review_count},
        )
        db.add(vibe_score_row)
        db.flush()

        for dim, score in result.dimension_scores.items():
            dim_row = DimensionScore(
                vibe_score_id=vibe_score_row.id,
                dimension=dim,
                raw_score=result.dimension_raw[dim],
                normalized_score=score,
                weight=result.dimension_weights[dim],
                weighted_contribution=result.weighted_contributions[dim],
                top_signals=result.top_signals.get(dim),
                feature_vector=result.feature_vectors.get(dim),
                evidence_texts=result.evidence_texts.get(dim),
            )
            db.add(dim_row)

        explanation = explain(result, str(product_id))
        for contrib in explanation.contributions:
            shap_row = ShapExplanation(
                vibe_score_id=vibe_score_row.id,
                feature_name=contrib.dimension,
                shap_value=contrib.shap_value,
                feature_value=contrib.feature_value,
                feature_value_raw=contrib.feature_value_display,
                rank_order=str(contrib.rank),
                direction=contrib.direction,
            )
            db.add(shap_row)

        db.commit()
        logger.info("Scoring complete for product %s: %.1f [%s]", product_id, result.vibe_score, result.score_band)

    except Exception as e:
        db.rollback()
        logger.exception("Scoring failed for product %s: %s", product_id, e)
    finally:
        db.close()


@router.get("/leaderboard", response_model=list[LeaderboardEntry])
def get_leaderboard(db: Session = Depends(get_db)):
    from ..models import Product as ProductModel

    scores = (
        db.query(VibeScore, ProductModel)
        .join(ProductModel, VibeScore.product_id == ProductModel.id)
        .filter(VibeScore.is_current == True)
        .order_by(VibeScore.vibe_score.desc())
        .all()
    )

    return [
        LeaderboardEntry(
            rank=i + 1,
            product_id=score.product_id,
            product_name=product.name,
            market=product.market,
            vibe_score=float(score.vibe_score),
            score_band=score.score_band,
            confidence=score.confidence,
        )
        for i, (score, product) in enumerate(scores)
    ]


@router.post("/compare", response_model=CompareResponse)
def compare_products(payload: CompareRequest, db: Session = Depends(get_db)):
    results = []
    for pid in payload.product_ids:
        score = (
            db.query(VibeScore)
            .filter(VibeScore.product_id == pid, VibeScore.is_current == True)
            .first()
        )
        if score:
            results.append(VibeScoreResponse.model_validate(score))
    return CompareResponse(products=results)


@router.get("/model-status")
def get_model_status(db: Session = Depends(get_db)):
    from ..services.xgb_service import get_model_status
    return get_model_status(db)


@router.post("/train", status_code=202)
def trigger_training(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    background_tasks.add_task(_run_training)
    return {"message": "Training job queued", "status": "queued"}


def _run_training() -> None:
    db = SessionLocal()
    try:
        from ..services.xgb_service import run_training
        meta = run_training(db)
        logger.info("Training complete: %s", meta)
    except Exception as e:
        logger.exception("XGBoost training failed: %s", e)
    finally:
        db.close()
