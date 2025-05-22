from contextlib import asynccontextmanager
from datetime import date
from itertools import count

import pytest
import pytest_asyncio
from fastapi import Depends, FastAPI
from typing import Annotated

from redis import Redis
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from httpx import AsyncClient, ASGITransport

from main import app
from src.databases.database import get_session
from src.models.trading_results_model import SpimexTradingResults, Base

from data import list_models_SpimexTradingResults

DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создаем асинхронный движок для тестовой БД
engine = create_async_engine(DATABASE_URL)

AsyncSessionLocal = async_sessionmaker(bind=engine)


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture
async def add_objects(get_session_fixt):
    get_session_fixt.add_all(list_models_SpimexTradingResults)
    await get_session_fixt.commit()


@pytest_asyncio.fixture
async def get_session_fixt():
    await create_tables()
    async with AsyncSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(get_session_fixt, add_objects):
    async def override_get_session():
        return get_session_fixt

    app.dependency_overrides[get_session] = override_get_session

    client = AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
    yield client
    await client.aclose()
    app.dependency_overrides.clear()

# def pytest_sessionfinish(session, exitstatus):
#     print("""
#   _____
# < Tests >
#   -----
#          \\   ^__^
#           \\  (oo)\\________   /
#              (__)\\     (  )\\/
#                 /      ```/""")
