import aiohttp
import pandas as pd
from typing import List, Tuple, Optional, Dict, Any
import logging
import io
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession

from models import SpimexTradingResult  # Наша модель данных
from database import AsyncSessionLocal
from parser import HEADERS, download_file
from sqlalchemy import select, and_, cast, Date
from datetime import datetime as dt

# Настраиваем логирование
logger = logging.getLogger(__name__)


def find_table_boundaries(df: pd.DataFrame, start_marker: str, end_marker: str) -> Optional[Tuple[int, int]]:
    """
    Находит границы таблицы в Excel-файле по маркерам начала и конца.

    return  Кортеж (номер_строки_начала, номер_строки_конца) или None, если не найдено
    """
    try:
        # Ищем строку с маркером начала
        start_rows = df[df.iloc[:, 0] == start_marker]
        if start_rows.empty:
            logger.warning(f"Маркер начала таблицы '{start_marker}' не найден")
            return None

        start_row = start_rows.index[0]

        # Ищем маркер конца после начала таблицы
        end_candidates = df.iloc[start_row + 3:][
            (df.iloc[start_row + 3:, 0] == end_marker) |
            (df.iloc[start_row + 3:, 0].isna())
            ]

        if end_candidates.empty:
            logger.warning(f"Маркер конца таблицы '{end_marker}' не найден после строки {start_row}")
            return None

        end_row = end_candidates.index[0]
        return start_row, end_row

    except Exception as e:
        logger.error(f"Ошибка при поиске границ таблицы: {str(e)}")
        return None


def clean_and_filter_data(df: pd.DataFrame, count_column: str) -> pd.DataFrame:
    # Преобразуем колонку с количеством в число
    df[count_column] = pd.to_numeric(df[count_column], errors='coerce')
    # Удаляем строки, где количество не указано
    df = df.dropna(subset=[count_column])
    # Оставляем только строки с количеством > 0
    df = df[df[count_column] > 0]

    # Преобразуем числовые колонки (объем, сумма)
    numeric_cols = df.columns[3:6]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce')

    return df


async def panda_filter(file_content: bytes) -> pd.DataFrame:
    """
    Обрабатывает XLS-файл и извлекает данные в DataFrame
    """

    try:
        # Читаем Excel из байтов (используем io.BytesIO)
        df = pd.read_excel(
            io.BytesIO(file_content),  # Файл в памяти
            usecols='B:F,O',  # Колонки B-F и O
            header=None,  # Нет заголовков
            dtype=str  # Все данные как строки
        )

        # Находим границы таблицы
        boundaries = find_table_boundaries(
            df,
            start_marker='Единица измерения: Метрическая тонна',
            end_marker='Итого:'
        )

        if not boundaries:
            return pd.DataFrame()

        start_row, end_row = boundaries

        # Вырезаем нужную часть таблицы
        df = df.iloc[start_row + 3:end_row].copy()
        df.reset_index(drop=True, inplace=True)

        # Название последней колонки (с количеством сделок)
        count_column = df.columns[-1]
        # Очищаем и фильтруем данные
        df = clean_and_filter_data(df, count_column)

        return df

    except Exception as e:
        logger.error(f"Ошибка в panda_filter: {str(e)}")
        return pd.DataFrame()


def parse_row(row: Tuple, date: str) -> Optional[Dict[str, Any]]:
    """Парсит одну строку данных в формат для БД."""
    try:
        exchange_product_id = str(row[1])

        # Преобразуем дату из строки в объект date
        trade_date = dt.strptime(date, '%Y-%m-%d').date() if isinstance(date, str) else date

        return {
            'exchange_product_id': exchange_product_id,
            'exchange_product_name': str(row[2]),
            'oil_id': exchange_product_id[:4],
            'delivery_basis_id': exchange_product_id[4:7],
            'delivery_basis_name': str(row[3]),
            'delivery_type_id': exchange_product_id[-1],
            'volume': float(row[4]) if pd.notna(row[4]) else 0.0,
            'total': float(row[5]) if pd.notna(row[5]) else 0.0,
            'count': int(float(row[6])) if pd.notna(row[6]) else 0,
            'date': trade_date  # Используем объект date
        }
    except Exception as e:
        logger.warning(f"Ошибка парсинга строки {row}: {str(e)}")
        return None


async def save_to_db(session: AsyncSession, data: Dict[str, Any]) -> None:
    """
    Сохраняет данные в базу (с проверкой на дубликаты)
    """
    try:
        # Преобразуем строку с датой в объект datetime.date
        if isinstance(data['date'], str):
            trade_date = dt.strptime(data['date'], '%Y-%m-%d').date()
        else:
            trade_date = data['date']

        # Проверяем, есть ли уже такая запись в БД
        result = await session.execute(
            select(SpimexTradingResult).where(
                and_(
                    SpimexTradingResult.exchange_product_id == data['exchange_product_id'],
                    SpimexTradingResult.date == trade_date  # Используем объект даты напрямую
                )
            )
        )
        existing_record = result.scalar_one_or_none()

        if existing_record:
            # Если запись существует - обновляем ее
            for key, value in data.items():
                setattr(existing_record, key, value)
        else:
            # Если записи нет - создаем новую
            data_obj = SpimexTradingResult(**data)
            session.add(data_obj)

    except Exception as e:
        logger.error(f"Ошибка при сохранении данных в БД: {str(e)}")
        raise


async def process_bulletin(session: AsyncSession, bulletin: Dict[str, Any], file_content: bytes) -> None:
    """Обрабатывает один бюллетень и передаем в функцию save_to_db для сохранения в БД."""
    try:
        # Преобразуем дату из бюллетеня в строку формата YYYY-MM-DD
        trade_date = bulletin['date'].strftime('%Y-%m-%d') if hasattr(bulletin['date'], 'strftime') else bulletin[
            'date']

        logger.info(f"Обрабатываем бюллетень за {trade_date}")

        df = await panda_filter(file_content)

        if df.empty:
            logger.info(f"Нет данных для обработки в бюллетене за {trade_date}")
            return

        for row in df.itertuples(index=True, name='Pandas'):
            data = parse_row(row, trade_date)
            if data:
                await save_to_db(session, data)

        await session.commit()
        logger.info(f"Успешно обработан бюллетень за {trade_date}")

    except Exception as e:
        await session.rollback()
        logger.error(f"Ошибка при обработке бюллетеня за {bulletin['date']}: {str(e)}")
        raise


async def process_spimex_bulletins(bulletin) -> None:
    # Создаем HTTP-сессию для загрузки файлов
    async with aiohttp.ClientSession(headers=HEADERS) as http_session:
        tasks = []

        try:
            # Загружаем файл асинхронно
            file_content = await download_file(http_session, bulletin['url'])
        except Exception as e:
            logger.error(f"Не удалось загрузить бюллетень за {bulletin['date']}: {str(e)}")
            return  # Пропускаем этот бюллетень

        async with AsyncSessionLocal() as db_session:
            if file_content:
                await process_bulletin(db_session, bulletin, file_content)
