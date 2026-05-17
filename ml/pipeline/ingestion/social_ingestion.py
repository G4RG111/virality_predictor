"""
Social metrics ingestion — normalizes platform engagement data (TikTok, Instagram, etc.).
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class SocialMetric:
    platform: str
    metric_date: str | None
    hashtag_count: int = 0
    view_count: int = 0
    engagement_rate: float = 0.0
    creator_post_count: int = 0
    viral_threshold_hit: bool = False
    raw: dict[str, Any] | None = None


def ingest_social_json(file_path: str | Path) -> list[SocialMetric]:
    with open(str(file_path), encoding="utf-8") as f:
        data = json.load(f)

    rows = data if isinstance(data, list) else data.get("metrics", [data])
    metrics = []

    for row in rows:
        metrics.append(SocialMetric(
            platform=str(row.get("platform", row.get("source", "unknown"))).lower(),
            metric_date=str(row.get("date", row.get("metric_date", ""))),
            hashtag_count=int(row.get("hashtag_count", row.get("hashtags", 0))),
            view_count=int(row.get("view_count", row.get("views", 0))),
            engagement_rate=float(row.get("engagement_rate", row.get("engagement", 0.0))),
            creator_post_count=int(row.get("creator_post_count", row.get("creator_posts", 0))),
            viral_threshold_hit=bool(row.get("viral_threshold_hit", row.get("went_viral", False))),
            raw=row,
        ))

    return metrics
