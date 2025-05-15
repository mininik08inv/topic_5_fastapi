from typing import Callable, Awaitable

import uvicorn
from fastapi import FastAPI, Request, Response
from contextlib import asynccontextmanager
from src.api import trading_results_api
from src.services.cache_service import init_redis, daily_cache_cleanup
import asyncio

import logging

log = logging.getLogger()


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


# @app.middleware("http")
# async def log_new_request(request: Request, call_next: Callable[[Request], Awaitable[Request]]) -> Response:
#     log.info("Request %s to %s", request.method, request.url)
#     return await call_next(request)


if __name__ == '__main__':
    uvicorn.run("main:app")
