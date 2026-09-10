import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.models import Base

# Default to SQLite for local development in backend/bhandar_setu.db; easily overridden for PostgreSQL via DATABASE_URL
env_db_url = os.getenv("DATABASE_URL")
if not env_db_url:
    backend_dir = Path(__file__).resolve().parent.parent
    db_file_path = backend_dir / "bhandar_setu.db"
    DATABASE_URL = f"sqlite:///{db_file_path.as_posix()}"
else:
    DATABASE_URL = env_db_url

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
