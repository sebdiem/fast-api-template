from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from datetime import UTC, datetime

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from template_app.core import config

# Database engine configuration
engine = create_async_engine(
    config.POSTGRESQL_URL.replace("postgresql:", "postgresql+asyncpg:"),
    # Pool sizes for development (adjust for production)
    pool_size=5 if config.ENV == "dev" else 2,
    max_overflow=10 if config.ENV == "dev" else 2,
    pool_pre_ping=True,
    pool_timeout=60,  # Increase timeout from default 30s
    pool_recycle=3600,  # Recycle connections every hour
    # Async-specific settings
    echo=config.DEBUG,
    future=True,
)

SESSION_OPTIONS = dict(
    expire_on_commit=False,
    autoflush=True,
    class_=AsyncSession,
)

SessionLocal = async_sessionmaker(engine, **SESSION_OPTIONS)  # type: ignore


async def get_session(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """Get a database session for FastAPI dependency injection."""
    async with SessionLocal() as session:
        if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
            # Whole request wrapped in one transaction (like django ATOMIC_REQUESTS)
            async with session.begin():
                # In case of error the context manager will rollback as needed
                yield session
        else:
            try:
                yield session
            finally:
                if session.in_transaction():
                    # Rollback any existing transaction (should not happen)
                    await session.rollback()


@asynccontextmanager
async def get_session_context() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session as an async context manager for direct usage."""
    async with SessionLocal() as session:
        async with session.begin():
            yield session


async def init_db_connections():
    """Initialize database connections."""
    pass  # Engine is created lazily


async def close_db_connections():
    """Close database connections."""
    await engine.dispose()


def now_factory():
    return datetime.now(UTC)


def escape_like(s: str) -> str:
    # Escape backslash first, then SQL LIKE wildcards
    return s.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
