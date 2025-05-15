from datetime import date, timedelta
from typing import Annotated, Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc

from src.databases.database import get_session
from src.models.trading_results_model import SpimexTradingResults
from src.schemas.trading_result_schema import TradingResult
from src.services.cache_service import cache_response, get_seconds_until_tomorrow_1411

router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_session)]


async def base_query(session: AsyncSession, filters=None, order_by=None, limit=None):
    stmt = select(SpimexTradingResults)

    if filters:
        stmt = stmt.where(and_(*filters))

    if order_by is not None:
        stmt = stmt.order_by(order_by)

    if limit is not None:
        stmt = stmt.limit(limit)

    result = await session.execute(stmt)
    return result.scalars().all()


@router.get("/last_trading_dates", response_model=List[str])
@cache_response(key_prefix="spimex", expire=get_seconds_until_tomorrow_1411())
async def get_last_trading_dates(
        request: Request,
        session: SessionDep,
        limit: int = Query(default=5, ge=1, description="Количество последних торговых дней")
) -> list[str]:
    results = await base_query(
        session,
        order_by=desc(SpimexTradingResults.date),
        limit=limit
    )
    dates = [str(row.date) for row in results]
    return dates


@router.get("/dynamics", response_model=List[TradingResult])
@cache_response(key_prefix="spimex", expire=get_seconds_until_tomorrow_1411())
async def get_dynamics(
        request: Request,
        session: SessionDep,
        oil_id: Optional[str] = Query(None),
        delivery_type_id: Optional[str] = Query(None),
        delivery_basis_id: Optional[str] = Query(None),
        start_date: Optional[date] = Query(None),
        end_date: Optional[date] = Query(None)
) -> List[TradingResult]:
    # Проверка, что указан хотя бы один фильтр
    if not any([oil_id, delivery_type_id, delivery_basis_id, start_date, end_date]):
        raise HTTPException(
            status_code=400,
            detail="Необходимо указать хотя бы один фильтр (oil_id, delivery_type_id, delivery_basis_id или даты)"
        )

    # Проверка дат
    if start_date and not end_date:
        end_date = date.today()
    elif end_date and not start_date:
        start_date = end_date - timedelta(days=365)

    if start_date and end_date and start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Дата начала должна быть раньше даты окончания"
        )

    filters = []
    if start_date:
        try:
            start_date_obj = date.fromisoformat(str(start_date))
            filters.append(SpimexTradingResults.date >= start_date_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Не верный формат даты. Используйте YYYY-MM-DD")

    if end_date:
        try:
            end_date_obj = date.fromisoformat(str(end_date))
            filters.append(SpimexTradingResults.date <= end_date_obj)
        except ValueError:
            raise HTTPException(status_code=400, detail="Не верный формат даты. Используйте YYYY-MM-DD")

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

    return [TradingResult.model_validate(row) for row in results]


@router.get("/trading_results", response_model=List[TradingResult])
@cache_response(key_prefix="spimex", expire=get_seconds_until_tomorrow_1411())
async def get_trading_results(
        request: Request,
        session: SessionDep,
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
