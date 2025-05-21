import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
from config import START_YEAR
import asyncio
import logging

BASE_URL = 'https://spimex.com'
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

logger = logging.getLogger(__name__)


async def fetch_html(session: aiohttp.ClientSession, url: str) -> str:
    """загружает HTML-страницу"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=20)) as response:
            response.raise_for_status()
            return await response.text()

    except aiohttp.ClientError as e:
        logger.error(f"Ошибка при загрузке {url}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при загрузке {url}: {str(e)}")
        raise


async def download_file(session: aiohttp.ClientSession, url: str) -> bytes:
    """Асинхронно загружает файл (XLS)"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
            response.raise_for_status()
            return await response.read()
    except aiohttp.ClientError as e:
        logger.error(f"Ошибка при загрузке файла {url}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Неожиданная ошибка при загрузке файла {url}: {str(e)}")
        raise


async def process_item(item):
    try:
        date_span = item.find('span')
        if not date_span:
            return None

        date_str = date_span.text.strip()
        trade_date = datetime.strptime(date_str, '%d.%m.%Y').date()

        if trade_date.year < START_YEAR:
            logger.info(f"Достигнуты бюллетени за {trade_date.year} год, завершаем сбор")
            return None

        link_tag = item.find('a', href=True)
        if not link_tag:
            return None

        full_link = urljoin(BASE_URL, link_tag['href'])
        return {'date': trade_date, 'url': full_link}

    except Exception as e:
        logger.error(f"Ошибка обработки элемента: {str(e)}")
        return None


async def parse_bulletin_page(session: aiohttp.ClientSession, page_num: int) -> tuple:
    """Парсит страницу с бюллетенями"""
    try:
        url = f'{BASE_URL}/markets/oil_products/trades/results/' if page_num == 1 else \
              f'{BASE_URL}/markets/oil_products/trades/results/?page=page-{page_num}'

        logger.info(f"Processing page {page_num}: {url}")
        html = await fetch_html(session, url)

        soup = BeautifulSoup(html, 'lxml')  # или html.parser

        accordeon = soup.find('div', class_='accordeon-inner__wrap') or \
                   soup.find('div', class_='accordeon-inner') or \
                   soup.find('div', class_='accordeon')

        if not accordeon:
            logger.warning("Не найден контейнер с бюллетенями")
            return [], True

        items = accordeon.find_all('div', class_=lambda x: x and 'accordeon-inner__item' in x) if accordeon else []

        if not items:
            logger.info("Пробуем альтернативный поиск элементов...")
            items = soup.find_all('div', class_=lambda x: x and 'item' in x and 'xls' in x)

        # Параллельная обработка элементов
        tasks = [process_item(item) for item in items]
        results = await asyncio.gather(*tasks)

        # Фильтрация None (ошибки или пропуски)
        bulletins = [bulletin for bulletin in results if bulletin]

        next_page = soup.find('li', class_='bx-pag-next')
        has_next = bool(next_page and 'disabled' not in next_page.get('class', []))

        return bulletins, not has_next

    except Exception as e:
        logger.error(f"Ошибка при парсинге страницы {page_num}: {str(e)}")
        return [], False


async def get_all_bulletin_links() -> list:
    """Получает все ссылки на бюллетени"""
    all_links = []
    page_num = 1
    stop_flag = False

    async with aiohttp.ClientSession(headers=HEADERS) as session:
        while not stop_flag:
            try:
                bulletins, should_stop = await parse_bulletin_page(session, page_num)
                all_links.extend(bulletins)

                if should_stop or not bulletins:
                    stop_flag = True
                else:
                    page_num += 1

            except Exception as e:
                logger.error(f"Ошибка обработки страницы {page_num}: {str(e)}")
                stop_flag = True

    all_links.sort(key=lambda x: x['date'], reverse=True)
    logger.info(f"Всего найдено бюллетеней: {len(all_links)}")
    return all_links