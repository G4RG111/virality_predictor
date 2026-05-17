from __future__ import annotations

import sys
import logging
from typing import TYPE_CHECKING

from sqlalchemy.orm import Session

from ..config import settings

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def embed_reviews(review_ids: list, db: Session) -> int:
    """Compute sentence-transformer embeddings for a batch of reviews and persist them.

    Returns the count of successfully embedded reviews.
    Embeddings stored as JSONB float lists (384-dim, all-MiniLM-L6-v2).
    Gracefully skips if sentence-transformers is unavailable.
    """
    if not review_ids:
        return 0

    ml_path = str(settings.ml_pipeline_path.resolve())
    if ml_path not in sys.path:
        sys.path.insert(0, ml_path)

    try:
        from pipeline.utils.embeddings import embed_texts
    except Exception:
        logger.warning("sentence-transformers not available; skipping embedding step")
        return 0

    from ..models.review import Review

    reviews = db.query(Review).filter(Review.id.in_(review_ids), Review.embedding.is_(None)).all()
    if not reviews:
        return 0

    texts = [r.review_text for r in reviews]

    try:
        vectors = embed_texts(texts)  # shape (N, 384), normalized float32
    except Exception as exc:
        logger.error("Embedding computation failed: %s", exc)
        return 0

    count = 0
    for review, vec in zip(reviews, vectors):
        review.embedding = vec.tolist()
        count += 1

    db.commit()
    logger.info("Embedded %d reviews", count)
    return count


def semantic_search(query_text: str, product_id, db: Session, top_k: int = 20) -> list[dict]:
    """Return top-k reviews for a product ranked by cosine similarity to query_text.

    Falls back to empty list if embeddings unavailable.
    """
    ml_path = str(settings.ml_pipeline_path.resolve())
    if ml_path not in sys.path:
        sys.path.insert(0, ml_path)

    try:
        from pipeline.utils.embeddings import embed_single, cosine_similarity
        import numpy as np
    except Exception:
        return []

    from ..models.review import Review

    reviews = (
        db.query(Review)
        .filter(
            Review.product_id == product_id,
            Review.embedding.isnot(None),
        )
        .all()
    )

    if not reviews:
        return []

    query_vec = embed_single(query_text)
    matrix = np.array([r.embedding for r in reviews], dtype="float32")
    scores = cosine_similarity(query_vec, matrix)
    top_indices = np.argsort(scores)[::-1][:top_k]

    return [
        {
            "review_id": str(reviews[i].id),
            "text": reviews[i].review_text,
            "score": float(scores[i]),
            "source": reviews[i].source,
            "rating": float(reviews[i].rating) if reviews[i].rating else None,
            "review_date": reviews[i].review_date.isoformat() if reviews[i].review_date else None,
        }
        for i in top_indices
    ]
