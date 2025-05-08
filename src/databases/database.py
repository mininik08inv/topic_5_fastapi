from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.configs.config import Config

config = Config.load()

DATABASE_URL = f"postgresql+asyncpg://{config.db.user}:{config.db.password}@{config.db.host}:{config.db.port}/{config.db.database}"


class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL, pool_size=30, max_overflow=20, pool_recycle=3600)

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session
