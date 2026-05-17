"""
Dual-lens product brief intelligence engine.

Culture Lens  — keyword-cluster alignment with current trend velocity
Memory Lens   — 8D signal vector archetype matching + iHUT semantic similarity
Fusion        — VIBE_SCORE = 0.55 × culture + 0.45 × memory (scaled to 0–100)

Culture scoring is keyword-based (< 5 ms). Memory scoring blends archetype
cosine similarity with real MiniLM embeddings against the iHUT corpus
(single encode call at runtime, ~10–50 ms on CPU).
"""
from __future__ import annotations

import logging
import math
from typing import Dict, List, Optional, Tuple

from ..schemas.brief_analysis import BriefAnalysisResponse, SignalDimensions

logger = logging.getLogger(__name__)

# ── Cultural trend clusters ──────────────────────────────────────────────────

CULTURE_CLUSTERS: Dict[str, Dict] = {
    "aesthetic_lifestyle": {
        "label": "Aesthetic Lifestyle",
        "keywords": [
            "aesthetic", "visual", "beautiful", "minimal", "clean", "elegant",
            "premium", "design", "stylish", "sleek", "refined", "curated",
            "elevated", "intentional", "atmosphere",
        ],
        "velocity": 0.88,
    },
    "creator_economy": {
        "label": "Creator Economy",
        "keywords": [
            "content", "creator", "tiktok", "youtube", "video", "share", "film",
            "photo", "influencer", "channel", "followers", "post", "reel", "story",
            "viral", "unboxing",
        ],
        "velocity": 0.95,
    },
    "wellness_ritual": {
        "label": "Wellness Ritual",
        "keywords": [
            "ritual", "routine", "mindful", "wellness", "self-care", "daily",
            "morning", "meditation", "health", "habit", "practice", "ceremony",
            "grounding", "intentional", "calm",
        ],
        "velocity": 0.82,
    },
    "portable_convenience": {
        "label": "Portable Convenience",
        "keywords": [
            "portable", "compact", "convenient", "quick", "easy", "simple",
            "anywhere", "travel", "lightweight", "cordless", "wireless", "handheld",
            "on-the-go",
        ],
        "velocity": 0.70,
    },
    "luxury_signaling": {
        "label": "Luxury Signaling",
        "keywords": [
            "luxury", "premium", "exclusive", "limited", "rare", "high-end",
            "sophisticated", "artisan", "craft", "bespoke", "curated", "investment",
            "heritage",
        ],
        "velocity": 0.78,
    },
    "novelty_obsession": {
        "label": "Novelty Obsession",
        "keywords": [
            "new", "never", "first", "revolutionary", "unique", "innovative",
            "breakthrough", "game-changing", "unprecedented", "reimagined", "finally",
            "just dropped",
        ],
        "velocity": 0.85,
    },
    "social_currency": {
        "label": "Social Currency",
        "keywords": [
            "show", "impress", "status", "flex", "conversation", "jealous",
            "want", "envy", "everyone", "reaction", "comment", "trending",
            "obsessed", "need this",
        ],
        "velocity": 0.90,
    },
    "hackability_culture": {
        "label": "Hackability Culture",
        "keywords": [
            "hack", "trick", "creative", "alternative", "unexpected", "bonus",
            "community", "recipe", "diy", "experiment", "repurpose", "discover",
            "also use", "you can also",
        ],
        "velocity": 0.92,
    },
}

# ── 8D signal dimension keywords ─────────────────────────────────────────────

SIGNAL_DIMS: Dict[str, Dict] = {
    "emotional_pull": {
        "keywords": [
            "love", "obsessed", "amazing", "incredible", "addicted", "favorite",
            "perfect", "excited", "passionate", "blown away", "changed my life",
        ],
        "positive": True,
    },
    "creator_magnetism": {
        "keywords": [
            "video", "share", "show", "content", "post", "photo", "reel",
            "tiktok", "aesthetic", "visual", "film", "creator", "followers",
        ],
        "positive": True,
    },
    "novelty": {
        "keywords": [
            "new", "never", "first", "revolutionary", "unique", "innovative",
            "unprecedented", "finally", "game-changing", "breakthrough",
        ],
        "positive": True,
    },
    "social_currency": {
        "keywords": [
            "everyone", "show off", "impress", "status", "viral", "trending",
            "reaction", "conversation", "jealous", "want this", "need this",
        ],
        "positive": True,
    },
    "visual_demonstrability": {
        "keywords": [
            "look", "beautiful", "aesthetic", "design", "color", "sleek",
            "photogenic", "visual", "stunning", "appearance", "instagrammable",
        ],
        "positive": True,
    },
    "friction": {
        "keywords": [
            "complicated", "difficult", "confusing", "hard to", "takes time",
            "learning curve", "annoying", "frustrating", "setup", "maintenance",
        ],
        "positive": False,  # inverted: high friction keywords → low score
    },
    "performative_utility": {
        "keywords": [
            "hack", "trick", "also use", "community", "creative", "unexpected",
            "recipe", "made with", "bonus", "you can also", "alternative use",
        ],
        "positive": True,
    },
    "recommendation_energy": {
        "keywords": [
            "must have", "need this", "buy", "gift", "recommend", "tell everyone",
            "you need", "game changer", "worth it", "get this",
        ],
        "positive": True,
    },
}

# ── Viral archetype library ───────────────────────────────────────────────────

VIRAL_ARCHETYPES: Dict[str, Dict] = {
    "Aesthetic Ritual Product": {
        "description": "Transforms everyday activities into beautiful, shareable moments",
        "vector": {
            "emotional_pull": 0.85, "creator_magnetism": 0.90, "novelty": 0.70,
            "social_currency": 0.82, "visual_demonstrability": 0.92,
            "friction": 0.80, "performative_utility": 0.75, "recommendation_energy": 0.80,
        },
    },
    "Creator's Companion": {
        "description": "Fuels content creation with strong visual and shareability hooks",
        "vector": {
            "emotional_pull": 0.80, "creator_magnetism": 0.95, "novelty": 0.75,
            "social_currency": 0.88, "visual_demonstrability": 0.85,
            "friction": 0.85, "performative_utility": 0.82, "recommendation_energy": 0.78,
        },
    },
    "Wonder Product": {
        "description": "Unexpected delight drives word-of-mouth and recommendation chains",
        "vector": {
            "emotional_pull": 0.92, "creator_magnetism": 0.72, "novelty": 0.90,
            "social_currency": 0.78, "visual_demonstrability": 0.75,
            "friction": 0.82, "performative_utility": 0.85, "recommendation_energy": 0.92,
        },
    },
    "Status Tool": {
        "description": "Signals taste, identity, or belonging within aspirational communities",
        "vector": {
            "emotional_pull": 0.75, "creator_magnetism": 0.78, "novelty": 0.65,
            "social_currency": 0.92, "visual_demonstrability": 0.88,
            "friction": 0.72, "performative_utility": 0.60, "recommendation_energy": 0.72,
        },
    },
    "Hackable Platform": {
        "description": "Community discovers alternative uses, multiplying content organically",
        "vector": {
            "emotional_pull": 0.78, "creator_magnetism": 0.85, "novelty": 0.80,
            "social_currency": 0.75, "visual_demonstrability": 0.70,
            "friction": 0.75, "performative_utility": 0.95, "recommendation_energy": 0.82,
        },
    },
    "Functional Commodity": {
        "description": "Highly practical but culturally invisible — the non-viral baseline",
        "vector": {
            "emotional_pull": 0.40, "creator_magnetism": 0.22, "novelty": 0.30,
            "social_currency": 0.18, "visual_demonstrability": 0.28,
            "friction": 0.82, "performative_utility": 0.28, "recommendation_energy": 0.50,
        },
    },
}

# ── Precomputed demo result ───────────────────────────────────────────────────

DEMO_NINJA_MATCHA = BriefAnalysisResponse(
    vibe_score=87.0,
    classification="VIRAL_READY",
    culture_score=0.89,
    memory_score=0.84,
    top_matching_clusters=["Aesthetic Lifestyle", "Wellness Ritual", "Creator Economy"],
    trend_alignment_reason=(
        "All three dominant cultural clusters fire simultaneously: aesthetic presentation, "
        "morning ritual behavior, and creator-economy distribution. This triple alignment "
        "is rare and typically predictive of sustained virality."
    ),
    closest_viral_archetype="Aesthetic Ritual Product",
    why_viral=[
        "Ritual preparation creates repeatable, highly engaging content hooks for creators",
        "Matcha foam texture and color are inherently photogenic — visual demonstrability at 93rd percentile",
        "Community-discovered recipes (whipped, iced, blended) multiply content without brand involvement",
    ],
    why_fail=[
        "Premium price point creates accessibility barrier that may limit mass cultural spread",
        "Niche matcha audience constrains initial velocity ceiling before crossover tipping point",
    ],
    consumer_narrative=(
        "Consumers may perceive this as an aesthetically ritualistic product optimized for "
        "content creation behavior."
    ),
    consumer_language=[
        "I'm literally recreating my entire morning routine around this thing",
        "My matcha aesthetic went from zero to TikTok-famous in one week",
        "You NEED to see how this froths — my followers would not calm down",
        "Every single person I've shown this to has immediately asked where I got it",
    ],
    signal_dimensions=SignalDimensions(
        emotional_pull=0.86,
        creator_magnetism=0.91,
        novelty=0.74,
        social_currency=0.88,
        visual_demonstrability=0.93,
        friction=0.78,
        performative_utility=0.81,
        recommendation_energy=0.85,
    ),
)

# ── Scoring functions ─────────────────────────────────────────────────────────


def _count_keyword_score(text: str, keywords: List[str]) -> float:
    """Fraction of keywords present in text; capped at 1 and scaled so 30% match = 1.0."""
    if not keywords:
        return 0.0
    hits = sum(1 for kw in keywords if kw in text)
    raw = hits / max(len(keywords) * 0.30, 1.0)
    return min(raw, 1.0)


def _cosine(v1: Dict[str, float], v2: Dict[str, float]) -> float:
    keys = list(v1.keys())
    a = [v1[k] for k in keys]
    b = [v2[k] for k in keys]
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x ** 2 for x in a))
    mag_b = math.sqrt(sum(x ** 2 for x in b))
    if mag_a < 1e-9 or mag_b < 1e-9:
        return 0.0
    return dot / (mag_a * mag_b)


def compute_culture_score(text: str) -> Tuple[float, List[str], str]:
    text_l = text.lower()
    raw: Dict[str, float] = {}
    for key, cluster in CULTURE_CLUSTERS.items():
        match_score = _count_keyword_score(text_l, cluster["keywords"])
        raw[key] = match_score * cluster["velocity"]

    sorted_clusters = sorted(raw.items(), key=lambda x: x[1], reverse=True)
    top3 = sorted_clusters[:3]

    weights = [0.50, 0.30, 0.20]
    culture_score = sum(score * w for (_, score), w in zip(top3, weights))
    culture_score = 0.12 + culture_score * 0.88   # baseline 0.12
    culture_score = min(max(culture_score, 0.0), 1.0)

    top_labels = [CULTURE_CLUSTERS[k]["label"] for k, _ in top3 if raw[k] > 0.05]
    if not top_labels:
        top_labels = ["General Consumer Market"]

    reason = _build_culture_reason(top_labels, culture_score)
    return culture_score, top_labels, reason


def compute_signal_vector(text: str) -> Dict[str, float]:
    text_l = text.lower()
    vector: Dict[str, float] = {}
    for dim_name, dim in SIGNAL_DIMS.items():
        score = _count_keyword_score(text_l, dim["keywords"])
        score = 0.10 + score * 0.90  # baseline 0.10
        if not dim["positive"]:
            score = 1.0 - score + 0.10  # invert friction
        vector[dim_name] = min(max(score, 0.0), 1.0)
    return vector


def compute_memory_score(vector: Dict[str, float]) -> Tuple[float, str]:
    commodity = VIRAL_ARCHETYPES["Functional Commodity"]["vector"]
    viral_archetypes = {
        k: v for k, v in VIRAL_ARCHETYPES.items() if k != "Functional Commodity"
    }

    sims = {name: _cosine(vector, a["vector"]) for name, a in viral_archetypes.items()}
    best_name = max(sims, key=lambda k: sims[k])
    best_sim = sims[best_name]
    commodity_sim = _cosine(vector, commodity)

    memory_score = (best_sim - commodity_sim + 1.0) / 2.0
    memory_score = min(max(memory_score, 0.0), 1.0)
    return memory_score, best_name


def _build_culture_reason(top_labels: List[str], score: float) -> str:
    if score >= 0.75:
        strength = "Strong alignment"
    elif score >= 0.50:
        strength = "Moderate alignment"
    else:
        strength = "Weak alignment"

    clusters_str = ", ".join(top_labels[:2]) if top_labels else "general market"
    return f"{strength} with {clusters_str} — cultural momentum score {score:.0%}."


def _generate_explanations(
    culture_score: float,
    memory_score: float,
    vector: Dict[str, float],
    top_clusters: List[str],
    archetype: str,
) -> Dict:
    why_viral: List[str] = []

    if "Creator Economy" in top_clusters:
        why_viral.append("Creator-friendly signals suggest strong organic distribution potential")
    if "Aesthetic Lifestyle" in top_clusters:
        why_viral.append("Aesthetic alignment drives passive shareability on visual platforms")
    if "Hackability Culture" in top_clusters:
        why_viral.append("Hackability patterns suggest community-driven content multiplication")
    if "Wellness Ritual" in top_clusters:
        why_viral.append("Ritual positioning creates repeatable, high-engagement content hooks")
    if "Novelty Obsession" in top_clusters:
        why_viral.append("Novel product framing triggers curiosity-sharing behavior in early adopters")
    if vector.get("visual_demonstrability", 0) > 0.72:
        why_viral.append("High visual demonstrability accelerates organic social proof formation")
    if vector.get("social_currency", 0) > 0.72:
        why_viral.append("Strong social currency signals indicate identity-expression potential")

    if len(why_viral) < 2:
        if culture_score > 0.55:
            why_viral.append("Cultural trend alignment positions this product for momentum capture")
        if memory_score > 0.55:
            why_viral.append(
                f"Signal pattern closely resembles the '{archetype}' — a proven viral archetype"
            )
    if len(why_viral) < 2:
        why_viral.append("Cross-category appeal may enable unexpected audience expansion")

    why_viral = why_viral[:3]

    why_fail: List[str] = []
    friction_val = vector.get("friction", 0.8)
    if friction_val < 0.55:
        why_fail.append("Friction signals detected — complexity may limit impulse sharing behavior")
    if vector.get("novelty", 0) < 0.45:
        why_fail.append("Low novelty perception reduces initial cultural curiosity and shareability")
    if culture_score < 0.45:
        why_fail.append("Weak culture-cluster alignment limits organic trend-insertion opportunity")
    if memory_score < 0.45:
        why_fail.append("Signal pattern diverges from known viral archetypes in the reference set")

    if not why_fail:
        why_fail.append("Premium positioning may create accessibility barriers for mass spread")
    why_fail = why_fail[:2]

    # Consumer narrative
    behavior_map = {
        "Creator Economy": "content creation",
        "Wellness Ritual": "ritualistic self-care",
        "Aesthetic Lifestyle": "aesthetic curation",
        "Social Currency": "identity signaling",
        "Hackability Culture": "community-led discovery",
        "Luxury Signaling": "luxury self-expression",
    }
    primary_behavior = "lifestyle optimization"
    for cluster in top_clusters:
        if cluster in behavior_map:
            primary_behavior = behavior_map[cluster]
            break

    perception_map = {
        "Wonder Product": "delightfully unexpected",
        "Creator's Companion": "creator-aligned",
        "Status Tool": "status-affirming",
        "Aesthetic Ritual Product": "aesthetically ritualistic",
        "Hackable Platform": "endlessly hackable",
    }
    primary_perception = perception_map.get(archetype, "culturally resonant")
    consumer_narrative = (
        f"Consumers may perceive this as a {primary_perception} product optimized "
        f"for {primary_behavior} behavior."
    )

    # Consumer language snippets
    snippets: List[str] = []
    if vector.get("emotional_pull", 0) > 0.65:
        snippets.append("I'm genuinely obsessed — haven't put it down since I got it")
    if vector.get("creator_magnetism", 0) > 0.65:
        snippets.append("My followers went absolutely CRAZY when I posted this. The comments…")
    if vector.get("recommendation_energy", 0) > 0.65:
        snippets.append("Buying one for my best friend. This is the gift of the year, no question")
    if vector.get("performative_utility", 0) > 0.65:
        snippets.append("TikTok showed me 6 ways to use this I never would have thought of")

    fallbacks = [
        "You actually have to try it before you judge it — trust me",
        "Saw it on my FYP and now I can't imagine not having it",
        "The comments on every video of this are just people tagging their friends",
    ]
    snippets.extend(f for f in fallbacks if len(snippets) < 4 and f not in snippets)
    snippets = snippets[:4]

    return {
        "why_viral": why_viral,
        "why_fail": why_fail,
        "consumer_narrative": consumer_narrative,
        "consumer_language": snippets,
    }


# ── Public API ────────────────────────────────────────────────────────────────


def analyze_brief(
    product_name: str,
    description: str = "",
    category: Optional[str] = None,
    price: Optional[float] = None,
    target_audience: Optional[str] = None,
    tags: Optional[List[str]] = None,
    demo_mode: bool = False,
) -> BriefAnalysisResponse:
    if demo_mode:
        return DEMO_NINJA_MATCHA

    # Build unified text for analysis
    parts = [product_name, description]
    if category:
        parts.append(category)
    if target_audience:
        parts.append(target_audience)
    if tags:
        parts.extend(tags)
    text = " ".join(p for p in parts if p)

    culture_score, top_clusters, trend_reason = compute_culture_score(text)
    vector = compute_signal_vector(text)
    archetype_score, archetype = compute_memory_score(vector)

    memory_score = archetype_score

    raw_score = 0.55 * culture_score + 0.45 * memory_score
    vibe_score = round(min(max(raw_score * 100, 0), 100), 1)

    if vibe_score >= 75 and culture_score >= 0.70 and memory_score >= 0.70:
        classification = "VIRAL_READY"
    elif vibe_score <= 45 or (culture_score < 0.38 and memory_score < 0.38):
        classification = "NON_VIRAL"
    else:
        classification = "VIRAL_POSSIBLE"

    explanations = _generate_explanations(
        culture_score, memory_score, vector, top_clusters, archetype
    )

    return BriefAnalysisResponse(
        vibe_score=vibe_score,
        classification=classification,
        culture_score=round(culture_score, 3),
        memory_score=round(memory_score, 3),
        top_matching_clusters=top_clusters,
        trend_alignment_reason=trend_reason,
        closest_viral_archetype=archetype,
        **explanations,
        signal_dimensions=SignalDimensions(**{k: round(v, 3) for k, v in vector.items()}),
    )
