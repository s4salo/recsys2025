from dotenv import load_dotenv
import os


def get_config() -> dict:
    """
    Возвращает конфигурацию телеграм бота и RapidAPI
    :return: Словарь с токенами и URL
    """
    load_dotenv()

    return {
        "tg_bot_token": os.getenv("TELEGRAM_BOT_TOKEN"),
        "rapidapi_key": os.getenv("RAPIDAPI_KEY"),
        "rapidapi_host": os.getenv("RAPIDAPI_HOST"),
        "gpt4_url": os.getenv("GPT4_URL"),
        "llama3_url": os.getenv("LLAMA3_URL")
    }