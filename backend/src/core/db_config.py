"""
DB_CONFIG: db_config
PURPOSE: Enterprise database configuration for SQLite and PostgreSQL
ENCODING: UTF-8 WITHOUT BOM
"""

import os
import logging
from typing import Optional

from src.config.settings import get_int_env, get_bool_env

logger = logging.getLogger(__name__)

_SQLITE_DEFAULT = "sqlite:///./soarb2b.db"
_raw_url = (os.getenv("DATABASE_URL") or _SQLITE_DEFAULT).strip()
DATABASE_URL = _raw_url if _raw_url else _SQLITE_DEFAULT

# Validate format
_lower = DATABASE_URL.lower()
if not (_lower.startswith("sqlite://") or _lower.startswith("postgresql://") or _lower.startswith("postgres://")):
    raise ValueError(
        "DATABASE_URL must be a valid SQLAlchemy URL (e.g. sqlite:///./soarb2b.db or postgresql://user:pass@host/db). "
        f"Got: {DATABASE_URL[:50]!r}..."
    )

# Production: forbid SQLite (must use PostgreSQL)
_env = (os.getenv("ENV") or "").strip().lower()
if _env == "production" and DATABASE_URL and "sqlite" in DATABASE_URL.lower():
    raise ValueError(
        "Production must use PostgreSQL. Set DATABASE_URL to a postgres:// URL. SQLite is not allowed when ENV=production."
    )

# Determine database type
IS_SQLITE = "sqlite" in DATABASE_URL.lower()
IS_POSTGRESQL = "postgresql" in DATABASE_URL.lower() or "postgres" in DATABASE_URL.lower()

# Database connection pool settings (PostgreSQL only)
DB_POOL_SIZE = get_int_env("DB_POOL_SIZE", 10)
DB_MAX_OVERFLOW = get_int_env("DB_MAX_OVERFLOW", 20)
DB_POOL_TIMEOUT = get_int_env("DB_POOL_TIMEOUT", 30)
DB_POOL_RECYCLE = get_int_env("DB_POOL_RECYCLE", 3600)   # 1 hour

# Connection settings
DB_CONNECT_TIMEOUT = get_int_env("DB_CONNECT_TIMEOUT", 10)
DB_ECHO_SQL = get_bool_env("DB_ECHO_SQL", False)


def get_database_config() -> dict:
    """
    Get database configuration based on database type.
    
    Returns:
        Dictionary with engine configuration
    """
    config = {
        "url": DATABASE_URL,
        "echo": DB_ECHO_SQL,
    }
    
    if IS_SQLITE:
        # SQLite configuration (development)
        config["connect_args"] = {"check_same_thread": False}
        logger.info("📦 Using SQLite database (development mode)")
        
    elif IS_POSTGRESQL:
        # PostgreSQL configuration (production)
        config.update({
            "pool_size": DB_POOL_SIZE,
            "max_overflow": DB_MAX_OVERFLOW,
            "pool_timeout": DB_POOL_TIMEOUT,
            "pool_recycle": DB_POOL_RECYCLE,
            "pool_pre_ping": True,   # Verify connections before using
            "connect_args": {
                "connect_timeout": DB_CONNECT_TIMEOUT,
                "application_name": "soarb2b-api",
            }
        })
        logger.info(f"📦 Using PostgreSQL database (pool_size={DB_POOL_SIZE}, max_overflow={DB_MAX_OVERFLOW})")
        
    else:
        # Default configuration for other databases
        logger.warning(f"⚠️ Unknown database type: {DATABASE_URL}")
    
    return config


def get_database_url() -> str:
    """Get database URL"""
    return DATABASE_URL


def is_postgresql() -> bool:
    """Check if using PostgreSQL"""
    return IS_POSTGRESQL


def is_sqlite() -> bool:
    """Check if using SQLite"""
    return IS_SQLITE


def get_connection_pool_info() -> dict:
    """
    Get connection pool information (PostgreSQL only).
    
    Returns:
        Dictionary with pool stats
    """
    if not IS_POSTGRESQL:
        return {"type": "sqlite", "pooling": False}
    
    return {
        "type": "postgresql",
        "pool_size": DB_POOL_SIZE,
        "max_overflow": DB_MAX_OVERFLOW,
        "pool_timeout": DB_POOL_TIMEOUT,
        "pool_recycle": DB_POOL_RECYCLE,
        "pool_pre_ping": True,
    }
