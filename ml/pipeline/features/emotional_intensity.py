"""
Dimension 2: Emotional Intensity (weight: 17%)
Measures the degree of emotional expression that drives share-worthy reactions.

Sub-signals:
  obsession_phrase_rate, exclamation_density, caps_ratio,
  emotion_classifier_score (joy/surprise/anticipation), superlative_count_rate
"""
from __future__ import annotations

from .base_extractor import (
    BaseDimensionExtractor,
    DimensionFeatures,
    IHUTChunk,
    Review,
    SignalEvidence,
)
from ..utils.lexicons import (
    OBSESSION_PHRASES,
    EXCITEMENT_INTENSIFIERS,
    contains_any,
    get_matched_phrases,
)
from ..utils.text_preprocessor import (
    exclamation_density,
    caps_ratio,
    superlative_count,
    word_count,
)

# Target emotion labels that correlate with virality (from distilroberta emotion model)
_VIRAL_EMOTIONS = {"joy", "surprise", "anticipation", "excitement"}
_EMOTION_MODEL = "j-hartmann/emotion-english-distilroberta-base"
_SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"


class EmotionalIntensityExtractor(BaseDimensionExtractor):

    @property
    def dimension_name(self) -> str:
        return "emotional_intensity"

    @property
    def weight(self) -> float:
        return 0.16

    def extract(
        self,
        reviews: list[Review],
        ihut_chunks: list[IHUTChunk] | None = None,
    ) -> DimensionFeatures:
        signals: list[SignalEvidence] = []
        feature_vector: dict[str, float] = {}
        total = len(reviews)

        if total == 0:
            return DimensionFeatures(
                dimension=self.dimension_name,
                weight=self.weight,
                raw_score=0.0,
                feature_count=0,
            )

        # ── Sub-signal 1: Obsession phrases ─────────────────────────────────
        obsession_count = 0
        intensifier_count = 0
        for review in reviews:
            matched = get_matched_phrases(review.text, OBSESSION_PHRASES)
            if matched:
                obsession_count += 1
                signals.append(SignalEvidence(
                    signal_type="obsession_phrase",
                    signal_value=matched[0],
                    source_text=review.text[:200],
                    confidence=0.9,
                ))
            if contains_any(review.text, EXCITEMENT_INTENSIFIERS):
                intensifier_count += 1

        obsession_rate = self._safe_rate(obsession_count, total)
        intensifier_rate = self._safe_rate(intensifier_count, total)
        feature_vector["obsession_phrase_rate"] = obsession_rate
        feature_vector["intensifier_rate"] = intensifier_rate

        # ── Sub-signal 2: Typography signals (!, CAPS) ────────────────────────
        all_texts = " ".join(r.text for r in reviews)
        excl_density = exclamation_density(all_texts)
        caps = caps_ratio(all_texts)
        feature_vector["exclamation_density"] = excl_density
        feature_vector["caps_ratio"] = caps

        # ── Sub-signal 3: Superlative density ────────────────────────────────
        total_words = sum(word_count(r.text) for r in reviews)
        total_superlatives = sum(superlative_count(r.text) for r in reviews)
        superlative_rate = self._safe_rate(total_superlatives, max(total_words, 1))
        feature_vector["superlative_rate"] = superlative_rate

        # ── Sub-signal 4: Emotion classifier (optional, requires transformers) ─
        emotion_score = 0.0
        try:
            emotion_score = _run_emotion_classifier(reviews)
        except Exception:
            pass  # Gracefully degrade if model not available
        feature_vector["emotion_classifier_score"] = emotion_score

        # ── iHUT contribution ────────────────────────────────────────────────
        ihut_emotion = 0.0
        if ihut_chunks:
            ihut_verbatims = [c.text for c in ihut_chunks if c.chunk_type == "verbatim"]
            ihut_obsession = sum(
                1 for t in ihut_verbatims if contains_any(t, OBSESSION_PHRASES)
            )
            ihut_emotion = self._safe_rate(ihut_obsession, max(len(ihut_verbatims), 1))
        feature_vector["ihut_emotional_score"] = ihut_emotion

        # ── Composite ────────────────────────────────────────────────────────
        raw_score = self._clamp(
            obsession_rate * 0.40
            + min(excl_density * 15, 0.15)          # cap exclamation contribution
            + min(caps * 0.5, 0.10)
            + superlative_rate * 20 * 0.10
            + emotion_score * 0.20
            + ihut_emotion * 0.05,
        )

        return DimensionFeatures(
            dimension=self.dimension_name,
            weight=self.weight,
            raw_score=raw_score,
            feature_count=len(signals),
            top_signals=self._top_n_signals(signals),
            feature_vector=feature_vector,
            evidence_texts=[s.source_text for s in signals[:8]],
        )


def _run_emotion_classifier(reviews: list[Review]) -> float:
    """
    Run HuggingFace emotion classifier on a sample of reviews.
    Returns fraction of reviews classified as viral-emotion (joy/surprise).
    Falls back to 0.0 if transformers not available.
    """
    from transformers import pipeline

    sample = [r.text[:512] for r in reviews[:50]]  # limit for speed
    classifier = pipeline("text-classification", model=_EMOTION_MODEL, top_k=1)
    results = classifier(sample)
    viral_count = sum(
        1 for r in results
        if r and r[0]["label"].lower() in _VIRAL_EMOTIONS
    )
    return viral_count / len(sample) if sample else 0.0
