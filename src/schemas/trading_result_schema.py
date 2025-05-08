from datetime import date
from pydantic import BaseModel, field_validator
from typing import Any
import json

class TradingResult(BaseModel):
    exchange_product_id: str
    exchange_product_name: str
    oil_id: str
    delivery_basis_id: str
    delivery_basis_name: str
    delivery_type_id: str
    volume: float
    total: float
    count: int
    date: str

    class Config:
        from_attributes = True
        json_encoders = {
            date: lambda v: v.isoformat(),
            float: lambda v: round(v, 2)  # Округляем float до 2 знаков
        }

    @field_validator('date', mode='before')
    def parse_date(cls, value):
        if isinstance(value, date):
            return value.isoformat()
        return value

    def json_serializable(self) -> dict[str, Any]:
        return json.loads(self.model_dump_json())