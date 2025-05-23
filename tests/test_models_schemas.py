import time
from datetime import date

import pytest

from src.schemas.trading_result_schema import TradingResult
from src.models.trading_results_model import SpimexTradingResults


@pytest.mark.schema
def test_trading_result_schema():
    data = {
        "exchange_product_id": "A100NVY060F",
        "exchange_product_name": "Бензин",
        "oil_id": "A100",
        "delivery_basis_id": "NVY",
        "delivery_basis_name": "Новоярославская",
        "delivery_type_id": "F",
        "volume": 120.0,
        "total": 11722920.0,
        "count": 2,
        "date": "2024-07-31"
    }
    result = TradingResult(**data)
    assert result.date == "2024-07-31"
    assert result.volume == 120.0


@pytest.mark.schema
def test_model_to_schema():
    time.sleep(4)
    model = SpimexTradingResults(
        exchange_product_id="A100NVY060F",
        exchange_product_name="Бензин",
        oil_id="A100",
        delivery_basis_id="NVY",
        delivery_basis_name="Новоярославская",
        delivery_type_id="F",
        volume=120.0,
        total=11722920.0,
        count=2,
        date=date(2024, 7, 31)
    )
    schema = TradingResult.model_validate(model)
    assert schema.date == "2024-07-31"
