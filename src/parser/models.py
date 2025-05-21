from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime
from datetime import datetime
from database import Base


# Модель для хранения результатов торгов Spimex
class SpimexTradingResult(Base):
    # Название таблицы в базе данных
    __tablename__ = 'spimex_trading_results'

    # Колонки таблицы:
    id = Column(Integer, primary_key=True)  # Уникальный идентификатор

    # ID продукта на бирже (например, "A100NY1")
    exchange_product_id = Column(String(20), nullable=False)

    # Название продукта (например, "Бензин АИ-100")
    exchange_product_name = Column(String(255))

    # ID нефтепродукта (первые 4 символа exchange_product_id)
    oil_id = Column(String(10))

    # ID базиса поставки (символы 4-7 в exchange_product_id)
    delivery_basis_id = Column(String(10))

    # Название базиса поставки (например, "Новороссийск")
    delivery_basis_name = Column(String(255))

    # Тип поставки (последний символ в exchange_product_id)
    delivery_type_id = Column(String(1))

    # Объем торгов (в тоннах)
    volume = Column(Numeric(20, 2))

    # Сумма сделок (в рублях)
    total = Column(Numeric(20, 2))

    # Количество сделок
    count = Column(Integer)

    # Дата торгов
    date = Column(Date, nullable=False)

    # Когда запись была создана (автоматически при добавлении)
    created_on = Column(DateTime, default=datetime.now)

    # Когда запись была обновлена (автоматически при изменении)
    updated_on = Column(DateTime, default=datetime.now, onupdate=datetime.now)
