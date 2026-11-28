"""Lazy SQLModel connection for Supabase; TinyDB auth remains independent."""

import os
from typing import Generator

from fastapi import HTTPException, status
from sqlalchemy.engine import make_url
from sqlmodel import Session, SQLModel, create_engine

from .config import load_project_env
from . import inventory_models  # noqa: F401 - registers table metadata

_engine = None


def get_inventory_engine():
    global _engine
    load_project_env()
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Inventory database is not configured. Set DATABASE_URL to the Supabase transaction-pooler URI.",
        )
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://"):]
    parsed_url = make_url(database_url)
    if parsed_url.get_backend_name() != "postgresql":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="DATABASE_URL must point to a PostgreSQL database.",
        )
    # The API declares psycopg2-binary. SQLAlchemy 2 otherwise defaults
    # postgresql:// URLs to psycopg (v3), which is not installed here.
    if parsed_url.drivername == "postgresql":
        parsed_url = parsed_url.set(drivername="postgresql+psycopg2")
    if _engine is None:
        _engine = create_engine(parsed_url, pool_pre_ping=True, pool_recycle=300)
    return _engine


def initialize_inventory_database() -> bool:
    """Create missing inventory tables when a Supabase URL is configured."""
    load_project_env()
    if not os.getenv("DATABASE_URL", "").strip():
        return False
    SQLModel.metadata.create_all(get_inventory_engine())
    return True


def get_db() -> Generator[Session, None, None]:
    """Provide one SQLModel session per inventory request."""
    try:
        engine = get_inventory_engine()
    except HTTPException:
        raise
    with Session(engine) as session:
        yield session


def close_inventory_database() -> None:
    global _engine
    if _engine is not None:
        _engine.dispose()
        _engine = None
