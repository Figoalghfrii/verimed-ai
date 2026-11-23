"""Async SQLAlchemy 2.0 database engine and session management."""

from collections.abc import AsyncGenerator
from typing import Any

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from verimed_api.core.config import get_settings

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    """Lazily initialize and return the singleton async database engine."""
    global _engine
    if _engine is None:
        settings = get_settings()
        if not settings.database_url:
            raise RuntimeError(
                "DATABASE_URL is not configured. Set DATABASE_URL before opening database sessions."
            )
        _engine = create_async_engine(
            settings.database_url,
            echo=False,
            pool_pre_ping=True,
            future=True,
        )
    return _engine


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Lazily return the async_sessionmaker bound to the configured engine."""
    global _session_factory
    if _session_factory is None:
        _session_factory = async_sessionmaker(
            bind=get_engine(),
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
    return _session_factory


class _LazyAsyncSessionFactory:
    """Callable lazy proxy preserving `async with AsyncSessionLocal() as session` compatibility."""

    def __call__(self, *args: Any, **kwargs: Any) -> AsyncSession:
        return get_session_factory()(*args, **kwargs)


AsyncSessionLocal = _LazyAsyncSessionFactory()


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency providing a scoped AsyncSession."""
    async with AsyncSessionLocal() as session:
        yield session
