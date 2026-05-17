"""FastAPI application factory."""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import Base, engine
from .routers import products, scoring, ingestion, explainability, trends, hackability, reviews, social, brief_analysis

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="VIBE — Viral Impact & Buzz Estimation",
    description="SharkNinja Virality Intelligence Engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = settings.api_prefix
app.include_router(products.router, prefix=prefix)
app.include_router(scoring.router, prefix=prefix)
app.include_router(ingestion.router, prefix=prefix)
app.include_router(explainability.router, prefix=prefix)
app.include_router(trends.router, prefix=prefix)
app.include_router(hackability.router, prefix=prefix)
app.include_router(reviews.router, prefix=prefix)
app.include_router(social.router, prefix=f"{prefix}/social", tags=["social"])
app.include_router(brief_analysis.router, prefix=prefix)


@app.get("/health")
def health():
    return {"status": "ok", "service": "vibe-backend"}


@app.get("/")
def root():
    return {"message": "VIBE API. See /docs for full API reference."}
