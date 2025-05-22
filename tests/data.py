# from datetime import date
#
# from src.models.trading_results_model import SpimexTradingResults
from datetime import date

from sqlalchemy import Column, Integer, String, Numeric, Date, DateTime
from datetime import datetime
from sqlalchemy.orm import DeclarativeBase


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


list_models_SpimexTradingResults = [
    SpimexTradingResults(
        exchange_product_id="A100ABS025A",
        exchange_product_name="Бензин (АИ-100-К5), НБ Абаканская (самовывоз автотранспортом)",
        oil_id="A100",
        delivery_basis_id="ABS",
        delivery_basis_name="НБ Абаканская",
        delivery_type_id="A",
        volume=50,
        total=5000000,
        count=1,
        date=date(2024, 4, 15), ),
    SpimexTradingResults(
        exchange_product_id="A100STI060F",
        exchange_product_name="Бензин (АИ-100-К5), ст. Стенькино II (ст. отправления)",
        oil_id="A100",
        delivery_basis_id="STI",
        delivery_basis_name="ст. Стенькино II",
        delivery_type_id="F",
        volume=60,
        total=6000000,
        count=1,
        date=date(2024, 1, 14), ),
    SpimexTradingResults(
        exchange_product_id="A100ANK060F",
        exchange_product_name="Бензин (АИ-100-К5), Ангарск-группа станций (ст. отправления)",
        oil_id="A100",
        delivery_basis_id="ANK",
        delivery_basis_name="Ангарск-группа станций",
        delivery_type_id="F",
        volume=60,
        total=6246000,
        count=1,
        date=date(2024, 2, 12), ),
    SpimexTradingResults(
        exchange_product_id="A100NFT005A",
        exchange_product_name="Бензин (АИ-100-К5), НБ Ростовская (самовывоз автотранспортом)",
        oil_id="A100",
        delivery_basis_id="NFT",
        delivery_basis_name="НБ Ростовская",
        delivery_type_id="A",
        volume=10,
        total=1120000,
        count=1,
        date=date(2024, 4, 11), ),
    SpimexTradingResults(
        exchange_product_id="A100UFM060F",
        exchange_product_name="Бензин (АИ-100-К5), Уфа-группа станций (ст. отправления)",
        oil_id="A100",
        delivery_basis_id="UFM",
        delivery_basis_name="Уфа-группа станций",
        delivery_type_id="F",
        volume=60,
        total=5940000,
        count=1,
        date=date(2024, 10, 10), ),
    SpimexTradingResults(
        exchange_product_id="A100NVY060F",
        exchange_product_name="Бензин (АИ-100-К5), ст. Новоярославская (ст. отправления)",
        oil_id="A100",
        delivery_basis_id="NVY",
        delivery_basis_name="ст. Новоярославская",
        delivery_type_id="F",
        volume=60,
        total=5668200,
        count=1,
        date=date(2024, 11, 15), ),
    SpimexTradingResults(
        exchange_product_id="A100NVY060F",
        exchange_product_name="Бензин (АИ-100-К5), ст. Новоярославская (ст. отправления)",
        oil_id="A100",
        delivery_basis_id="NVY",
        delivery_basis_name="ст. Новоярославская",
        delivery_type_id="F",
        volume=60,
        total=5640000,
        count=1,
        date=date(2024, 11, 13), ),
    SpimexTradingResults(
        exchange_product_id="A100NVY060F",
        exchange_product_name="Бензин (АИ-100-К5), ст. Новоярославская (ст. отправления)",
        oil_id="A100",
        delivery_basis_id="NVY",
        delivery_basis_name="ст. Новоярославская",
        delivery_type_id="F",
        volume=180,
        total=16759140,
        count=3,
        date=date(2024, 11, 7), ),
    SpimexTradingResults(
        exchange_product_id="A100UFM060F",
        exchange_product_name="Бензин (АИ-100-К5), Уфа-группа станций (ст. отправления)",
        oil_id="A100",
        delivery_basis_id="UFM",
        delivery_basis_name="Уфа-группа станций",
        delivery_type_id="F",
        volume=60,
        total=5964660,
        count=1,
        date=date(2024, 11, 6), ),
    SpimexTradingResults(
        exchange_product_id="A100STI060F",
        exchange_product_name="Бензин (АИ-100-К5), ст. Стенькино II (ст. отправления)",
        oil_id="A100",
        delivery_basis_id="STI",
        delivery_basis_name="ст. Стенькино II",
        delivery_type_id="F",
        volume=60,
        total=6009540,
        count=1,
        date=date(2024, 9, 5), ),
    SpimexTradingResults(
        exchange_product_id="A100NVY060F",
        exchange_product_name="Бензин (АИ-100-К5), ст. Новоярославская (ст. отправления)",
        oil_id="A100",
        delivery_basis_id="NVY",
        delivery_basis_name="ст. Новоярославская",
        delivery_type_id="F",
        volume=60,
        total=5567820,
        count=1,
        date=date(2024, 11, 1), ),
    SpimexTradingResults(
        exchange_product_id="A100NVY060F",
        exchange_product_name="Бензин (АИ-100-К5), ст. Новоярославская (ст. отправления)",
        oil_id="A100",
        delivery_basis_id="NVY",
        delivery_basis_name="ст. Новоярославская",
        delivery_type_id="F",
        volume=60,
        total=5540100,
        count=1,
        date=date(2024, 10, 31), ),
    SpimexTradingResults(
        exchange_product_id="A100NVY060F",
        exchange_product_name="Бензин",
        oil_id="A100",
        delivery_basis_id="NVY",
        delivery_basis_name="Новоярославская",
        delivery_type_id="F",
        volume=120.0,
        total=11722920.0,
        count=2,
        date=date(2024, 7, 31)),
    SpimexTradingResults(
        exchange_product_id="A100NVY060F",
        exchange_product_name="Бензин (АИ-100-К5), Уфа-группа станций",
        oil_id="A100",
        delivery_basis_id="UFM",
        delivery_basis_name="Уфа-группа станций",
        delivery_type_id="F",
        volume=60,
        total=4121760,
        count=1,
        date=date(2025, 4, 28)),
    SpimexTradingResults(
        exchange_product_id="A100NVY060F",
        exchange_product_name="Бензин (АИ-100-К5), Уфа-группа станций",
        oil_id="A100",
        delivery_basis_id="UFM",
        delivery_basis_name="Уфа-группа станций",
        delivery_type_id="F",
        volume=60,
        total=4121760,
        count=1,
        date=date(2023, 3, 10))]
