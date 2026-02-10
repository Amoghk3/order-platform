from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = None
SessionLocal = None


def init_db():
    global engine, SessionLocal

    engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

    SessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
    )
