"""SQLAlchemy engine, session factory and initialisation."""
from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create tables and seed demo data if the database is empty."""
    # Import models so they register on Base.metadata before create_all.
    import models  # noqa: F401
    import demo_data  # noqa: F401

    Base.metadata.create_all(bind=engine)
    demo_data.seed_if_empty(SessionLocal)
