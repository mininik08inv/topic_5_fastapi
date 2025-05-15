import math
from datetime import time, datetime, timedelta
from redis.asyncio import Redis
import asyncio
import json
import logging
from functools import wraps
from fastapi import Request
from typing import Any, TypeVar, Type, Optional, Callable
from pydantic import BaseModel

from src.configs.config import config

T = TypeVar('T', bound=BaseModel)


logger = logging.getLogger(__name__)
logging.basicConfig(level=config.log.loging_default_lavel)

# Конфигурация кеширования
CACHE_RESET_TIME = time(14, 11)  # Время сброса кеша (14:11)
REDIS_URL = config.redis.REDIS_URL


async def init_redis() -> Redis:
    """Инициализация подключения к Redis"""
    return Redis.from_url(REDIS_URL, decode_responses=True)

def get_seconds_until_tomorrow_1411():
    now = datetime.now()
    tomorrow = now.date() + timedelta(days=1)
    target_time = datetime.combine(tomorrow, datetime.strptime(
        config.redis.CACHE_RESET_TIME,
        "%H:%M").time()
                                   )
    delta = target_time - now
    return math.ceil(delta.total_seconds())


# async def daily_cache_cleanup(redis: Redis):
#     """Фоновая задача для ежедневной очистки кеша"""
#     while True:
#         now = datetime.now()
#         next_reset = datetime.combine(now.date(), CACHE_RESET_TIME)
#
#         if now.time() >= CACHE_RESET_TIME:
#             next_reset += timedelta(days=1)
#
#         sleep_seconds = (next_reset - now).total_seconds()
#         logger.debug(f"Следующая очистка кеша в {next_reset} (через {sleep_seconds:.0f} секунд)")
#
#         await asyncio.sleep(sleep_seconds)
#
#         keys = await redis.keys("spimex:*")
#         if keys:
#             await redis.delete(*keys)
#             logger.info(f"Очищено {len(keys)} ключей кеша")


class CacheService:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self, key: str, model: Type[T] = None) -> Any:
        cached = await self.redis.get(key)
        if not cached:
            logger.debug('Нет такого ключа')
            return None

        try:
            data = json.loads(cached)
            if model and issubclass(model, BaseModel):
                if isinstance(data, list):
                    return [model.model_validate(item) for item in data]
                return model.model_validate(data)
            logger.debug('Кеш найден, отдаем кеш')
            return data
        except json.JSONDecodeError:
            return None

    async def set(self, key: str, data: Any, expire: int = None):
        if isinstance(data, BaseModel):
            to_cache = data.json_serializable()
        elif isinstance(data, list) and len(data) > 0 and isinstance(data[0], BaseModel):
            to_cache = [item.json_serializable() for item in data]
        else:
            to_cache = data
        logger.debug('Устанавливаем кеш')
        await self.redis.set(key, json.dumps(to_cache), ex=expire)


def cache_response(
        key_prefix: str = "spimex",
        expire: int = get_seconds_until_tomorrow_1411(),
        model: Optional[Callable] = None
):
    def decorator(func):
        @wraps(func)
        async def wrapper(request: Request, *args, **kwargs):
            cache = CacheService(request.app.state.redis)
            new_kwargs = {k: v for k, v in kwargs.items() if k != 'session'}  # Убираем сессию из ключа
            cache_key = f"{key_prefix}:{func.__name__}:{str(new_kwargs)}"

            # Получаем модель из аннотаций, если не указана явно
            response_model = model or func.__annotations__.get('return')

            if cached := await cache.get(cache_key, model=response_model):
                return cached

            result = await func(request, *args, **kwargs)
            await cache.set(cache_key, result, expire)
            return result

        return wrapper

    return decorator