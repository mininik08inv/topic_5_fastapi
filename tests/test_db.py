from datetime import date
from fastapi import HTTPException
import pytest
from sqlalchemy import desc

from src.databases.database import base_query
from src.models.trading_results_model import SpimexTradingResults
from tests.data import list_models_SpimexTradingResults


@pytest.mark.asyncio
async def test_base_query_no_filters(get_session_fixt, add_objects):
    """Тест base_query без фильтров"""
    results = await base_query(
        session=get_session_fixt,
        order_by=desc(SpimexTradingResults.date)
    )

    # Проверяем, что получили все записи
    assert len(results) == len(list_models_SpimexTradingResults)


@pytest.mark.asyncio
async def test_base_query_empty_result(get_session_fixt, add_objects):
    """Тест base_query с фильтром, который не даёт результатов"""
    filters = [SpimexTradingResults.oil_id == "NOT_EXIST"]

    results = await base_query(
        session=get_session_fixt,
        filters=filters
    )

    assert len(results) == 0


@pytest.mark.asyncio
async def test_base_query_with_oil_id_filter(get_session_fixt, add_objects):
    """Тест base_query с фильтром по oil_id"""
    oil_id = "A100"
    filters = [SpimexTradingResults.oil_id == oil_id]

    results = await base_query(
        session=get_session_fixt,
        filters=filters,
        order_by=desc(SpimexTradingResults.date)
    )

    # Проверяем, что все результаты соответствуют фильтру
    assert all(r.oil_id == oil_id for r in results)
    assert len(results) == 15