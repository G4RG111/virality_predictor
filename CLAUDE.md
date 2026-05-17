# VIBE: Viral Impact & Buzz Estimation
## Engineering Handbook for SharkNinja Virality Intelligence Platform

---

## Project Overview

VIBE predicts whether a SharkNinja product will become culturally/socially viral — before and shortly after launch — using iHUT tester data, Amazon reviews, and social signals. The core output is a **VIBE Score (0–100)** with full dimension-level explainability via SHAP.

**Virality ≠ Satisfaction.** A product can be highly rated, useful, and beloved — and still never go viral. Viral products have *performative utility*: people want to be seen using them. This distinction is foundational to every model, feature, and UI decision.

---

## Architecture Philosophy

- **Monorepo**: `frontend/` (Next.js), `backend/` (FastAPI), `ml/` (pure Python pipeline)
- The ML pipeline is a standalone importable package — no HTTP concerns, no FastAPI imports
- The backend is a thin orchestration layer: receives files, triggers ML jobs, stores results, serves the API
- The frontend is entirely TypeScript, strictly typed, consuming the FastAPI API only
- Each VIBE dimension is computed by an independent, swappable extractor — never couple dimensions
- SHAP explainability is not optional — every score must be decomposable to feature contributions

---

## VIBE Score Principles

- 9 dimensions, weights must always sum to 1.0
- **Hackability (25%)** is the top dimension — SharkNinja's unique viral vector
- Hackability = community-discovered alternative uses, not just intended use satisfaction
- Scores are relative to a reference corpus (viral vs. standard SharkNinja products)
- Confidence degrades gracefully below 50 reviews; never suppress a score, flag it
- `baseline + sum(SHAP_i) = VIBE_score` — this invariant must always hold

### Current Dimension Weights
| Dimension | Weight |
|-----------|--------|
| Hackability | 23% |
| Emotional Intensity | 16% |
| Shareability | 16% |
| Novelty | 11% |
| Creator Friendliness | 11% |
| Review Momentum | 9% |
| Recommendation Intent | 4% |
| Price-to-Wow | 2% |
| Social Buzz | 8% |

---

## Virality Modeling Philosophy

Signal extraction must distinguish:
- **Functional language**: "works well", "easy to use", "good value" → satisfaction, not virality
- **Viral language**: "obsessed", "showed everyone", "TikTok made me buy this" → virality signals
- **Hack language**: "I use it for X instead", "you can also", "didn't expect this to work as" → hackability
- **Creator language**: "for my channel", "filmed", "my followers" → creator friendliness

Never conflate star rating with virality potential. A 3-star review mentioning "went viral on TikTok" outweighs a 5-star review with only functional praise for VIBE purposes.

---

## ML Workflow Rules

- All extractors inherit `BaseDimensionExtractor` — never bypass the interface
- `feature_registry.py` is the single source of truth for dimension → extractor mapping
- Use `pdfplumber` for iHUT PDFs (not PyPDF2) — preserves layout needed to separate tester verbatims from analyst text
- Sentence-transformer embeddings via `ml/pipeline/utils/embeddings.py` only — never instantiate models inline
- Model artifacts go in `ml/data/models/` — never commit large files
- Normalization reference corpus calibration must be re-run whenever the corpus changes
- SHAP computation: Phase 1 uses analytic SHAP (weighted formula); Phase 2 uses TreeSHAP (XGBoost)

---

## Backend Conventions (FastAPI)

- All routes under `/api/v1/` prefix
- Pydantic schemas in `schemas/` — never return ORM objects directly
- Database sessions via dependency injection (`Depends(get_db)`)
- UUID primary keys everywhere — never integer IDs in public APIs
- `is_current=True` flag on `vibe_scores` — never delete old scores, only supersede them
- All file uploads return a `job_id` immediately; clients poll `/ingestion/jobs/{job_id}`
- Errors: use `HTTPException` with structured detail dicts, never bare strings

---

## Frontend Conventions (Next.js / TypeScript)

- App Router only — no Pages Router patterns
- All API calls through `lib/api-client.ts` — never fetch directly in components
- Types defined in `lib/types.ts` — shared across all components and hooks
- VIBE components in `components/vibe/` — reusable, data-driven, no business logic
- Hackability components in `components/hackability/` — separate namespace, separate concerns
- Color convention: score bands drive color tokens (low=slate, moderate=amber, high=blue, viral=violet)
- No hardcoded product names in components — all data flows through props

---

## Dashboard Philosophy

The dashboard is an **executive intelligence tool**, not a generic analytics dashboard.

- Every number must answer "so what?" — annotate scores with interpretation
- SHAP waterfall charts must show plain-English labels, not feature variable names
- The Hackability Feed is a first-class dashboard element — not a detail-page afterthought
- Virality trajectory is more important than point-in-time score — always show trend direction
- Compare view prioritizes dimension deltas over raw scores — the gap tells the story

---

## Coding Standards

- Python: black formatting, type hints on all function signatures, no bare `except`
- TypeScript: strict mode, no `any`, named exports only
- No inline SQL — SQLAlchemy ORM only
- No secrets in code — all config via environment variables through `config.py` / `.env`
- Tests live in `tests/` mirroring the source structure
- One module = one responsibility — if a file exceeds 200 lines, split it

---

## Scalability Expectations

- Phase 1: Single-process FastAPI, synchronous ML calls, SQLite acceptable for dev
- Phase 2: PostgreSQL with pgvector for review embeddings (384-dim)
- Phase 3+: Celery + Redis task queue replaces synchronous scoring
- The ML pipeline is designed to run as a Celery worker without modification
- All feature extractors must be stateless — safe for parallel execution
