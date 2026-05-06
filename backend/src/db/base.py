"""
DATABASE: base
PURPOSE: SQLAlchemy Base and database configuration
ENCODING: UTF-8 WITHOUT BOM
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

_SQLITE_DEFAULT = "sqlite:///./soarb2b.db"
_raw_url = (os.getenv("DATABASE_URL") or _SQLITE_DEFAULT).strip()
DATABASE_URL = _raw_url if _raw_url else _SQLITE_DEFAULT

# Validate format so create_engine never receives invalid URL
_lower = DATABASE_URL.lower()
if not (_lower.startswith("sqlite://") or _lower.startswith("postgresql://") or _lower.startswith("postgres://")):
    raise ValueError(
        "DATABASE_URL must be a valid SQLAlchemy URL (e.g. sqlite:///./soarb2b.db or postgresql://user:pass@host/db). "
        f"Got: {DATABASE_URL[:50]!r}..."
    )

# Determine database type
IS_SQLITE = "sqlite" in DATABASE_URL.lower()
IS_POSTGRESQL = "postgresql" in DATABASE_URL.lower() or "postgres" in DATABASE_URL.lower()

# Create engine with appropriate configuration
if IS_SQLITE:
    # SQLite configuration (development)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False   # Set to True for SQL query logging
    )
elif IS_POSTGRESQL:
    # PostgreSQL configuration (production)
    # Add connection pooling and other optimizations
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,   # Connection pool size
        max_overflow=20,   # Maximum overflow connections
        pool_pre_ping=True,   # Verify connections before using
        echo=False   # Set to True for SQL query logging
    )
else:
    # Default configuration for other databases
    engine = create_engine(
        DATABASE_URL,
        echo=False
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()


def get_db():
    """
    Dependency function to get database session.
    Use this in FastAPI route dependencies.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.
    Call this on application startup.
    """
    Base.metadata.create_all(bind=engine)

