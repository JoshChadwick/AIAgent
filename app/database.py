from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


def make_engine(url: str | None = None):
    return create_engine(url or get_settings().database_url, pool_pre_ping=True)


SessionLocal = sessionmaker(bind=make_engine(), autoflush=False, autocommit=False)


def get_session():
    with SessionLocal() as session:
        yield session
