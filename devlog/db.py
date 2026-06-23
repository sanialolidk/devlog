import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

load_dotenv()

_DEFAULT_DB = f"sqlite:///{Path.home() / '.devlog' / 'devlog.db'}"
_raw = os.getenv("DATABASE_URL", _DEFAULT_DB)
# Railway (and Heroku) provide postgres:// but SQLAlchemy requires postgresql://
DATABASE_URL = _raw.replace("postgres://", "postgresql://", 1) if _raw.startswith("postgres://") else _raw


class Base(DeclarativeBase):
    pass


def _make_engine():
    if DATABASE_URL.startswith("sqlite"):
        Path.home().joinpath(".devlog").mkdir(exist_ok=True)
    return create_engine(DATABASE_URL, echo=False)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


def get_session():
    """For CLI commands: returns a plain session (caller must close)."""
    return SessionLocal()


def get_db():
    """FastAPI dependency: yields a session and closes on teardown."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
