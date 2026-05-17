"""
Formats SHAP explanations into structures consumed by the FastAPI response layer.
"""
from __future__ import annotations

from .shap_explainer import ShapExplanation, ShapContribution


def to_api_dict(explanation: ShapExplanation) -> dict:
    """Serialize a ShapExplanation to a JSON-serializable dict for API responses."""
    return {
        "product_id": explanation.product_id,
        "vibe_score": explanation.vibe_score,
        "baseline_score": explanation.baseline_score,
        "narrative": explanation.narrative,
        "top_positive_drivers": explanation.top_positive_drivers,
        "top_negative_drivers": explanation.top_negative_drivers,
        "model_version": explanation.model_version,
        "contributions": [_contribution_to_dict(c) for c in explanation.contributions],
    }


def _contribution_to_dict(c: ShapContribution) -> dict:
    return {
        "dimension": c.dimension,
        "display_name": c.display_name,
        "shap_value": c.shap_value,
        "feature_value": c.feature_value,
        "feature_value_display": c.feature_value_display,
        "direction": c.direction,
        "rank": c.rank,
    }


def to_waterfall_data(explanation: ShapExplanation) -> list[dict]:
    """
    Format contributions for a SHAP waterfall chart.
    Each entry represents one bar: start, end, value, label.
    """
    running = explanation.baseline_score
    waterfall = [
        {
            "label": "Baseline",
            "value": 0,
            "cumulative": running,
            "type": "baseline",
        }
    ]

    sorted_contribs = sorted(explanation.contributions, key=lambda c: abs(c.shap_value), reverse=True)

    for c in sorted_contribs:
        start = running
        running = round(running + c.shap_value, 2)
        waterfall.append({
            "label": c.display_name,
            "value": round(c.shap_value, 2),
            "start": start,
            "end": running,
            "cumulative": running,
            "type": c.direction,
            "feature_display": c.feature_value_display,
        })

    waterfall.append({
        "label": "VIBE Score",
        "value": 0,
        "cumulative": explanation.vibe_score,
        "type": "total",
    })

    return waterfall


def format_key_drivers(explanation: ShapExplanation, n: int = 5) -> dict:
    """Return top N positive and negative drivers in plain language."""
    positives = [c for c in explanation.contributions if c.shap_value > 0][:n]
    negatives = [c for c in explanation.contributions if c.shap_value < 0][:n]

    return {
        "positive_drivers": [
            {
                "rank": i + 1,
                "dimension": c.display_name,
                "impact": f"+{c.shap_value:.1f} pts",
                "reason": c.feature_value_display,
                "strength": "strong" if c.shap_value > 5 else "moderate" if c.shap_value > 2 else "slight",
            }
            for i, c in enumerate(positives)
        ],
        "negative_drivers": [
            {
                "rank": i + 1,
                "dimension": c.display_name,
                "impact": f"{c.shap_value:.1f} pts",
                "reason": c.feature_value_display,
                "strength": "strong" if c.shap_value < -5 else "moderate" if c.shap_value < -2 else "slight",
            }
            for i, c in enumerate(negatives)
        ],
        "narrative": explanation.narrative,
    }
