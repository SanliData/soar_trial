"""
CONFIG: settings
PURPOSE: Centralized env validation with fail-fast on startup (production readiness)
ENCODING: UTF-8 WITHOUT BOM
"""

from __future__ import annotations

import os
import logging
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)


def get_int_env(key: str, default: int) -> int:
    raw = os.getenv(key)
    if raw is None or not str(raw).strip():
        return default
    try:
        return int(str(raw).strip())
    except ValueError:
        raise ValueError(f"{key} must be a valid integer")


def get_float_env(key: str, default: float) -> float:
    raw = os.getenv(key)
    if raw is None or not str(raw).strip():
        return default
    try:
        return float(str(raw).strip())
    except ValueError:
        raise ValueError(f"{key} must be a valid float")


def get_bool_env(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None or not str(raw).strip():
        return default
    return str(raw).strip().lower() == "true"


class Settings(BaseSettings):
    """
    Application settings with fail-fast for required production env vars.
    Load .env from backend/ (caller must load_dotenv before first use if needed).
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ***REMOVED*** --- Required for all environments (with defaults for dev) ---
    ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./finderos.db"
    JWT_SECRET: Optional[str] = None
    SOARB2B_API_KEYS: str = ""

    ***REMOVED*** --- Optional / feature flags ---
    FINDEROS_VERSION: str = "0.1.0"
    FINDEROS_CORS_ORIGINS: str = ""
    FINDEROS_HOST: str = "0.0.0.0"
    FINDEROS_PORT: str = "8000"
    REDIS_URL: Optional[str] = None
    REDIS_HOST: str = "localhost"
    REDIS_PORT: str = "6379"
    REDIS_DB: str = "0"
    REDIS_REQUIRED: bool = False
    SOARB2B_ADMIN_EMAILS: str = ""
    SOARB2B_ADMIN_KEYS: str = ""
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    BASE_URL: str = ""
    FRONTEND_ORIGIN: str = ""
    OPENAI_API_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    ENABLE_DOCS: bool = True
    ***REMOVED*** --- Cloud Run / generic PaaS (optional; DigitalOcean uses FINDEROS_PORT only) ---
    K_SERVICE: Optional[str] = None
    SKIP_PORT_CHECK: bool = False
    FINDEROS_USE_HTTPS: bool = False
    FINDEROS_SSL_CERTFILE: Optional[str] = None
    FINDEROS_SSL_KEYFILE: Optional[str] = None

    @field_validator("ENV", mode="before")
    @classmethod
    def normalize_env(cls, v: object) -> str:
        if v is None or (isinstance(v, str) and not v.strip()):
            return "development"
        return str(v).strip().lower() if isinstance(v, str) else str(v)

    @field_validator("REDIS_REQUIRED", "SKIP_PORT_CHECK", "FINDEROS_USE_HTTPS", mode="before")
    @classmethod
    def parse_bool_false_default(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if v is None or (isinstance(v, str) and not v.strip()):
            return False
        return str(v).strip().lower() in ("1", "true", "yes", "on")

    @field_validator("ENABLE_DOCS", mode="before")
    @classmethod
    def parse_bool_enable_docs(cls, v: object) -> bool:
        if isinstance(v, bool):
            return v
        if v is None or (isinstance(v, str) and not v.strip()):
            return True
        return str(v).strip().lower() in ("1", "true", "yes", "on")

    def validate_production_required(self) -> None:
        """
        Call after init: if ENV=production, require DATABASE_URL (PostgreSQL),
        JWT_SECRET, and SOARB2B_API_KEYS. Raises ValueError on failure.
        """
        if self.ENV != "production":
            return
        errors: list[str] = []
        if not self.DATABASE_URL or "sqlite" in self.DATABASE_URL.lower():
            errors.append("ENV=production requires DATABASE_URL to be PostgreSQL (no SQLite).")
        if not self.JWT_SECRET or not self.JWT_SECRET.strip():
            errors.append("ENV=production requires JWT_SECRET to be set.")
        if not self.SOARB2B_API_KEYS or not self.SOARB2B_API_KEYS.strip():
            errors.append("ENV=production requires SOARB2B_API_KEYS to be set.")
        if not self.FINDEROS_CORS_ORIGINS or not self.FINDEROS_CORS_ORIGINS.strip():
            errors.append("ENV=production requires FINDEROS_CORS_ORIGINS (comma-separated origins; wildcard not allowed).")
        if not self.BASE_URL or not self.BASE_URL.strip():
            errors.append("ENV=production requires BASE_URL (e.g. https://soarb2b.com).")
        else:
            b = self.BASE_URL.strip().lower()
            if not b.startswith("https://"):
                errors.append("ENV=production requires BASE_URL to be HTTPS.")
        if not self.GOOGLE_CLIENT_ID or not self.GOOGLE_CLIENT_ID.strip():
            errors.append("ENV=production requires GOOGLE_CLIENT_ID for Sign in with Google.")
        if not self.GOOGLE_CLIENT_SECRET or not self.GOOGLE_CLIENT_SECRET.strip():
            errors.append("ENV=production requires GOOGLE_CLIENT_SECRET for Sign in with Google.")
        if errors:
            raise ValueError("Production env validation failed: " + "; ".join(errors))


def get_settings() -> Settings:
    """Load and validate settings (singleton-style, creates new each time for simplicity)."""
    s = Settings()
    s.validate_production_required()
    return s
