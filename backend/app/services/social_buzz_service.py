"""
Social Buzz Service — fetches Google Trends + Reddit signals.
Stores results in the existing social_metrics table (platform="google_trends"/"reddit").
Returns a dict compatible with SocialBuzzExtractor.
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

import requests
from sqlalchemy.orm import Session

from ..models.social_metric import SocialMetric

logger = logging.getLogger(__name__)

_CACHE_TTL_HOURS = 24
_REDDIT_LIMIT = 25
_REDDIT_MENTION_MAX = 50   # mention count that maps to reddit_score=1.0
_NEUTRAL_FALLBACK = {
    "trend_score": 0.30,
    "reddit_score": 0.30,
    "reddit_sentiment": 0.70,
    "mention_count": 0,
    "top_posts": [],
    "cached": False,
    "fetched_at": None,
}


def fetch_social_signals(
    product_name: str,
    product_id: UUID,
    db: Session,
) -> dict:
    """
    Return social signal dict for SocialBuzzExtractor.
    1. Check cache (social_metrics within last 24h).
    2. Fetch Google Trends + Reddit.
    3. Store results; return combined dict.
    Falls back to neutral values (0.30) on any failure.
    """
    cached = _load_cached(product_id, db)
    if cached is not None:
        return cached

    try:
        trend_score = _fetch_google_trends(product_name)
    except Exception as e:
        logger.warning("Google Trends fetch failed for %s: %s", product_name, e)
        trend_score = 0.30

    try:
        reddit_data = _fetch_reddit_mentions(product_name)
    except Exception as e:
        logger.warning("Reddit fetch failed for %s: %s", product_name, e)
        reddit_data = {"reddit_score": 0.30, "reddit_sentiment": 0.70, "mention_count": 0, "top_posts": []}

    result = {
        "trend_score": trend_score,
        "reddit_score": reddit_data["reddit_score"],
        "reddit_sentiment": reddit_data["reddit_sentiment"],
        "mention_count": reddit_data["mention_count"],
        "top_posts": reddit_data["top_posts"],
        "cached": False,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }

    _store_signals(product_id, trend_score, reddit_data, db)
    return result


def _load_cached(product_id: UUID, db: Session) -> dict | None:
    """Return cached social signals if a google_trends row exists within TTL."""
    cutoff = datetime.now(timezone.utc) - timedelta(hours=_CACHE_TTL_HOURS)
    row = (
        db.query(SocialMetric)
        .filter(
            SocialMetric.product_id == product_id,
            SocialMetric.platform == "google_trends",
            SocialMetric.metric_date >= cutoff.date(),
        )
        .order_by(SocialMetric.metric_date.desc())
        .first()
    )
    if row is None or not row.raw_payload:
        return None

    payload = row.raw_payload
    reddit_row = (
        db.query(SocialMetric)
        .filter(
            SocialMetric.product_id == product_id,
            SocialMetric.platform == "reddit",
            SocialMetric.metric_date >= cutoff.date(),
        )
        .order_by(SocialMetric.metric_date.desc())
        .first()
    )
    reddit_payload = reddit_row.raw_payload if reddit_row and reddit_row.raw_payload else {}

    return {
        "trend_score": float(payload.get("trend_score", 0.30)),
        "reddit_score": float(reddit_payload.get("reddit_score", 0.30)),
        "reddit_sentiment": float(reddit_payload.get("reddit_sentiment", 0.70)),
        "mention_count": int(reddit_payload.get("mention_count", 0)),
        "top_posts": reddit_payload.get("top_posts", []),
        "cached": True,
        "fetched_at": payload.get("fetched_at"),
    }


def _fetch_google_trends(product_name: str) -> float:
    """Return normalized trend score [0,1] from Google Trends (12-month interest)."""
    from pytrends.request import TrendReq  # lazy import — optional dependency

    keyword = product_name[:100]
    pt = TrendReq(hl="en-US", tz=360, timeout=(10, 25), retries=1, backoff_factor=0.5)
    pt.build_payload([keyword], timeframe="today 12-m", geo="")
    df = pt.interest_over_time()
    if df is None or df.empty or keyword not in df.columns:
        return 0.0
    return float(df[keyword].mean()) / 100.0


def _fetch_reddit_mentions(query: str) -> dict:
    """
    Search Reddit public API (no auth) for product mentions in the last month.
    Returns {reddit_score, reddit_sentiment, mention_count, top_posts}.
    """
    url = "https://www.reddit.com/search.json"
    params = {"q": query, "type": "link", "t": "month", "limit": _REDDIT_LIMIT, "sort": "relevance"}
    headers = {"User-Agent": "VIBE-Predictor/1.0 (social signal research tool)"}

    resp = requests.get(url, params=params, headers=headers, timeout=15)
    resp.raise_for_status()
    data = resp.json()

    posts = data.get("data", {}).get("children", [])
    mention_count = len(posts)
    reddit_score = min(1.0, mention_count / _REDDIT_MENTION_MAX)

    scores = [p["data"].get("score", 0) for p in posts if "data" in p]
    upvote_ratios = [p["data"].get("upvote_ratio", 0.5) for p in posts if "data" in p]
    reddit_sentiment = sum(upvote_ratios) / len(upvote_ratios) if upvote_ratios else 0.70

    top_posts = [
        p["data"].get("title", "")
        for p in posts[:5]
        if "data" in p and p["data"].get("title")
    ]

    return {
        "reddit_score": round(reddit_score, 4),
        "reddit_sentiment": round(reddit_sentiment, 4),
        "mention_count": mention_count,
        "top_posts": top_posts,
        "scores": scores,
    }


def _store_signals(
    product_id: UUID,
    trend_score: float,
    reddit_data: dict,
    db: Session,
) -> None:
    """Upsert Google Trends and Reddit rows into social_metrics."""
    today = date.today()
    fetched_at = datetime.now(timezone.utc).isoformat()

    # Google Trends row
    gt_row = (
        db.query(SocialMetric)
        .filter(
            SocialMetric.product_id == product_id,
            SocialMetric.platform == "google_trends",
            SocialMetric.metric_date == today,
        )
        .first()
    )
    if gt_row:
        gt_row.raw_payload = {"trend_score": trend_score, "fetched_at": fetched_at}
    else:
        db.add(SocialMetric(
            product_id=product_id,
            platform="google_trends",
            metric_date=today,
            raw_payload={"trend_score": trend_score, "fetched_at": fetched_at},
        ))

    # Reddit row
    rd_row = (
        db.query(SocialMetric)
        .filter(
            SocialMetric.product_id == product_id,
            SocialMetric.platform == "reddit",
            SocialMetric.metric_date == today,
        )
        .first()
    )
    reddit_payload = {
        "reddit_score": reddit_data["reddit_score"],
        "reddit_sentiment": reddit_data["reddit_sentiment"],
        "mention_count": reddit_data["mention_count"],
        "top_posts": reddit_data["top_posts"],
        "fetched_at": fetched_at,
    }
    if rd_row:
        rd_row.raw_payload = reddit_payload
    else:
        db.add(SocialMetric(
            product_id=product_id,
            platform="reddit",
            metric_date=today,
            raw_payload=reddit_payload,
        ))

    db.commit()


def get_latest_social_signals(product_id: UUID, db: Session) -> dict | None:
    """Read the most recently stored signals for a product (no live fetch)."""
    gt_row = (
        db.query(SocialMetric)
        .filter(SocialMetric.product_id == product_id, SocialMetric.platform == "google_trends")
        .order_by(SocialMetric.metric_date.desc())
        .first()
    )
    rd_row = (
        db.query(SocialMetric)
        .filter(SocialMetric.product_id == product_id, SocialMetric.platform == "reddit")
        .order_by(SocialMetric.metric_date.desc())
        .first()
    )

    if not gt_row and not rd_row:
        return None

    gt = gt_row.raw_payload or {} if gt_row else {}
    rd = rd_row.raw_payload or {} if rd_row else {}

    return {
        "trend_score": float(gt.get("trend_score", 0.30)),
        "reddit_score": float(rd.get("reddit_score", 0.30)),
        "reddit_sentiment": float(rd.get("reddit_sentiment", 0.70)),
        "mention_count": int(rd.get("mention_count", 0)),
        "top_posts": rd.get("top_posts", []),
        "cached": True,
        "fetched_at": gt.get("fetched_at") or rd.get("fetched_at"),
    }
