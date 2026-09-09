import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base

# Default to SQLite for local development; easily overridden for PostgreSQL via DATABASE_URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./bhandar_setu.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create database tables based on SQLAlchemy metadata."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency for yielding database session."""
    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()
