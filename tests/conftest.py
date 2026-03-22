from pathlib import Path
from typing import AsyncGenerator

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlmodel import SQLModel

from app.config import Settings
from app.database import get_db
from app.main import app


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def settings() -> Settings:
    return Settings(DATABASE_URL="sqlite+aiosqlite:///books_test.db")


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def engine(settings: Settings) -> AsyncGenerator[AsyncEngine, None]:
    """
    Creates/drops tables once per test session.
    """
    engine = create_async_engine(
        settings.DATABASE_URL,
        future=True,
        echo=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

    await engine.dispose()


@pytest_asyncio.fixture(scope="session", loop_scope="session")
def session_factory(engine):
    return async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )


@pytest_asyncio.fixture(loop_scope="session")
async def db_session(engine: AsyncEngine) -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        for table in reversed(SQLModel.metadata.sorted_tables):
            await conn.execute(table.delete())

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture(loop_scope="session")
async def populate(db_session: AsyncSession) -> None:
    statements = text(Path("./dataset.sql").read_text())
    await db_session.execute(statements)
    await db_session.commit()
    return


@pytest_asyncio.fixture()
async def client(
    session_factory: async_sessionmaker,
) -> AsyncGenerator[AsyncClient, None]:
    """
    One shared AsyncClient for the entire test session.
    """

    async def override_get_db():
        async with session_factory() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()
