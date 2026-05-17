"""
SHAP Explainability Pipeline.
Phase 1: Analytic SHAP for weighted formula (exact decomposition).
Phase 2: TreeSHAP for XGBoost model.

Invariant: baseline_score + sum(shap_values) == vibe_score (within float precision).
"""
from __future__ import annotations

from dataclasses import dataclass, field

from ..scoring.score_aggregator import VibeScoreResult


@dataclass
class ShapContribution:
    dimension: str
    display_name: str
    shap_value: float           # contribution to VIBE score (positive = helpful, negative = drag)
    feature_value: float        # raw dimension score (0–1)
    feature_value_display: str  # human-readable: "14% of reviews"
    direction: str              # "positive" | "negative" | "neutral"
    rank: int = 0               # 1 = highest |shap_value|


@dataclass
class ShapExplanation:
    product_id: str
    vibe_score: float
    baseline_score: float
    contributions: list[ShapContribution]
    narrative: str
    top_positive_drivers: list[str]
    top_negative_drivers: list[str]
    model_version: str = "weighted-formula-v1"


from ..features.feature_registry import DIMENSION_DISPLAY_NAMES


def explain(result: VibeScoreResult, product_id: str) -> ShapExplanation:
    """
    Build a full SHAP explanation from a VibeScoreResult.
    Uses analytic SHAP (Phase 1 weighted formula).
    """
    contributions: list[ShapContribution] = []

    for dim, shap_val in result.shap_values.items():
        raw = result.dimension_raw.get(dim, 0.0)
        display = DIMENSION_DISPLAY_NAMES.get(dim, dim.replace("_", " ").title())
        feature_display = _format_feature_value(dim, raw, result.feature_vectors.get(dim, {}))

        direction = "positive" if shap_val > 0.5 else ("negative" if shap_val < -0.5 else "neutral")

        contributions.append(ShapContribution(
            dimension=dim,
            display_name=display,
            shap_value=round(shap_val, 2),
            feature_value=raw,
            feature_value_display=feature_display,
            direction=direction,
        ))

    # Sort by |shap_value| descending and assign ranks
    contributions.sort(key=lambda c: abs(c.shap_value), reverse=True)
    for i, c in enumerate(contributions):
        c.rank = i + 1

    positives = [c for c in contributions if c.shap_value > 0]
    negatives = [c for c in contributions if c.shap_value < 0]

    narrative = _build_narrative(result.vibe_score, positives, negatives, result.score_band)

    return ShapExplanation(
        product_id=product_id,
        vibe_score=result.vibe_score,
        baseline_score=result.baseline_score,
        contributions=contributions,
        narrative=narrative,
        top_positive_drivers=[c.display_name for c in positives[:3]],
        top_negative_drivers=[c.display_name for c in negatives[:3]],
    )


def _format_feature_value(dim: str, raw: float, feature_vector: dict) -> str:
    """Convert a raw dimension score into a human-readable metric string."""
    pct = round(raw * 100, 1)

    if dim == "hackability":
        rate = feature_vector.get("hack_phrase_rate", raw)
        return f"{round(rate * 100, 1)}% of reviews mention alternative uses"

    elif dim == "emotional_intensity":
        rate = feature_vector.get("obsession_phrase_rate", raw)
        return f"{round(rate * 100, 1)}% of reviews contain obsession language"

    elif dim == "shareability":
        rate = feature_vector.get("platform_mention_rate", raw)
        return f"{round(rate * 100, 1)}% of reviews mention social platforms"

    elif dim == "novelty":
        rate = feature_vector.get("novelty_phrase_rate", raw)
        return f"{round(rate * 100, 1)}% of reviews express novelty/surprise"

    elif dim == "creator_friendliness":
        rate = feature_vector.get("creator_mention_rate", raw)
        return f"{round(rate * 100, 1)}% of reviews mention content creation"

    elif dim == "review_momentum":
        vr = feature_vector.get("velocity_ratio", 1.0)
        return f"{round(vr, 1)}x review velocity (recent vs prior period)"

    elif dim == "recommendation_intent":
        rate = feature_vector.get("wom_rate", raw)
        return f"{round(rate * 100, 1)}% of reviews contain word-of-mouth language"

    elif dim == "price_wow":
        rate = feature_vector.get("price_wow_rate", raw)
        return f"{round(rate * 100, 1)}% of reviews express value surprise"

    return f"Score: {pct}/100"


def _build_narrative(
    vibe_score: float,
    positives: list[ShapContribution],
    negatives: list[ShapContribution],
    band: str,
) -> str:
    """Generate a 2-3 sentence plain-English narrative."""
    band_phrases = {
        "viral": "This product has exceptional viral potential",
        "high": "This product shows strong viral potential",
        "moderate": "This product has moderate viral potential",
        "low": "This product has limited viral potential at this time",
    }
    opening = band_phrases.get(band, f"VIBE Score: {vibe_score}/100")

    driver_str = ""
    if positives:
        top = positives[0]
        driver_str = f" The strongest driver is **{top.display_name}** ({top.feature_value_display})."
        if len(positives) > 1:
            second = positives[1]
            driver_str += f" **{second.display_name}** also contributes positively."

    drag_str = ""
    if negatives:
        drag = negatives[0]
        drag_str = f" The main limiting factor is **{drag.display_name}** ({drag.feature_value_display})."

    return f"{opening} (VIBE Score: {vibe_score}/100).{driver_str}{drag_str}"
