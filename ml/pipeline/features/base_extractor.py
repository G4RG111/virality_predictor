"""
Abstract base class for all VIBE dimension extractors.
Every extractor must implement this interface.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Review:
    """Normalized review record consumed by all extractors."""
    text: str
    rating: float | None = None          # 1.0 – 5.0
    review_date: str | None = None        # ISO date string
    source: str = "unknown"              # amazon | ihut | social
    market: str | None = None
    reviewer_type: str | None = None     # consumer | tester | creator
    helpful_votes: int = 0
    verified_purchase: bool = False
    external_id: str | None = None


@dataclass
class IHUTChunk:
    """Segment extracted from an iHUT PDF slide."""
    text: str
    chunk_type: str                       # header | body | verbatim | table_cell
    slide_number: int
    section: str | None = None           # e.g. "Key Findings", "Verbatim Feedback"
    market: str | None = None
    product: str | None = None
    confidence: float = 1.0              # extraction confidence


@dataclass
class SignalEvidence:
    """A single extracted virality signal with its source."""
    signal_type: str
    signal_value: str                    # matched phrase or computed value
    source_text: str                     # original review/chunk text
    source_id: str | None = None
    confidence: float = 1.0


@dataclass
class DimensionFeatures:
    """Output of a single dimension extractor."""
    dimension: str
    weight: float                        # configured weight (0.0 – 1.0)
    raw_score: float                     # pre-normalization, 0.0 – 1.0
    feature_count: int                   # number of signals that fed this score
    top_signals: list[SignalEvidence] = field(default_factory=list)
    feature_vector: dict[str, Any] = field(default_factory=dict)  # named sub-features
    evidence_texts: list[str] = field(default_factory=list)        # verbatim evidence

    @property
    def weighted_raw(self) -> float:
        return self.raw_score * self.weight


class BaseDimensionExtractor(ABC):
    """
    Base class for all VIBE dimension extractors.

    Subclasses implement `extract()` and `dimension_name`/`weight`.
    Extractors must be stateless — safe for parallel execution.
    """

    @property
    @abstractmethod
    def dimension_name(self) -> str:
        """Unique identifier: e.g. 'hackability', 'emotional_intensity'."""
        ...

    @property
    @abstractmethod
    def weight(self) -> float:
        """Configured weight in VIBE score (0.0 – 1.0). All weights must sum to 1.0."""
        ...

    @abstractmethod
    def extract(
        self,
        reviews: list[Review],
        ihut_chunks: list[IHUTChunk] | None = None,
    ) -> DimensionFeatures:
        """
        Compute dimension features from reviews and optional iHUT chunks.

        Args:
            reviews: Normalized review records.
            ihut_chunks: iHUT tester verbatims and slide text (may be None
                         when only Amazon reviews are available).

        Returns:
            DimensionFeatures with raw_score in [0, 1].
        """
        ...

    def _safe_rate(self, count: int, total: int) -> float:
        """Safe division returning 0.0 when total is 0."""
        return count / total if total > 0 else 0.0

    def _clamp(self, value: float, lo: float = 0.0, hi: float = 1.0) -> float:
        return max(lo, min(hi, value))

    def _top_n_signals(
        self, signals: list[SignalEvidence], n: int = 10
    ) -> list[SignalEvidence]:
        return sorted(signals, key=lambda s: s.confidence, reverse=True)[:n]
