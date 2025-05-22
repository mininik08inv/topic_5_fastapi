from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


# Модель для хранения результатов торгов Spimex
class SpimexTradingResults(Base):
    # Название таблицы в базе данных
    __tablename__ = 'spimex_trading_results'

    id = Column(Integer, primary_key=True)  # Уникальный идентификатор
    exchange_product_id = Column(String(20), nullable=False)  # ID продукта на бирже (например, "A100NY1")
    exchange_product_name = Column(String(255))  # Название продукта (например, "Бензин АИ-100")
    oil_id = Column(String(10))  # ID нефтепродукта (первые 4 символа exchange_product_id)
    delivery_basis_id = Column(String(10))  # ID базиса поставки (символы 4-7 в exchange_product_id)
    delivery_basis_name = Column(String(255))  # Название базиса поставки (например, "Новороссийск")
    delivery_type_id = Column(String(1))  # Тип поставки (последний символ в exchange_product_id)
    volume = Column(Numeric(20, 2))  # Объем торгов (в тоннах)
    total = Column(Numeric(20, 2))  # Сумма сделок (в рублях)
    count = Column(Integer)  # Количество сделок
    date = Column(Date, nullable=False)  # Дата торгов
    created_on = Column(DateTime, default=datetime.now)  # Когда запись была создана (автоматически при добавлении)
    updated_on = Column(DateTime, default=datetime.now,
                        onupdate=datetime.now)  # Когда запись была обновлена (автоматически при изменении)
