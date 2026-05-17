"""Phase 2 smoke test — run all 9 extractors, check SHAP invariant."""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.features.base_extractor import Review, IHUTChunk
from pipeline.features.hackability import HackabilityExtractor
from pipeline.features.feature_registry import DIMENSION_WEIGHTS, build_extractors
from pipeline.scoring.score_aggregator import compute_vibe_score

# Test 1: Single extractor
e = HackabilityExtractor()
viral_reviews = [
    Review(text="I use this for smoothies AND slushies! Never knew it could do that - total hack!", rating=5.0, source="amazon"),
    Review(text="You can also use it to make sorbet. Brilliant alternative use!", rating=5.0, source="amazon"),
    Review(text="TikTok showed me this trick with the blender - mind blown", rating=4.0, source="social"),
]
result = e.extract(viral_reviews)
print(f"Hackability raw_score: {result.raw_score:.3f} (weight={result.weight})")
print(f"Top signals: {[(s.signal_type, s.signal_value[:40]) for s in result.top_signals[:3]]}")

# Test 2: Weights sum
total = sum(DIMENSION_WEIGHTS.values())
status = "PASS" if abs(total - 1.0) < 1e-6 else "FAIL"
print(f"\nWeight sum: {total:.6f} -> {status}")

# Test 3: All 9 extractors instantiate without error
extractors = build_extractors(social_data=None)
print(f"\nAll {len(extractors)} extractors instantiated: {[ex.dimension_name for ex in extractors]}")

# Test 4: Full VIBE score - viral vs non-viral
bland_reviews = [
    Review(text="Works well. Does the job. Good value.", rating=4.0, source="amazon"),
    Review(text="Functional product. Easy to use.", rating=4.0, source="amazon"),
    Review(text="Does what it says. No complaints.", rating=3.0, source="amazon"),
]

viral_result = compute_vibe_score(viral_reviews)
bland_result = compute_vibe_score(bland_reviews)

print(f"\nViral product VIBE score: {viral_result.vibe_score} [{viral_result.score_band}]")
print(f"Bland product VIBE score:  {bland_result.vibe_score} [{bland_result.score_band}]")
diff_ok = viral_result.vibe_score > bland_result.vibe_score
print(f"  Viral > Bland: {'PASS' if diff_ok else 'FAIL'}")

# Test 5: SHAP invariant
print()
for label, res in [("viral", viral_result), ("bland", bland_result)]:
    shap_sum = sum(res.shap_values.values())
    reconstructed = res.baseline_score + shap_sum
    delta = abs(reconstructed - res.vibe_score)
    status = "PASS" if delta < 0.1 else "FAIL"
    print(
        f"SHAP invariant [{label}]: {res.baseline_score:.1f} + {shap_sum:.2f} = "
        f"{reconstructed:.1f} vs vibe={res.vibe_score} -> {status} (delta={delta:.4f})"
    )

print("\nPhase 2 smoke test complete.")
