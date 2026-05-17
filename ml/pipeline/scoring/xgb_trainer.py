"""
XGBoost trainer for VIBE virality prediction (Phase 3).

Pure ML module — no DB or HTTP dependencies.
Accepts feature DataFrames and returns training metadata.
Model saved as JSON to ml/data/models/vibe_xgb_v1.json.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import StratifiedKFold, cross_val_score
from xgboost import XGBClassifier

logger = logging.getLogger(__name__)

_FEATURE_COLS = [
    "hackability_raw",
    "emotional_intensity_raw",
    "shareability_raw",
    "novelty_raw",
    "creator_friendliness_raw",
    "review_momentum_raw",
    "recommendation_intent_raw",
    "price_wow_raw",
    "helpful_votes_avg",
    "creator_frac",
    "velocity_30d",
]

_DIMENSION_MAP = {
    "hackability": "hackability_raw",
    "emotional_intensity": "emotional_intensity_raw",
    "shareability": "shareability_raw",
    "novelty": "novelty_raw",
    "creator_friendliness": "creator_friendliness_raw",
    "review_momentum": "review_momentum_raw",
    "recommendation_intent": "recommendation_intent_raw",
    "price_wow": "price_wow_raw",
}


def build_feature_row(
    dimension_raw: dict[str, float],
    helpful_votes_avg: float = 0.0,
    creator_frac: float = 0.0,
    velocity_30d: float = 0.0,
) -> dict[str, float]:
    """Build a single feature dict for inference (one product)."""
    row: dict[str, float] = {col: 0.0 for col in _FEATURE_COLS}
    for dim, col in _DIMENSION_MAP.items():
        row[col] = float(dimension_raw.get(dim, 0.0))
    row["helpful_votes_avg"] = float(helpful_votes_avg)
    row["creator_frac"] = float(creator_frac)
    row["velocity_30d"] = float(velocity_30d)
    return row


def train_xgb_model(
    features: list[dict[str, float]],
    labels: list[int],
    models_dir: Path,
) -> dict[str, Any]:
    """
    Train an XGBoost classifier on the provided feature/label pairs.

    Args:
        features: list of feature dicts (from build_feature_row)
        labels: list of 0/1 integers (same order as features)
        models_dir: directory to save model + metadata JSON files

    Returns:
        dict with keys: auc, n_samples, n_viral, model_path, trained_at
    """
    if len(features) < 2:
        raise ValueError(f"Need at least 2 labeled samples to train; got {len(features)}")

    X = pd.DataFrame(features, columns=_FEATURE_COLS).fillna(0.0)
    y = np.array(labels, dtype=int)

    n_viral = int(y.sum())
    n_standard = len(y) - n_viral
    scale_pos_weight = n_standard / max(n_viral, 1)

    clf = XGBClassifier(
        max_depth=4,
        learning_rate=0.05,
        n_estimators=200,
        scale_pos_weight=scale_pos_weight,
        eval_metric="auc",
        random_state=42,
        verbosity=0,
        use_label_encoder=False,
    )

    # Cross-validation (use min splits to handle small datasets)
    n_splits = min(5, len(y))
    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
    cv_scores = cross_val_score(clf, X, y, cv=cv, scoring="roc_auc")
    mean_auc = float(np.mean(cv_scores))

    # Final fit on full dataset
    clf.fit(X, y)

    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "vibe_xgb_v1.json"
    clf.save_model(str(model_path))

    feature_names_path = models_dir / "feature_names.json"
    feature_names_path.write_text(json.dumps(_FEATURE_COLS))

    from datetime import datetime, timezone
    trained_at = datetime.now(timezone.utc).isoformat()

    meta = {
        "model_version": "xgb-v1",
        "trained_at": trained_at,
        "auc": round(mean_auc, 4),
        "n_samples": len(y),
        "n_viral": n_viral,
        "model_path": str(model_path),
        "feature_cols": _FEATURE_COLS,
    }
    (models_dir / "training_meta.json").write_text(json.dumps(meta, indent=2))

    logger.info(
        "XGBoost trained: n=%d viral=%d auc=%.3f saved=%s",
        len(y), n_viral, mean_auc, model_path,
    )
    return meta


def load_model_and_predict(feature_row: dict[str, float], models_dir: Path) -> float | None:
    """
    Load the saved XGBoost model and predict viral probability for one product.
    Returns None if model file does not exist.
    """
    model_path = models_dir / "vibe_xgb_v1.json"
    if not model_path.exists():
        return None

    clf = XGBClassifier()
    clf.load_model(str(model_path))

    X = pd.DataFrame([feature_row], columns=_FEATURE_COLS).fillna(0.0)
    prob = float(clf.predict_proba(X)[0][1])
    return round(prob * 100, 1)
