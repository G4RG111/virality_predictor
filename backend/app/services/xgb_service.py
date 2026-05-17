"""
Backend service layer for XGBoost training.
Reads DB state, builds feature matrix, delegates to ml/pipeline/scoring/xgb_trainer.py.
"""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from ..config import settings
from ..models import Review, VibeScore, DimensionScore
from ..models.outcome import ProductOutcome

logger = logging.getLogger(__name__)


def _ml_path() -> Path:
    return settings.ml_pipeline_path.resolve()


def _models_dir() -> Path:
    return _ml_path() / "data" / "models"


def _ensure_ml_importable() -> None:
    ml = str(_ml_path())
    if ml not in sys.path:
        sys.path.insert(0, ml)


def build_feature_matrix(db: Session) -> tuple[list[dict], list[int], list[UUID]]:
    """
    Build (features, labels, product_ids) for all products with clear viral_proxy labels.
    Excludes products in the uncertain band (viral_proxy is None).
    """
    _ensure_ml_importable()
    from pipeline.scoring.xgb_trainer import build_feature_row

    outcomes = (
        db.query(ProductOutcome)
        .filter(ProductOutcome.viral_proxy.isnot(None))
        .all()
    )

    features, labels, product_ids = [], [], []
    for outcome in outcomes:
        pid = outcome.product_id

        # Get dimension raw scores from most recent VibeScore
        vs = (
            db.query(VibeScore)
            .filter(VibeScore.product_id == pid, VibeScore.is_current == True)
            .first()
        )
        if not vs:
            continue

        dim_scores = db.query(DimensionScore).filter(DimensionScore.vibe_score_id == vs.id).all()
        dimension_raw = {ds.dimension: float(ds.raw_score) for ds in dim_scores}

        # Engagement signals
        reviews = db.query(Review).filter(Review.product_id == pid).all()
        n = len(reviews)
        if n == 0:
            continue

        avg_helpful = sum(r.helpful_votes or 0 for r in reviews) / n
        creator_frac = sum(1 for r in reviews if r.reviewer_type == "creator") / n
        cutoff = datetime.now(timezone.utc).date() - timedelta(days=30)
        recent = sum(1 for r in reviews if r.review_date and r.review_date >= cutoff)
        velocity_30d = recent / 30.0

        row = build_feature_row(dimension_raw, avg_helpful, creator_frac, velocity_30d)
        features.append(row)
        labels.append(1 if outcome.viral_proxy else 0)
        product_ids.append(pid)

    return features, labels, product_ids


def run_training(db: Session) -> dict[str, Any]:
    """
    Full Phase 3 training pipeline:
    1. Auto-label all products
    2. Build feature matrix
    3. Train XGBoost
    4. Return metadata
    """
    from ..services.auto_labeler import label_all_products
    _ensure_ml_importable()
    from pipeline.scoring.xgb_trainer import train_xgb_model

    n_labeled = label_all_products(db)
    logger.info("Auto-labeled %d products", n_labeled)

    features, labels, _ = build_feature_matrix(db)
    if len(features) < 2:
        return {
            "trained": False,
            "error": f"Not enough labeled products to train (need ≥ 2, got {len(features)})",
            "n_labeled_products": n_labeled,
        }

    meta = train_xgb_model(features, labels, _models_dir())
    meta["trained"] = True
    meta["n_labeled_products"] = n_labeled
    return meta


def get_model_status(db: Session) -> dict[str, Any]:
    """Return current model status from training_meta.json if it exists."""
    meta_path = _models_dir() / "training_meta.json"
    n_labeled = db.query(ProductOutcome).filter(ProductOutcome.viral_proxy.isnot(None)).count()

    if not meta_path.exists():
        return {"trained": False, "n_labeled_products": n_labeled}

    meta = json.loads(meta_path.read_text())
    return {
        "trained": True,
        "model_version": meta.get("model_version"),
        "trained_at": meta.get("trained_at"),
        "auc": meta.get("auc"),
        "n_samples": meta.get("n_samples"),
        "n_viral": meta.get("n_viral"),
        "n_labeled_products": n_labeled,
    }


def predict_ml_score(dimension_raw: dict[str, float], db: Session) -> tuple[float | None, str | None]:
    """
    Predict ML score for one product using the saved XGBoost model.
    Returns (ml_score, ml_model_version) or (None, None) if model not trained.
    Also needs engagement features — reads from passed signals directly.
    """
    _ensure_ml_importable()
    from pipeline.scoring.xgb_trainer import build_feature_row, load_model_and_predict

    feature_row = build_feature_row(dimension_raw)
    score = load_model_and_predict(feature_row, _models_dir())
    if score is None:
        return None, None
    return score, "xgb-v1"
