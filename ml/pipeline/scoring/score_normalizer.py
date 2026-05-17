"""
Score normalization utilities.
Calibrates raw dimension scores against a reference corpus.
"""
from __future__ import annotations

import json
from pathlib import Path

# Default min/max per dimension derived from reference corpus calibration.
# Values represent (5th percentile of standard products, 95th percentile of viral products).
# These are initial estimates — run `notebooks/02_feature_engineering.ipynb` to recalibrate.
_DEFAULT_CALIBRATION: dict[str, tuple[float, float]] = {
    "hackability": (0.02, 0.55),
    "emotional_intensity": (0.05, 0.65),
    "shareability": (0.01, 0.50),
    "novelty": (0.05, 0.60),
    "creator_friendliness": (0.01, 0.45),
    "review_momentum": (0.10, 0.80),
    "recommendation_intent": (0.05, 0.60),
    "price_wow": (0.05, 0.70),
}

_CALIBRATION_PATH = Path(__file__).parent.parent.parent / "data" / "models" / "calibration.json"


def load_calibration() -> dict[str, tuple[float, float]]:
    if _CALIBRATION_PATH.exists():
        with open(_CALIBRATION_PATH) as f:
            data = json.load(f)
        return {k: tuple(v) for k, v in data.items()}
    return _DEFAULT_CALIBRATION


def normalize_score(raw: float, dimension: str, calibration: dict | None = None) -> float:
    """
    Map a raw dimension score [0,1] to a calibrated [0,1] range
    using the reference corpus min/max.
    """
    cal = calibration or _DEFAULT_CALIBRATION
    lo, hi = cal.get(dimension, (0.0, 1.0))
    if hi <= lo:
        return raw
    normalized = (raw - lo) / (hi - lo)
    return max(0.0, min(1.0, normalized))


def save_calibration(calibration: dict[str, tuple[float, float]]) -> None:
    _CALIBRATION_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_CALIBRATION_PATH, "w") as f:
        json.dump({k: list(v) for k, v in calibration.items()}, f, indent=2)
