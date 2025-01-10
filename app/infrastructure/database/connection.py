"""Database connection management.

Production-ready implementation dengan:
- Configurable connection pool settings
- Pool timeout dan recycle untuk stale connection prevention
- Health check method
- Logging untuk monitoring
"""

import logging
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


_engine: AsyncEngine | None = None
_async_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Get or create async database engine dengan configurable pool settings."""
    global _engine
    if _engine is None:
        settings = get_settings()
        try:
            _engine = create_async_engine(
                settings.database_url,
                echo=settings.debug,
                pool_pre_ping=True,
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow,
                pool_timeout=settings.db_pool_timeout,
                pool_recycle=settings.db_pool_recycle,
            )
            logger.info(
                f"Database engine created: pool_size={settings.db_pool_size}, "
                f"max_overflow={settings.db_max_overflow}, "
                f"pool_timeout={settings.db_pool_timeout}s, "
                f"pool_recycle={settings.db_pool_recycle}s"
            )
        except Exception as e:
            logger.error(f"Failed to create database engine: {e}")
            raise
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    """Get or create async session maker."""
    global _async_session_maker
    if _async_session_maker is None:
        engine = get_engine()
        _async_session_maker = async_sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False, autoflush=False
        )
    return _async_session_maker


@asynccontextmanager
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session dengan proper error handling."""
    session_maker = get_session_maker()
    session = session_maker()
    try:
        yield session
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Database session error: {e}")
        raise
    except Exception as e:
        await session.rollback()
        logger.error(f"Unexpected error in database session: {e}")
        raise
    finally:
        await session.close()


async def health_check() -> dict[str, Any]:
    """Check database connectivity dan return health status."""
    result: dict[str, Any] = {
        "status": "unhealthy",
        "connected": False,
        "latency_ms": None,
        "error": None,
    }

    try:
        engine = get_engine()
        start_time = time.time()

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))

        latency = (time.time() - start_time) * 1000

        result.update({
            "status": "healthy",
            "connected": True,
            "latency_ms": round(latency, 2),
        })
        logger.debug(f"Database health check passed: {latency:.2f}ms")

    except SQLAlchemyError as e:
        result["error"] = str(e)
        logger.warning(f"Database health check failed: {e}")
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"Unexpected error in database health check: {e}")

    return result


async def init_db() -> None:
    """Initialize database - create all tables."""
    try:
        engine = get_engine()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully")
    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


async def close_db() -> None:
    """Close database connection dan cleanup resources."""
    global _engine, _async_session_maker
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _async_session_maker = None
        logger.info("Database connection closed")
