from datetime import date, timedelta
from typing import List

import pytest
from unittest.mock import AsyncMock, patch

from src.schemas.trading_result_schema import TradingResult


# Тесты эндпоинта /last_trading_dates ===============================================================
@pytest.mark.asyncio
async def test_get_last_trading_dates(client):
    '''Тест эндпоинта /last_trading_dates без передачи лимита'''
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
    '''Тест эндпоинта /last_trading_dates с лимитом'''
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


# Тесты эндпоинта get_dynamics ========================================================================
@pytest.mark.asyncio
async def test_get_dynamics_no_filters(client):
    """Тест ошибки при отсутствии фильтров"""
    response = await client.get("/dynamics")
    assert response.status_code == 400
    assert "Необходимо указать хотя бы один фильтр" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_dynamics_date_validation(client):
    """Тест валидации дат"""
    # Неправильный порядок дат
    response = await client.get("/dynamics?start_date=2023-01-02&end_date=2023-01-01")
    assert response.status_code == 400
    assert "Дата начала должна быть раньше даты окончания" in response.json()["detail"]

    # Неверный формат даты
    response = await client.get("/dynamics?start_date=invalid-date")
    assert response.status_code == 400
    assert "Неверный формат даты. Используйте YYYY-MM-DD" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_trading_results_empty_response(client):
    """Тест пустого ответа при отсутствии данных"""
    response = await client.get("/dynamics?oil_id=NOT_EXIST")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize('query', [
    "oil_id=A100",
    "delivery_type_id=F",
    "start_date=2023-01-01",
    "delivery_basis_id=UFM",
    "start_date=2023-01-01&end_date=2025-01-31",
    "end_date=2025-01-31",
])
@pytest.mark.asyncio
async def test_get_dynamics_with_filters(client, query):
    """Тест с различными комбинациями фильтров"""
    with patch('src.services.cache_service.init_redis') as mock_init_redis:
        # Создаем AsyncMock для redis
        mock_redis = AsyncMock()
        mock_init_redis.return_value = mock_redis
        mock_redis.get.return_value = None  # Имитируем пустой кеш

        response = await client.get(f"/dynamics?{query}")
        assert response.status_code == 200
        assert type(response.json()) == list

# Тесты эндпоинта /trading_results =========================================================
@pytest.mark.asyncio
async def test_get_trading_results_no_filters(client):
    """Тест ошибки при отсутствии фильтров"""
    response = await client.get("/trading_results")
    assert response.status_code == 400
    assert "Необходимо указать хотя бы один фильтр" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_trading_results_empty_response(client):
    """Тест пустого ответа при отсутствии данных"""
    response = await client.get("/trading_results?oil_id=NOT_EXIST")
    assert response.status_code == 200
    assert response.json() == []


@pytest.mark.parametrize('query,expected_count', [
    ("oil_id=A100", 10),
    ("delivery_type_id=F", 10),
    ("delivery_basis_id=UFM", 4),
    ("oil_id=A100&delivery_type_id=F", 10),
    ("oil_id=A100&delivery_basis_id=UFM", 4),
    ("delivery_type_id=F&delivery_basis_id=UFM", 4),
    ("oil_id=A100&delivery_type_id=F&delivery_basis_id=UFM", 4),
])
@pytest.mark.asyncio
async def test_get_trading_results_with_filters(client, query, expected_count):
    """Тест с различными комбинациями фильтров"""
    response = await client.get(f"/trading_results?{query}")
    assert response.status_code == 200
    results = response.json()
    assert isinstance(results, list)
    assert len(results) == expected_count
    assert type(response.json()) == list
