"""
Feature registry — single source of truth for dimension → extractor mapping.
Weights must sum to 1.0.
"""
from __future__ import annotations

from .base_extractor import BaseDimensionExtractor
from .hackability import HackabilityExtractor
from .emotional_intensity import EmotionalIntensityExtractor
from .shareability import ShareabilityExtractor
from .novelty import NoveltyExtractor
from .creator_friendliness import CreatorFriendlinessExtractor
from .review_momentum import ReviewMomentumExtractor
from .recommendation_intent import RecommendationIntentExtractor
from .price_wow import PriceWowExtractor
from .social_buzz import SocialBuzzExtractor

# Static 8-extractor list kept for backward compatibility (XGBoost trainer uses this)
DIMENSION_EXTRACTORS: list[BaseDimensionExtractor] = [
    HackabilityExtractor(),
    EmotionalIntensityExtractor(),
    ShareabilityExtractor(),
    NoveltyExtractor(),
    CreatorFriendlinessExtractor(),
    ReviewMomentumExtractor(),
    RecommendationIntentExtractor(),
    PriceWowExtractor(),
]


def build_extractors(social_data: dict | None = None) -> list[BaseDimensionExtractor]:
    """
    Factory returning all 9 dimension extractors.
    Pass social_data to inject pre-fetched Google Trends + Reddit signals
    into SocialBuzzExtractor. Falls back to reference mean when None.
    """
    return [
        HackabilityExtractor(),
        EmotionalIntensityExtractor(),
        ShareabilityExtractor(),
        NoveltyExtractor(),
        CreatorFriendlinessExtractor(),
        ReviewMomentumExtractor(),
        RecommendationIntentExtractor(),
        PriceWowExtractor(),
        SocialBuzzExtractor(social_data),
    ]


# Includes all 9 dimensions (used by score_aggregator for SHAP baseline)
DIMENSION_WEIGHTS: dict[str, float] = {
    "hackability": 0.23,
    "emotional_intensity": 0.16,
    "shareability": 0.16,
    "novelty": 0.11,
    "creator_friendliness": 0.11,
    "review_momentum": 0.09,
    "recommendation_intent": 0.04,
    "price_wow": 0.02,
    "social_buzz": 0.08,
}

assert abs(sum(DIMENSION_WEIGHTS.values()) - 1.0) < 1e-6, (
    f"Dimension weights must sum to 1.0, got {sum(DIMENSION_WEIGHTS.values())}"
)

DIMENSION_DISPLAY_NAMES: dict[str, str] = {
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

DIMENSION_DESCRIPTIONS: dict[str, str] = {
    "hackability": "Community-discovered alternative uses and creative misapplication potential",
    "emotional_intensity": "Degree of emotional excitement and obsessive language in reviews",
    "shareability": "Platform mentions, 'show it off' intent, and TikTok/Instagram presence",
    "novelty": "How different the product feels vs. everything the reviewer has tried before",
    "creator_friendliness": "Visual appeal, filming intent, and content creation suitability",
    "review_momentum": "Acceleration of review volume and rating trajectory over time",
    "recommendation_intent": "Word-of-mouth spread, gifting intent, and NPS proxy signals",
    "price_wow": "Value-surprise: emotional reaction when product exceeds price expectations",
    "social_buzz": "Real-time social interest via Google Trends + Reddit community mentions",
}
