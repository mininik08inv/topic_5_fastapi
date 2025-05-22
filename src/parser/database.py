from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import text

from config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER

# Формируем строку подключения к PostgreSQL
# asyncpg - это асинхронный драйвер для PostgreSQL
DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# Создаем "движок" для работы с базой данных
# echo=True включает логирование SQL-запросов (полезно для отладки)
engine = create_async_engine(DATABASE_URL, pool_size=20, pool_timeout=120, echo=False)


AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# Базовый класс для всех моделей SQLAlchemy
class Base(DeclarativeBase):
    pass


# Функция для проверки подключения к БД
async def test_connection():
    async with AsyncSessionLocal() as session:
        try:
            # Выполняем простой SQL-запрос для проверки соединения
            await session.execute(text("SELECT 1"))
            print("✅ Подключение к базе данных успешно установлено")
        except Exception as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
