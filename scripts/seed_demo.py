#!/usr/bin/env python3
"""
VIBE Demo Seed Script
=====================
Populates the database with demo products and reviews so the dashboard
has compelling data on first launch.

Products seeded:
  1. [DEMO] Ninja Slushie Maker  -- HIGH/VIRAL (hackability, social buzz)
  2. [DEMO] Ninja Creami         -- MODERATE/HIGH
  3. [DEMO] Chanel Slim UI       -- real iHUT data (LOW -- non-viral premium product)
  4. [DEMO] Chanel UK Slim UI    -- real iHUT data (LOW)

Usage (from vibe-predictor/ root):
  python scripts/seed_demo.py
  python scripts/seed_demo.py --reset   # drop existing [DEMO] data first
"""
from __future__ import annotations

import sys
import os
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
ML_PATH = REPO_ROOT / "ml"
BACKEND_PATH = REPO_ROOT / "backend"
sys.path.insert(0, str(ML_PATH))
sys.path.insert(0, str(BACKEND_PATH))

try:
    from dotenv import load_dotenv
    load_dotenv(REPO_ROOT / ".env")
except ImportError:
    pass

logging.basicConfig(level=logging.INFO, format="%(levelname)s  %(message)s")
log = logging.getLogger("seed_demo")

# Real iHUT PDF paths (one directory above vibe-predictor/)
IHUT_PDF_PATHS = {
    "Chanel Slim UI (Global)": REPO_ROOT.parent / "Chanel Slim UI IHUT MasterDeck_compressed_compressed.pdf",
    "Chanel Slim UI (UK)": REPO_ROOT.parent / "Chanel UK Slim UI IHUT_Master deck_compressed_compressed.pdf",
}

# ── Synthetic review banks ────────────────────────────────────────────────────
_SLUSHIE_REVIEWS = [
    ("I use this to make smoothies AND cocktail slushies! Total hack - game changer!", 5.0),
    ("TikTok showed me frozen lemonade in this thing. Absolute genius!", 5.0),
    ("You can also freeze coffee in it for the most amazing frappuccino.", 5.0),
    ("Didn't expect this to work as a sorbet maker but wow IT DOES!", 5.0),
    ("Hack: pour in pre-made juice, freeze, blend - perfect granita in minutes.", 5.0),
    ("I use it for dog's frozen treats now. Alternative uses are ENDLESS.", 4.0),
    ("My roommates discovered it makes incredible frozen margaritas. We use it every day.", 5.0),
    ("Someone on Instagram showed the slushie trick for protein shakes. Life changing.", 5.0),
    ("I am OBSESSED. Showed everyone at my BBQ and now 4 friends ordered it.", 5.0),
    ("I literally screamed when I first used this. Slushies come out PERFECT.", 5.0),
    ("Cannot stop talking about this. My entire office is now obsessed.", 5.0),
    ("This is the most fun kitchen appliance I have ever owned, no exaggeration.", 5.0),
    ("Posted a video of the slushie coming out and got 40k views overnight!", 5.0),
    ("Brought this to a pool party and it became the main event. Everyone wanted one.", 5.0),
    ("My kid thinks I am the coolest mom in the neighborhood because of this machine.", 5.0),
    ("Filmed my first YouTube review just for this product. The swirl is SO satisfying.", 5.0),
    ("The color of the slushie against a white background = perfect thumbnail shot.", 5.0),
    ("The pour is incredibly photogenic. Every influencer in my feed has one now.", 4.0),
    ("Already bought three as gifts. Best housewarming present ever.", 5.0),
    ("Gave one to my sister AND my mom within a week of buying my own.", 5.0),
    ("If you are reading this review, just buy it. You will not regret it.", 5.0),
    ("Bought a second one for my office break room. My team loves it.", 5.0),
    ("Never seen anything like this. I thought slushies were only for gas stations.", 5.0),
    ("Blew my mind that this exists. How did we live without it?", 5.0),
    ("This is the first appliance that genuinely surprised me in years.", 5.0),
    ("For the price this is absolutely insane value. Expected to pay triple.", 5.0),
    ("Shocked at how affordable this is compared to what it delivers.", 4.0),
    ("Slushies are amazing but the machine is a bit loud. Still 5 stars.", 4.0),
    ("Cleans easily if you do it right after use. Slushie quality is unreal.", 5.0),
    ("My kids use it every single day after school. Worth every penny.", 5.0),
]

_CREAMI_REVIEWS = [
    ("This machine made me feel like a pastry chef. Better than Haagen-Dazs.", 5.0),
    ("I make protein ice cream every day now. The texture is incredible.", 5.0),
    ("TikTok was RIGHT about the Ninja Creami. Life will never be the same.", 5.0),
    ("I have made 40 different flavors in the past month. Cannot stop experimenting.", 5.0),
    ("Gifted one to my sister and she cried happy tears. That good.", 5.0),
    ("You can make Dole Whip at home with this. Disney fans will understand.", 5.0),
    ("Ice cream comes out so creamy and smooth. Posted a video and friends bombarded me.", 4.0),
    ("My nutritionist approved my protein ice cream recipe. Obsessed.", 5.0),
    ("Takes 24 hours to freeze but the wait is absolutely worth it every time.", 4.0),
    ("Kids think we own a gelato shop. Best parenting hack of the year.", 5.0),
    ("The crunchy mix-in feature is mind-blowing. Cookie pieces throughout is heaven.", 5.0),
    ("Super loud when running but I forgive it because the results are amazing.", 3.0),
    ("Made mango sorbet from fresh fruit. Three ingredients. Perfection.", 5.0),
    ("Everyone at book club wanted the recipe when I brought my Creami ice cream.", 5.0),
    ("For the price it is worth every cent. Professional results at home.", 5.0),
    ("Would buy again. Have already bought two more as gifts.", 5.0),
    ("More complicated than expected but YouTube tutorials make it easy.", 3.0),
    ("Ice cream is SO much better than store-bought. Addicting to make.", 5.0),
    ("I can control exactly what goes in. Great for my dietary restrictions.", 4.0),
    ("Ninja has completely changed my relationship with dessert.", 5.0),
]


def _make_reviews(texts_ratings: list[tuple[str, float]], source: str = "amazon") -> list[dict]:
    base_date = datetime(2024, 1, 1)
    return [
        {
            "review_text": text,
            "rating": rating,
            "source": source,
            "review_date": (base_date + timedelta(days=i * 3)).date(),
            "verified_purchase": True,
            "helpful_votes": max(0, int((rating - 3) * 10 + i % 5)),
            "reviewer_type": "consumer",
            "market": "US",
        }
        for i, (text, rating) in enumerate(texts_ratings)
    ]


def seed(reset: bool = False) -> None:
    import sqlalchemy as sa
    from sqlalchemy.orm import sessionmaker

    db_url = os.environ.get(
        "DATABASE_URL", "postgresql://vibe:vibepass@localhost:5432/vibe_db"
    )
    # Map Docker service name to localhost for local runs
    db_url = db_url.replace("@db:", "@localhost:")

    engine = sa.create_engine(db_url, pool_pre_ping=True)
    SessionFactory = sessionmaker(bind=engine)

    log.info("Connecting to: %s", db_url.split("@")[-1])

    from app.models.product import Product
    from app.models.review import Review
    from app.models.vibe_score import VibeScore, DimensionScore, ShapExplanation

    with SessionFactory() as db:
        if reset:
            log.info("Resetting existing [DEMO] data...")
            demo_ids = [p.id for p in db.query(Product).filter(Product.name.like("%[DEMO]%")).all()]
            for pid in demo_ids:
                # Cascade deletes via SQLAlchemy relationships
                p = db.query(Product).filter(Product.id == pid).first()
                if p:
                    db.delete(p)
            db.commit()
            log.info("Reset complete.")

        products_to_seed = [
            {
                "meta": {
                    "name": "[DEMO] Ninja Slushie Maker",
                    "sku": "NC300-DEMO",
                    "category": "Kitchen Appliances",
                    "market": "US",
                    "price_usd": 49.99,
                    "description": "Make perfectly textured slushies, frozen cocktails, and more.",
                },
                "reviews": _make_reviews(_SLUSHIE_REVIEWS),
            },
            {
                "meta": {
                    "name": "[DEMO] Ninja Creami",
                    "sku": "NC301E-DEMO",
                    "category": "Kitchen Appliances",
                    "market": "US",
                    "price_usd": 199.99,
                    "description": "Turn frozen ingredients into ice cream, sorbet, smoothie bowls.",
                },
                "reviews": _make_reviews(_CREAMI_REVIEWS),
            },
        ]

        # Load real iHUT PDFs
        from pipeline.ingestion.ihut_extractor import extract_ihut_pdf

        for product_name, pdf_path in IHUT_PDF_PATHS.items():
            if not pdf_path.exists():
                log.warning("iHUT PDF not found, skipping: %s", pdf_path)
                continue
            log.info("Extracting: %s", pdf_path.name)
            doc = extract_ihut_pdf(pdf_path)
            verbatims = doc.verbatim_chunks
            log.info("  Extracted %d verbatim chunks from %s", len(verbatims), pdf_path.name)
            ihut_reviews = [
                {
                    "review_text": chunk.text[:1000],
                    "rating": None,
                    "source": "ihut",
                    "review_date": None,
                    "verified_purchase": False,
                    "helpful_votes": 0,
                    "reviewer_type": "tester",
                    "market": chunk.market,
                }
                for chunk in verbatims
                if len(chunk.text.strip()) > 20
            ]
            products_to_seed.append({
                "meta": {
                    "name": f"[DEMO] {product_name}",
                    "sku": f"CHANEL-{doc.market.upper()}-DEMO",
                    "category": "Beauty Devices",
                    "market": doc.market,
                    "price_usd": None,
                    "description": f"Chanel hair styling device iHUT cohort — {doc.market}.",
                },
                "reviews": ihut_reviews,
            })

        from pipeline.features.base_extractor import Review as MLReview
        from pipeline.scoring.score_aggregator import compute_vibe_score

        for entry in products_to_seed:
            meta = entry["meta"]
            reviews_data = entry["reviews"]
            name = meta["name"]

            existing = db.query(Product).filter(Product.name == name).first()
            if existing:
                product = existing
                log.info("Product already exists, reusing: %s", name)
            else:
                product = Product(**meta)
                db.add(product)
                db.flush()
                log.info("Created product: %s  id=%s", name, product.id)

            existing_count = db.query(Review).filter(Review.product_id == product.id).count()
            if existing_count == 0:
                for rev in reviews_data:
                    db.add(Review(product_id=product.id, **rev))
                db.flush()
                log.info("  Inserted %d reviews", len(reviews_data))
            else:
                log.info("  Reviews already exist (%d), skipping", existing_count)

            db_reviews = db.query(Review).filter(Review.product_id == product.id).all()
            ml_reviews = [
                MLReview(
                    text=r.review_text,
                    rating=float(r.rating) if r.rating else None,
                    source=r.source,
                    market=r.market,
                    reviewer_type=r.reviewer_type,
                )
                for r in db_reviews
            ]

            log.info("  Scoring %d reviews...", len(ml_reviews))
            result = compute_vibe_score(ml_reviews)

            # Supersede old score
            db.query(VibeScore).filter(
                VibeScore.product_id == product.id,
                VibeScore.is_current.is_(True),
            ).update({"is_current": False})

            vibe = VibeScore(
                product_id=product.id,
                score_version="1.0",
                vibe_score=result.vibe_score,
                score_band=result.score_band,
                confidence=result.confidence,
                confidence_value=result.confidence_value,
                baseline_score=result.baseline_score,
                model_version=result.model_version,
                is_current=True,
            )
            db.add(vibe)
            db.flush()

            # Dimension scores
            for dim, norm_score in result.dimension_scores.items():
                raw = result.dimension_raw.get(dim, 0.0)
                fv = result.feature_vectors.get(dim, {})
                signals = result.top_signals.get(dim, [])
                evidence = result.evidence_texts.get(dim, [])
                db.add(DimensionScore(
                    vibe_score_id=vibe.id,
                    dimension=dim,
                    raw_score=raw,
                    normalized_score=norm_score,
                    weight=result.dimension_weights.get(dim, 0.0),
                    weighted_contribution=result.weighted_contributions.get(dim, 0.0),
                    feature_count=str(len(signals)),
                    top_signals=signals,
                    feature_vector={k: float(v) for k, v in fv.items()},
                    evidence_texts=evidence[:10],
                ))

            # SHAP explanations — one row per dimension
            sorted_dims = sorted(result.shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
            for rank, (dim, shap_val) in enumerate(sorted_dims, start=1):
                raw = result.dimension_raw.get(dim, 0.0)
                direction = "positive" if shap_val > 0 else ("negative" if shap_val < 0 else "neutral")
                db.add(ShapExplanation(
                    vibe_score_id=vibe.id,
                    feature_name=dim,
                    shap_value=shap_val,
                    feature_value=raw,
                    feature_value_raw=f"{raw:.3f}",
                    rank_order=str(rank),
                    direction=direction,
                ))

            db.commit()
            log.info(
                "  => VIBE Score: %.1f [%s]  confidence=%s  (reviews=%d)",
                result.vibe_score, result.score_band, result.confidence, len(ml_reviews),
            )

        log.info("\nSeed complete. %d products loaded.", len(products_to_seed))
        log.info("Open http://localhost:3000/dashboard to view results.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed VIBE demo data")
    parser.add_argument("--reset", action="store_true", help="Delete existing [DEMO] data before seeding")
    args = parser.parse_args()
    seed(reset=args.reset)
