import os
from dotenv import load_dotenv


def get_api_config():
    """
    Функция для загрузки конфигурации API из переменных окружения
    :return: Словарь с настройками API
    """
    # Загружаем переменные из .env файла
    load_dotenv()

    config = {
        # RapidAPI ключ (общий для всех API)
        "rapidapi_key": os.getenv("RAPIDAPI_KEY"),

        # Pizza API (из вашего примера)
        "pizza_url": os.getenv("PIZZA_API_URL"),
        "pizza_host": os.getenv("PIZZA_API_HOST"),

        # Wizzard API (из вашего примера)
        "wizzard_url": os.getenv("WIZZARD_API_URL"),
        "wizzard_host": os.getenv("WIZZARD_API_HOST"),

        # API Ninjas
        "ninjas_url": os.getenv("NINJAS_API_URL"),
        "ninjas_host": os.getenv("NINJAS_API_HOST"),

        # Sentiment Analysis API
        "sentiment_url": os.getenv("SENTIMENT_API_URL"),
        "sentiment_host": os.getenv("SENTIMENT_API_HOST"),
    }

    return config
