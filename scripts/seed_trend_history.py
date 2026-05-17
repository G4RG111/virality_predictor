#!/usr/bin/env python3
"""
Seed historical VIBE score entries so the Trends tab shows meaningful trajectories.

For each product that already has a current VIBE score, this script inserts
3 backdated score rows (30d, 14d, 7d ago) with slightly lower scores, simulating
a product building viral momentum toward the current value.

Usage (from vibe-predictor/ root):
  python scripts/seed_trend_history.py
  python scripts/seed_trend_history.py --reset   # remove previously seeded history first
"""
from __future__ import annotations

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
BACKEND_PATH = REPO_ROOT / "backend"
sys.path.insert(0, str(BACKEND_PATH))

try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger("seed_trend_history")


def _band(score: float) -> str:
    if score >= 11.0:
        return "viral"
    if score >= 7.5:
        return "high"
    if score >= 4.5:
        return "moderate"
    return "low"


# How much to subtract from current score at each lookback point.
# Positive = the product was lower in the past (upward trend story).
_LOOKBACK_DELTAS: list[tuple[int, float]] = [
    (30, 2.2),   # 30 days ago: significantly lower
    (14, 1.3),   # 14 days ago: still gaining
    (7,  0.5),   # 7 days ago: almost there
    # day 0 = the existing is_current=True row
]


def seed(reset: bool = False) -> None:
    import sqlalchemy as sa
    from sqlalchemy.orm import sessionmaker

    db_url = os.environ.get(
        "DATABASE_URL", "postgresql://vibe:vibepass@localhost:5432/vibe_db"
    )
    db_url = db_url.replace("@db:", "@localhost:")

    engine = sa.create_engine(db_url, pool_pre_ping=True)
    SessionFactory = sessionmaker(bind=engine)

    log.info("Connecting to: %s", db_url.split("@")[-1])

    from app.models.vibe_score import VibeScore

    with SessionFactory() as db:
        if reset:
            log.info("Removing previously seeded historical entries (is_current=False)...")
            deleted = (
                db.query(VibeScore)
                .filter(VibeScore.is_current.is_(False))
                .delete(synchronize_session=False)
            )
            db.commit()
            log.info("Removed %d historical rows.", deleted)

        current_scores = (
            db.query(VibeScore)
            .filter(VibeScore.is_current.is_(True))
            .all()
        )

        if not current_scores:
            log.error("No current VIBE scores found. Run seed_demo.py first.")
            return

        log.info("Found %d products with current scores.", len(current_scores))
        now = datetime.now(tz=timezone.utc)

        for score in current_scores:
            current_val = float(score.vibe_score)
            log.info(
                "  Product %s: current=%.1f [%s]",
                score.product_id, current_val, score.score_band,
            )

            for days_ago, delta in _LOOKBACK_DELTAS:
                historical_val = max(0.1, round(current_val - delta, 2))
                historical_band = _band(historical_val)
                historical_at = now - timedelta(days=days_ago)

                # Skip if a historical row for this product+date already exists
                exists = (
                    db.query(VibeScore)
                    .filter(
                        VibeScore.product_id == score.product_id,
                        VibeScore.is_current.is_(False),
                        VibeScore.computed_at >= historical_at - timedelta(hours=12),
                        VibeScore.computed_at <= historical_at + timedelta(hours=12),
                    )
                    .first()
                )
                if exists:
                    log.info("    -%dd row already exists, skipping.", days_ago)
                    continue

                row = VibeScore(
                    product_id=score.product_id,
                    score_version=score.score_version,
                    vibe_score=historical_val,
                    score_band=historical_band,
                    confidence=score.confidence,
                    confidence_value=score.confidence_value,
                    baseline_score=score.baseline_score,
                    model_version=score.model_version,
                    is_current=False,
                )
                # Override the server_default timestamp to the backdate
                db.add(row)
                db.flush()

                # Update computed_at directly after flush so we have the row id
                db.execute(
                    sa.text(
                        "UPDATE vibe_scores SET computed_at = :ts WHERE id = :id"
                    ),
                    {"ts": historical_at, "id": row.id},
                )

                log.info(
                    "    -%dd: %.1f [%s]  computed_at=%s",
                    days_ago, historical_val, historical_band,
                    historical_at.strftime("%Y-%m-%d"),
                )

            db.commit()

        log.info("\nTrend history seeded. Open http://localhost:3000/trends to verify.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed VIBE score trend history")
    parser.add_argument("--reset", action="store_true", help="Remove all is_current=False rows first")
    args = parser.parse_args()
    seed(reset=args.reset)
