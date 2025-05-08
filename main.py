from fastapi import FastAPI
from contextlib import asynccontextmanager
from src.api import trading_results_api
from src.services.cache_service import init_redis, daily_cache_cleanup
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация Redis
    redis = await init_redis()
    app.state.redis = redis

    # Запуск фоновой задачи для очистки кеша
    asyncio.create_task(daily_cache_cleanup(redis))
    yield
    # Закрытие соединения при завершении
    await redis.close()


app = FastAPI(lifespan=lifespan)
app.include_router(trading_results_api.router)
