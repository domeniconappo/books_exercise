import typing as tp

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import make_settings

settings = make_settings()

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.APP_ENV == "development",
    pool_pre_ping=True,
)

sync_engine = create_engine(
    settings.DATABASE_URL.replace("+aiosqlite", ""),
    echo=True,  # only used in development for testing
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> tp.AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


DB = tp.Annotated[AsyncSession, Depends(get_db)]


def get_db_sync():
    """Used for tests in shell"""
    return sessionmaker(bind=sync_engine, expire_on_commit=False)
