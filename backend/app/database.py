from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Replace postgresql:// with postgresql+psycopg:// for psycopg3
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

# Create async database URL (replace psycopg with psycopg_async for async driver)
async_database_url = database_url.replace("postgresql+psycopg://", "postgresql+psycopg_async://")

# Create async engine with connection pool settings
async_engine = create_async_engine(
    async_database_url,
    pool_size=5,  # Maximum number of connections to keep in the pool
    max_overflow=10,  # Maximum number of connections to create beyond pool_size
    pool_timeout=30,  # Timeout for getting a connection from the pool (seconds)
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_pre_ping=True,  # Verify connections before using them
    connect_args={
        "connect_timeout": 10,  # Connection timeout in seconds
    },
    echo=False,  # Set to True for SQL query logging (development only)
)

# Keep sync engine for migrations only
engine = create_engine(
    database_url,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,
    pool_pre_ping=True,
    connect_args={
        "connect_timeout": 10,
    },
    echo=False,
)

# Async session for application
AsyncSessionLocal = async_sessionmaker(
    async_engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Sync session for migrations only (backward compatibility)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


async def async_get_db():
    """Async database dependency"""
    async with AsyncSessionLocal() as session:
        yield session
