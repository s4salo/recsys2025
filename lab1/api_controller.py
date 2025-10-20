import requests
import json
from data_handler import get_api_config

# Получаем конфигурацию API
config = get_api_config()


def make_api_request_get(url: str, headers: dict, params: dict = None) -> dict:
    """
    Функция для выполнения GET запроса к API и возврата ответа в формате JSON
    :url: Эндпойнт
    :headers: Заголовки запроса
    :params: Параметры запроса
    :return: Словарь с ответом
    """
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP-ошибка: {err}")
        return None


def make_api_request_post(url: str, headers: dict, payload: dict = None) -> dict:
    """
    Функция для выполнения POST-запроса к API и возврата JSON-ответа
    :url: Эндпойнт
    :headers: Заголовки запроса
    :payload: Данные для запроса
    :return: Словарь с ответом
    """
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP-ошибка: {err}")
        return None


def analyze_ninjas_api(text: str) -> dict:
    """
    Функция для анализа отзыва через API Ninjas Sentiment API.
    :text: Текст отзыва
    :return: Словарь с результатами
    """
    headers = {
        "X-RapidAPI-Key": config["rapidapi_key"],
        "X-RapidAPI-Host": config["ninjas_host"],
    }

    params = {"text": text}
    result = make_api_request_get(config["ninjas_url"], headers, params)

    if result:
        return {
            'success': True,
            'data': result,
            'api_name': 'API Ninjas'
        }
    else:
        return {
            'success': False,
            'error': 'API request failed',
            'api_name': 'API Ninjas'
        }


def analyze_sentiment_analysis_api(text: str) -> dict:
    """
    Функция для анализа отзыва через Sentiment Analysis API.
    :text: Текст отзыва
    :return: Словарь с результатами
    """
    headers = {
        "X-RapidAPI-Key": config["rapidapi_key"],
        "X-RapidAPI-Host": config["sentiment_host"],
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    payload = [{
        "id": "1",
        "language": "en",
        "text": text
    }]

    result = make_api_request_post(config["sentiment_url"], headers, payload)

    if result:
        return {
            'success': True,
            'data': result,
            'api_name': 'Sentiment Analysis'
        }
    else:
        return {
            'success': False,
            'error': 'Ошибка запроса к API',
            'api_name': 'Sentiment Analysis'
        }