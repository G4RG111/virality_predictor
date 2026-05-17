"""Application configuration via environment variables."""
from __future__ import annotations

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file so uvicorn works from any working directory.
_ENV_FILE = Path(__file__).resolve().parent.parent.parent / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")

    # Database
    database_url: str = "postgresql://vibe:vibepass@localhost:5432/vibe_db"

    # App
    secret_key: str = "dev-secret-change-in-production"
    environment: str = "development"
    debug: bool = False

    # File storage
    upload_dir: Path = Path("./uploads")
    max_upload_size_mb: int = 50

    # ML Pipeline
    ml_pipeline_path: Path = Path("../ml")
    embedding_model: str = "all-MiniLM-L6-v2"
    use_ml_model: bool = False            # False = weighted formula; True = XGBoost (Phase 3)

    # Score confidence thresholds
    min_reviews_medium: int = 50
    min_reviews_high: int = 200

    # API
    api_prefix: str = "/api/v1"
    # Set CORS_ORIGINS env var as comma-separated URLs in production.
    # "*" means allow all origins (fine for a public demo).
    cors_origins_str: str = (
        "http://localhost:3000,http://localhost:3001,"
        "http://localhost:3002,http://localhost:3003,"
        "http://127.0.0.1:3000"
    )

    @property
    def cors_origins(self) -> list[str]:
        raw = self.cors_origins_str.strip()
        if raw == "*":
            return ["*"]
        return [o.strip() for o in raw.split(",") if o.strip()]

    def is_production(self) -> bool:
        return self.environment == "production"


settings = Settings()
