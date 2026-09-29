"""
Database connection layer.

Day 1 scope: establish the async SQLAlchemy engine/session machinery and a
FastAPI dependency (`get_db`) that routes can use later. We deliberately do
NOT define the full RAG schema (documents, chunks, embeddings, etc.) yet —
that lands on Day 2+ once retrieval design is finalized. Only a minimal
`User` model exists today so the auth scaffolding in `core/security.py` has
somewhere to eventually attach.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import get_settings
from app.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# `future=True` / async engine talking to Postgres via asyncpg driver.
# pool_pre_ping avoids using stale connections after the DB restarts.
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session per-request."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> bool:
    """
    Lightweight connectivity check used by the /health endpoint.

    Returns True if a trivial query succeeds, False otherwise. Never raises
    — callers should treat False as "database currently unreachable".
    """
    from sqlalchemy import text

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:  # noqa: BLE001 - we want to catch anything here
        logger.warning("Database health check failed: %s", exc)
        return False
