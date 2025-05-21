from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import select, and_, desc

from src.configs.config import config
from src.models.trading_results_model import SpimexTradingResults

DATABASE_URL = config.db.DB_URL

engine = create_async_engine(DATABASE_URL, pool_size=30, max_overflow=20, pool_recycle=3600)

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_session():
    async with new_session() as session:
        yield session


async def base_query(session: AsyncSession, filters=None, order_by=None, limit=None):
    stmt = select(SpimexTradingResults)

    if filters:
        stmt = stmt.where(and_(*filters))

    if order_by is not None:
        stmt = stmt.order_by(order_by)

    if limit is not None:
        stmt = stmt.limit(limit)

    result = await session.execute(stmt)
    return result.scalars().all()
