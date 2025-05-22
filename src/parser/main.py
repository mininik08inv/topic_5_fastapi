import asyncio
import time
import logging
from asyncio import Semaphore
from datetime import datetime

# Импортируем наши функции
from parser import get_all_bulletin_links
from save_to_database import process_spimex_bulletins

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)
DB_CONCURRENCY_LIMIT = 10
db_semaphore = Semaphore(DB_CONCURRENCY_LIMIT)


async def async_main():
    """Основная асинхронная функция приложения"""
    start_time = time.time()  # Засекаем время начала

    logger.info("🟢 Запускаем парсер Spimex")

    # 1. Получаем список всех бюллетеней
    logger.info("🔍 Ищем бюллетени на сайте Spimex...")
    bulletin_list = await get_all_bulletin_links()
    logger.info(f"Найдено {len(bulletin_list)} бюллетеней для обработки")

    # 2. Обрабатываем бюллетени и сохраняем в БД
    logger.info("Начинаем обработку бюллетеней...")
    async with db_semaphore:  # Ожидает, если уже есть 10 активных задач
        try:
            # Создаем список задач на обработку каждого бюллетеня
            tasks = [process_spimex_bulletins(bulletin) for bulletin in bulletin_list]
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Ошибка при обработке бюллетеня: {e}")
            raise

    # Выводим время выполнения
    duration = time.time() - start_time
    logger.info(f"✅ Парсер успешно завершил работу за {duration:.2f} секунд")



if __name__ == "__main__":
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("🛑 Приложение остановлено пользователем")
    except Exception as e:
        logger.error(f"💥 Необработанная ошибка: {e}")