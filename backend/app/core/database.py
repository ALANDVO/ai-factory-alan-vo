"""Database session management."""
from contextlib import asynccontextmanager
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from app.core.config import get_settings
from app.models.base import Base


engine = None
async_session_maker = None


def init_db() -> None:
    """Initialize database engine and session maker."""
    global engine, async_session_maker
    settings = get_settings()
    engine = create_async_engine(
        settings.database_url,
        echo=settings.debug,
        poolclass=NullPool,
    )
    async_session_maker = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


async def create_tables() -> None:
    """Create all database tables."""
    if engine is None:
        init_db()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    global engine
    if engine:
        await engine.dispose()
        engine = None


@asynccontextmanager
async def get_session() -> AsyncSession:
    """Get a database session."""
    if async_session_maker is None:
        init_db()
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_session_dependency() -> AsyncSession:
    """FastAPI dependency for database session."""
    async with get_session() as session:
        yield session