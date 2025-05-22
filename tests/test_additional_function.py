from datetime import date
from fastapi import HTTPException
import pytest

from src.api.trading_results_api import validate_date


@pytest.mark.parametrize("date_str, expected", [
    ("2023-01-01", date(2023, 1, 1)),
    (None, None),
    ("", None),
])
def test_validate_date_success(date_str, expected):
    """Тест успешной валидации даты"""
    result = validate_date(date_str)
    assert result == expected


@pytest.mark.parametrize("invalid_date", [
    "2023-13-01",  # Несуществующий месяц
    "2023-01-32",  # Несуществующий день
    "not-a-date",  # Совсем не дата
    "2023/01/01",  # Неправильный разделитель
])
def test_validate_date_failure(invalid_date):
    """Тест ошибки валидации при неверном формате даты"""
    with pytest.raises(HTTPException) as exc_info:
        validate_date(invalid_date)

    assert exc_info.value.status_code == 400
    assert "Неверный формат даты. Используйте YYYY-MM-DD" in exc_info.value.detail