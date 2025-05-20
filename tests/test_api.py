import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_get_last_trading_dates(client):
    with patch('src.services.cache_service.init_redis') as mock_init_redis:
        mock_redis = AsyncMock()
        mock_init_redis.return_value = mock_redis

        # Первый вызов - кеш пустой
        mock_redis.get.return_value = None

        response = await client.get("/last_trading_dates")

        print(f'\n-----Response: {response.json()}\n')

        assert response.status_code == 200
        assert len(response.json()) == 5

        # Проверяем, что get был вызван
        mock_redis.get.assert_awaited_once()
        mock_redis.get.assert_awaited_with("spimex:get_last_trading_dates:{'limit': 5}")


@pytest.mark.parametrize('limit', [1, 10, 14])
@pytest.mark.asyncio
async def test_get_last_trading_dates_with_limit(client, limit):
    with patch('src.services.cache_service.init_redis') as mock_init_redis:
        mock_redis = AsyncMock()
        mock_init_redis.return_value = mock_redis

        # Первый вызов - кеш пустой
        mock_redis.get.return_value = None

        url = f"/last_trading_dates?limit={limit}"
        response = await client.get(url)

        print(f"\n----- Limit: {limit}, Response: {response.json()}\n")

        assert response.status_code == 200
        assert len(response.json()) == limit

        # Проверяем, что get был вызван с правильным ключом
        mock_redis.get.assert_awaited_once()
        mock_redis.get.assert_awaited_with(f"spimex:get_last_trading_dates:{{'limit': {limit}}}")