from datetime import date, timedelta
from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from src.databases.database import get_session, base_query
from src.models.trading_results_model import SpimexTradingResults
from src.schemas.trading_result_schema import TradingResult
from src.services.cache_service import cache_response, get_seconds_until_tomorrow_1411

router = APIRouter()


@router.get("/last_trading_dates", response_model=List[date])
@cache_response(key_prefix="spimex", expire=get_seconds_until_tomorrow_1411())
async def get_last_trading_dates(
        request: Request,
        session: Annotated[AsyncSession, Depends(get_session)],
        limit: int = Query(
            default=5,
            ge=1,
            le=1000,  # Добавляем верхний лимит для защиты
            description="Количество последних торговых дней (1-1000)"
        )
):
    stmt = (
        select(SpimexTradingResults.date)
        .distinct()
        .order_by(SpimexTradingResults.date.desc())
        .limit(limit)
    )
    results = await session.scalars(stmt)

    dates = [str(row) for row in results]
    return dates

def validate_date(date_str: Optional[str]) -> Optional[date]:
    if not date_str:
        return None
    try:
        return date.fromisoformat(str(date_str))
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=400,
            detail="Неверный формат даты. Используйте YYYY-MM-DD"
        )


@router.get("/dynamics", response_model=List[TradingResult])
@cache_response(key_prefix="spimex", expire=get_seconds_until_tomorrow_1411())
async def get_dynamics(
        request: Request,
        session: Annotated[AsyncSession, Depends(get_session)],
        oil_id: Optional[str] = Query(None),
        delivery_type_id: Optional[str] = Query(None),
        delivery_basis_id: Optional[str] = Query(None),
        start_date: Optional[str] = Query(None),  # Изменено на str для валидации
        end_date: Optional[str] = Query(None)     # Изменено на str для валидации
) -> List[TradingResult]:
    # Проверка, что указан хотя бы один фильтр
    if not any([oil_id, delivery_type_id, delivery_basis_id, start_date, end_date]):
        raise HTTPException(
            status_code=400,
            detail="Необходимо указать хотя бы один фильтр (oil_id, delivery_type_id, delivery_basis_id или даты)"
        )

    # Валидация дат
    start_date_obj = validate_date(start_date) if start_date else None
    end_date_obj = validate_date(end_date) if end_date else None

    # Установка дефолтных дат если нужно
    if start_date_obj and not end_date_obj:
        end_date_obj = date.today()
    elif end_date_obj and not start_date_obj:
        start_date_obj = end_date_obj - timedelta(days=365)

    # Проверка что start_date <= end_date
    if start_date_obj and end_date_obj and start_date_obj > end_date_obj:
        raise HTTPException(
            status_code=400,
            detail="Дата начала должна быть раньше даты окончания"
        )

    # Сбор фильтров
    filters = []
    if start_date_obj:
        filters.append(SpimexTradingResults.date >= start_date_obj)
    if end_date_obj:
        filters.append(SpimexTradingResults.date <= end_date_obj)
    if oil_id:
        filters.append(SpimexTradingResults.oil_id == oil_id)
    if delivery_type_id:
        filters.append(SpimexTradingResults.delivery_type_id == delivery_type_id)
    if delivery_basis_id:
        filters.append(SpimexTradingResults.delivery_basis_id == delivery_basis_id)

    results = await base_query(
        session,
        filters=filters if filters else None,
        order_by=desc(SpimexTradingResults.date)
    )
    if len(results) > 0:
        return [TradingResult.model_validate(row) for row in results]
    else:
        raise HTTPException(
            status_code=200,
            detail="Данных по вашим фильтрам не нашлось!"
        )


@router.get("/trading_results", response_model=List[TradingResult])
@cache_response(key_prefix="spimex", expire=get_seconds_until_tomorrow_1411())
async def get_trading_results(
        request: Request,
        session: Annotated[AsyncSession, Depends(get_session)],
        oil_id: Optional[str] = Query(None),
        delivery_type_id: Optional[str] = Query(None),
        delivery_basis_id: Optional[str] = Query(None),
        limit: int = Query(default=10, ge=1)
) -> List[TradingResult]:
    # Проверка, что указан хотя бы один фильтр
    if not any([oil_id, delivery_type_id, delivery_basis_id]):
        raise HTTPException(
            status_code=400,
            detail="Необходимо указать хотя бы один фильтр (oil_id, delivery_type_id, delivery_basis_id)"
        )

    filters = []
    if oil_id:
        filters.append(SpimexTradingResults.oil_id == oil_id)
    if delivery_type_id:
        filters.append(SpimexTradingResults.delivery_type_id == delivery_type_id)
    if delivery_basis_id:
        filters.append(SpimexTradingResults.delivery_basis_id == delivery_basis_id)

    results = await base_query(
        session,
        filters=filters if filters else None,
        order_by=desc(SpimexTradingResults.date),
        limit=limit
    )

    return [TradingResult.model_validate(row) for row in results]
