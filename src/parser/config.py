from dotenv import load_dotenv
import os

# Загружаем переменные окружения из файла .env
load_dotenv()

# Получаем настройки базы данных из переменных окружения
DB_NAME = os.environ.get('DB_DATABASE')  # Название базы данных
DB_HOST = os.environ.get('DB_HOST')  # Адрес сервера БД
DB_PORT = os.environ.get('DB_PORT')  # Порт для подключения
DB_USER = os.environ.get('DB_USER')  # Имя пользователя БД
DB_PASS = os.environ.get('DB_PASSWORD')  # Пароль пользователя БД

# Год, с которого начинаем сбор данных (чтобы не парсить старые данные)
START_YEAR = 2023

