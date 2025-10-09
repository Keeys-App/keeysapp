from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

# Replace postgresql:// with postgresql+psycopg:// for psycopg3
database_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+psycopg://")

# Create engine with connection pool settings
engine = create_engine(
    database_url,
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

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
