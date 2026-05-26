from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# Create the SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,       # Test connection before using it
    pool_size=10,             # Keep 10 connections in pool
    max_overflow=20,          # Allow 20 extra connections when pool is full
)

# SessionLocal is a factory that creates new database sessions
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """
    Dependency function that yields a database session.
    Used in FastAPI routes via Depends(get_db).
    Automatically closes the session when done.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
