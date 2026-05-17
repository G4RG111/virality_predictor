"""
Test iHUT PDF extraction + VIBE scoring on the real Chanel PDFs.
Run from: vibe-predictor/ml/
"""
import sys
import os
import io
from pathlib import Path

# Force UTF-8 output so Windows console doesn't choke on non-ASCII characters
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pipeline.ingestion.ihut_extractor import extract_ihut_pdf, IHUTDocument
from pipeline.features.base_extractor import Review, IHUTChunk
from pipeline.scoring.score_aggregator import compute_vibe_score

PDF_PATHS = [
    r"d:\ML Projects\ViralityPredictor\Chanel MP DE IHUT_ MasterDeck_3Nov (004).pptx_compressed_compressed.pdf",
    r"d:\ML Projects\ViralityPredictor\Chanel Slim UI IHUT MasterDeck_compressed_compressed.pdf",
    r"d:\ML Projects\ViralityPredictor\Chanel UK Slim UI IHUT_Master deck_compressed_compressed.pdf",
]


def ihut_chunks_to_reviews(doc: IHUTDocument) -> list[Review]:
    """Convert iHUT verbatim chunks to Review objects for scoring."""
    reviews = []
    for chunk in doc.verbatim_chunks:
        if len(chunk.text.strip()) < 15:
            continue
        reviews.append(Review(
            text=chunk.text,
            rating=None,
            source="ihut",
            market=chunk.market,
            reviewer_type="tester",
        ))
    return reviews


def main():
    results = {}

    for pdf_path in PDF_PATHS:
        path = Path(pdf_path)
        if not path.exists():
            print(f"  [SKIP] Not found: {path.name}")
            continue

        print(f"\n{'='*60}")
        print(f"Processing: {path.name}")
        print("=" * 60)

        doc = extract_ihut_pdf(pdf_path)

        total = len(doc.chunks)
        verbatims = len(doc.verbatim_chunks)
        hack_signals = len(doc.hackability_chunks)
        headers = len([c for c in doc.chunks if c.chunk_type == "header"])

        print(f"  Product: {doc.product}")
        print(f"  Market:  {doc.market}")
        print(f"  Pages:   {doc.metadata.get('total_pages', '?')}")
        print(f"  Total chunks:    {total}")
        print(f"  Verbatim chunks: {verbatims}")
        print(f"  Hackability signals in iHUT: {hack_signals}")
        print(f"  Header chunks:   {headers}")

        if verbatims > 0:
            print(f"\n  Sample verbatims (first 3):")
            for i, chunk in enumerate(doc.verbatim_chunks[:3]):
                print(f"    [{i+1}] [{chunk.section}] {chunk.text[:120]!r}")

        if hack_signals > 0:
            print(f"\n  Hackability signals (first 3):")
            for chunk in doc.hackability_chunks[:3]:
                print(f"    - {chunk.text[:120]!r}")

        # Compute VIBE score from iHUT verbatims only
        reviews = ihut_chunks_to_reviews(doc)
        print(f"\n  Reviews for scoring: {len(reviews)}")

        if reviews:
            score_result = compute_vibe_score(reviews, ihut_chunks=doc.verbatim_chunks)
            print(f"\n  VIBE Score: {score_result.vibe_score} [{score_result.score_band}]")
            print(f"  Confidence: {score_result.confidence} ({score_result.confidence_value:.2f})")
            print(f"  Dimension breakdown:")
            for dim, score in sorted(score_result.dimension_scores.items(), key=lambda x: -x[1]):
                weight = score_result.dimension_weights[dim]
                contrib = score_result.weighted_contributions[dim]
                print(f"    {dim:25s}: {score:5.1f}  (weight={weight:.2f}, contrib={contrib:.2f})")
            print(f"\n  SHAP baseline: {score_result.baseline_score}")
            print(f"  SHAP values:   {score_result.shap_values}")
            shap_recon = score_result.baseline_score + sum(score_result.shap_values.values())
            print(f"  SHAP invariant: {shap_recon:.1f} == {score_result.vibe_score} -> {'PASS' if abs(shap_recon - score_result.vibe_score) < 0.1 else 'FAIL'}")

            results[doc.market] = {
                "product": doc.product,
                "vibe_score": score_result.vibe_score,
                "score_band": score_result.score_band,
                "verbatim_count": verbatims,
                "hackability_signals": hack_signals,
            }

    if results:
        print(f"\n\n{'='*60}")
        print("SUMMARY: VIBE Scores from iHUT Data")
        print("=" * 60)
        for market, r in sorted(results.items(), key=lambda x: -x[1]["vibe_score"]):
            print(f"  {market:8s} | {r['product'][:30]:30s} | VIBE={r['vibe_score']:5.1f} [{r['score_band']}] | verbatims={r['verbatim_count']} | hack_signals={r['hackability_signals']}")


if __name__ == "__main__":
    main()
