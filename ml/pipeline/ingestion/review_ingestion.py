"""
Review ingestion — normalizes Amazon CSV/Excel/JSON into Review dataclass.
Auto-detects column schema via fuzzy matching.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..features.base_extractor import Review

# Candidate column names for each field (fuzzy mapped)
_TEXT_CANDIDATES = ["review_text", "body", "content", "text", "review", "comment", "reviewbody", "review_body", "reviewtext"]
_RATING_CANDIDATES = ["rating", "star_rating", "stars", "overall", "score", "review_rating", "starrating"]
_DATE_CANDIDATES = ["review_date", "date", "created_at", "review_time", "reviewdate", "timestamp"]
_SOURCE_CANDIDATES = ["source", "platform", "channel"]
_MARKET_CANDIDATES = ["market", "country", "region", "locale", "marketplace"]
_VERIFIED_CANDIDATES = ["verified_purchase", "verified", "is_verified"]
_HELPFUL_CANDIDATES = ["helpful_votes", "helpful", "upvotes", "likes"]
_ID_CANDIDATES = ["review_id", "id", "external_id", "asin", "product_id"]


def _match_column(columns: list[str], candidates: list[str]) -> str | None:
    col_lower = {c.lower().replace(" ", "_"): c for c in columns}
    for cand in candidates:
        if cand in col_lower:
            return col_lower[cand]
    return None


def _row_to_review(row: dict[str, Any], col_map: dict[str, str | None]) -> Review | None:
    text_col = col_map.get("text")
    if not text_col or not row.get(text_col):
        return None

    text = str(row[text_col]).strip()
    if len(text) < 5:
        return None

    rating = None
    if col_map.get("rating") and row.get(col_map["rating"]):
        try:
            rating = float(row[col_map["rating"]])
        except (ValueError, TypeError):
            pass

    date = None
    if col_map.get("date") and row.get(col_map["date"]):
        date = str(row[col_map["date"]])

    source = "amazon"
    if col_map.get("source") and row.get(col_map["source"]):
        source = str(row[col_map["source"]]).lower()

    market = None
    if col_map.get("market") and row.get(col_map["market"]):
        market = str(row[col_map["market"]])

    verified = False
    if col_map.get("verified") and row.get(col_map["verified"]):
        val = str(row[col_map["verified"]]).lower()
        verified = val in ("true", "1", "yes", "y", "verified")

    helpful = 0
    if col_map.get("helpful") and row.get(col_map["helpful"]):
        try:
            helpful = int(row[col_map["helpful"]])
        except (ValueError, TypeError):
            pass

    ext_id = None
    if col_map.get("id") and row.get(col_map["id"]):
        ext_id = str(row[col_map["id"]])

    return Review(
        text=text,
        rating=rating,
        review_date=date,
        source=source,
        market=market,
        verified_purchase=verified,
        helpful_votes=helpful,
        external_id=ext_id,
    )


def _build_col_map(columns: list[str]) -> dict[str, str | None]:
    return {
        "text": _match_column(columns, _TEXT_CANDIDATES),
        "rating": _match_column(columns, _RATING_CANDIDATES),
        "date": _match_column(columns, _DATE_CANDIDATES),
        "source": _match_column(columns, _SOURCE_CANDIDATES),
        "market": _match_column(columns, _MARKET_CANDIDATES),
        "verified": _match_column(columns, _VERIFIED_CANDIDATES),
        "helpful": _match_column(columns, _HELPFUL_CANDIDATES),
        "id": _match_column(columns, _ID_CANDIDATES),
    }


def ingest_csv(file_path: str | Path) -> list[Review]:
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError("pandas not installed") from e

    df = pd.read_csv(str(file_path), encoding="utf-8", on_bad_lines="skip")
    col_map = _build_col_map(list(df.columns))
    reviews = [_row_to_review(row, col_map) for row in df.to_dict(orient="records")]
    return [r for r in reviews if r is not None]


def ingest_excel(file_path: str | Path) -> list[Review]:
    try:
        import pandas as pd
    except ImportError as e:
        raise ImportError("pandas not installed") from e

    df = pd.read_excel(str(file_path))
    col_map = _build_col_map(list(df.columns))
    reviews = [_row_to_review(row, col_map) for row in df.to_dict(orient="records")]
    return [r for r in reviews if r is not None]


def ingest_json(file_path: str | Path) -> list[Review]:
    with open(str(file_path), encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        rows = data
    elif isinstance(data, dict) and "reviews" in data:
        rows = data["reviews"]
    else:
        rows = [data]

    if not rows:
        return []

    col_map = _build_col_map(list(rows[0].keys()))
    reviews = [_row_to_review(row, col_map) for row in rows]
    return [r for r in reviews if r is not None]


def ingest_reviews(file_path: str | Path) -> list[Review]:
    """Route to correct ingestion function based on file extension."""
    path = Path(file_path)
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return ingest_csv(path)
    elif suffix in (".xlsx", ".xls"):
        return ingest_excel(path)
    elif suffix == ".json":
        return ingest_json(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Expected .csv, .xlsx, .xls, or .json")
