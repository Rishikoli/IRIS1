"""
Project IRIS - SQLAlchemy Database Models
Base model and utility functions for PostgreSQL integration
"""

from datetime import datetime
from typing import Any, Dict
import json
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, JSON, BigInteger
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy as sa

from config import settings

# Create base class for all models
Base = declarative_base()

# JSON serialization helpers for JSONB fields
class JSONBType(sa.TypeDecorator):
    """Custom type for handling JSONB fields with proper serialization"""

    impl = sa.Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is not None:
            return json.dumps(value, default=str)
        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            return json.loads(value)
        return value

# Utility functions for JSONB handling
def serialize_jsonb(value: Any) -> str:
    """Serialize value for JSONB storage"""
    return json.dumps(value, default=str)

def deserialize_jsonb(value: str) -> Any:
    """Deserialize value from JSONB storage"""
    return json.loads(value) if value else None

# Base model with common fields
class BaseModel(Base):
    """Base model with common fields for all tables"""

    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

# Database connection setup
def create_database_engine():
    """Create SQLAlchemy engine with connection pooling"""
    return create_engine(
        settings.database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=3600,   # Recycle connections after 1 hour
        echo=settings.is_development  # Log SQL in development
    )

# Global engine and session factory
engine = create_database_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Session:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """Create all tables in the database"""
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """Drop all tables from the database (for testing)"""
    Base.metadata.drop_all(bind=engine)
