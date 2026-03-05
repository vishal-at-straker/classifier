"""Database session and engine."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from src.config import get_settings
from src.db.models import Base  # noqa: F401 - Base used for create_all


_engine = None
_SessionLocal = None


def get_engine():
    global _engine
    if _engine is None:
        settings = get_settings()
        # SQLite: check_same_thread=False for FastAPI
        connect_args = {}
        if settings.database_url.startswith("sqlite"):
            connect_args["check_same_thread"] = False
        _engine = create_engine(
            settings.database_url,
            connect_args=connect_args,
            echo=False,
        )
    return _engine


def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return _SessionLocal


def get_db() -> Session:
    """Dependency: yield a DB session."""
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Call once at startup or via script."""
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
