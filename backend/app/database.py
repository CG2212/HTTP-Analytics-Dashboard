from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.dialects.postgresql import JSONB
import datetime

from app.config import DATABASE_URL
from app.logging_config import setup_logging, get_logger

logger = get_logger("app.database")

# Create the async engine with connection pooling for PostgreSQL
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=5,          # Maintain up to 5 persistent connections
    max_overflow=0,
    pool_timeout=1      # Allow up to 1 extra temporary connections under heavy load
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

class HTTPSessionModel(Base):
    __tablename__ = "http_sessions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    method = Column(String(10), index=True)
    url = Column(String(500))
    status_code = Column(Integer, index=True)
    user_agent = Column(String(500), index=True)
    client_ip = Column(String(50))
    
    # Use native PostgreSQL JSONB for flexible, fast header queries
    request_headers = Column(JSONB)
    response_headers = Column(JSONB)

async def init_db():
    logger.debug("Initializing database engine connection...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error("Failed to initialize database tables", exc_info=True)
        raise e