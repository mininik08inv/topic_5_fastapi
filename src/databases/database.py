from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from src.configs.config import config


# DATABASE_URL = f"postgresql+asyncpg://{config.db.DB_USER}:{config.db.DB_PASSWORD}@{config.db.DB_HOST}:{config.db.DB_PORT}/{config.db.DB_DATABASE}"
DATABASE_URL = config.db.DB_URL

class Base(DeclarativeBase):
    pass


engine = create_async_engine(DATABASE_URL, pool_size=30, max_overflow=20, pool_recycle=3600)

new_session = async_sessionmaker(bind=engine, expire_on_commit=False)

async def get_session():
    async with new_session() as session:
        yield session
