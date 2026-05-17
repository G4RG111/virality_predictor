from __future__ import annotations

import asyncio
import re
import time
from dataclasses import dataclass

import httpx
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


class ScraperBlockedError(Exception):
    pass


@dataclass
class AmazonReview:
    review_text: str
    rating: float | None
    review_date: str | None
    verified_purchase: bool


def _parse_rating(text: str | None) -> float | None:
    if not text:
        return None
    m = re.search(r"(\d+(?:\.\d+)?)", text)
    return float(m.group(1)) if m else None


def _parse_page(html: str) -> list[AmazonReview]:
    soup = BeautifulSoup(html, "lxml")
    reviews: list[AmazonReview] = []

    for div in soup.select('[data-hook="review"]'):
        body_el = div.select_one('[data-hook="review-body"] span')
        if not body_el:
            continue
        text = body_el.get_text(strip=True)
        if not text:
            continue

        rating_el = div.select_one('[data-hook="review-star-rating"], [data-hook="cmps-review-star-rating"]')
        rating = _parse_rating(rating_el.get("class", [""])[0] if rating_el else None)
        if rating is None and rating_el:
            rating = _parse_rating(rating_el.get_text())

        date_el = div.select_one('[data-hook="review-date"]')
        date_text: str | None = None
        if date_el:
            raw = date_el.get_text(strip=True)
            # "Reviewed in the United States on January 15, 2024"
            m = re.search(r"on (.+)$", raw)
            date_text = m.group(1) if m else raw

        verified_el = div.select_one('[data-hook="avp-badge"]')
        verified = verified_el is not None

        reviews.append(AmazonReview(
            review_text=text,
            rating=rating,
            review_date=date_text,
            verified_purchase=verified,
        ))

    return reviews


def fetch_amazon_reviews(asin: str, max_pages: int = 10) -> list[dict]:
    """
    Synchronously scrape Amazon product reviews for a given ASIN.
    Returns a list of dicts compatible with the Review ORM model.
    Raises ScraperBlockedError if Amazon returns a CAPTCHA/bot-check page.
    """
    base_url = f"https://www.amazon.com/product-reviews/{asin}"
    all_reviews: list[dict] = []

    with httpx.Client(headers=HEADERS, follow_redirects=True, timeout=15) as client:
        for page in range(1, max_pages + 1):
            params = {
                "pageNumber": str(page),
                "reviewerType": "all_reviews",
                "sortBy": "recent",
            }
            try:
                resp = client.get(base_url, params=params)
            except httpx.RequestError as exc:
                raise ScraperBlockedError(f"Network error fetching page {page}: {exc}") from exc

            if resp.status_code == 503 or "api-services-support" in str(resp.url):
                raise ScraperBlockedError("Amazon returned a bot-check page. Try again later.")

            parsed = _parse_page(resp.text)

            # If page 1 returned nothing, assume blocked or invalid ASIN
            if page == 1 and not parsed:
                if "captcha" in resp.text.lower() or "robot" in resp.text.lower():
                    raise ScraperBlockedError("Amazon CAPTCHA detected. Try again in a few minutes.")
                # Could be a valid ASIN with 0 reviews — return empty
                break

            if not parsed:
                break  # No more pages

            for r in parsed:
                all_reviews.append({
                    "review_text": r.review_text,
                    "rating": r.rating,
                    "review_date": r.review_date,
                    "verified_purchase": r.verified_purchase,
                    "source": "amazon",
                    "market": "US",
                })

            if page < max_pages:
                time.sleep(2)  # Polite delay between pages

    return all_reviews
