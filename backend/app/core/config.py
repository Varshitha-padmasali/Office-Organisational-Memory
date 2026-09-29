"""
Application configuration.

Settings are loaded from environment variables (and a local .env file in
development). We use pydantic's BaseSettings so that:
  - Every config value is typed and validated at startup (fail fast).
  - Nothing is ever hardcoded in source code (12-factor app style).
  - The same code works locally, in Docker, and in production by only
    changing environment variables.
"""

from functools import lru_cache
from typing import List

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- General ---
    PROJECT_NAME: str = "Office Organizational Memory"
    ENVIRONMENT: str = "development"  # development | staging | production
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # --- Database ---
    # Example: postgresql+asyncpg://user:password@localhost:5432/org_memory
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/org_memory"

    # --- Auth (scaffolding only for Day 1 — not wired to real endpoints yet) ---
    JWT_SECRET: str = "change-me-in-env"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    # --- AI provider (used starting Day 3+, not called on Day 1) ---
    GEMINI_API_KEY: str = ""

    # --- CORS ---
    # Comma-separated list of allowed origins, e.g.
    # "http://localhost:3000,https://app.example.com"
    BACKEND_CORS_ORIGINS: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse BACKEND_CORS_ORIGINS into a clean list of origins."""
        if not self.BACKEND_CORS_ORIGINS:
            return []
        return [origin.strip() for origin in self.BACKEND_CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """
    Cached settings accessor.

    Using lru_cache means the .env file / environment is only parsed once
    per process, and Settings() can be safely called anywhere (routes,
    services, tests) without re-parsing on every call.
    """
    return Settings()
