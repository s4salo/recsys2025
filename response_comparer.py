from typing import Dict, Optional


def normalize_sentiment_result(api_result: dict, api_name: str) -> Optional[str]:
    """
    Извлекает тональность и нормализует к единому формату
    :api_result: Результат работы API
    :api_name: Название API ('API Ninjas' или 'Sentiment Analysis')
    :return: Нормализованная тональность ('positive', 'negative', 'neutral') или None в случае ошибки
    """
    if not api_result or not api_result.get('success'):
        return None

    try:
        if api_name == 'API Ninjas':
            # API Ninjas возвращает: {"score": 0.123, "text": переданный текст, "sentiment": "POSITIVE"}
            label = api_result['data'].get('sentiment', '').lower()
            return label

        elif api_name == 'Sentiment Analysis':
            # Sentiment Analysis возвращает массив с результатами
            data = api_result['data']
            if isinstance(data, list) and len(data) > 0:
                result = data[0]
                predictions = result.get('predictions', [])
                if predictions:
                    # Находим предсказание с максимальной вероятностью
                    best_prediction = max(predictions, key=lambda x: x.get('probability', 0))
                    sentiment = best_prediction.get('prediction', '').lower()
                    return sentiment

        return None

    except (KeyError, TypeError, IndexError):
        return None


def compare_api_results(ninjas_result: dict, sentiment_result: dict) -> dict:
    """
    Сравнивает результаты двух API и определяет, совпадают ли они
    :ninjas_result: Результат API Ninjas
    :sentiment_result: Результат Sentiment Analysis API
    :return: Словарь с результатами сравнения
    """
    # Нормализуем результаты
    ninjas_sentiment = normalize_sentiment_result(ninjas_result, 'API Ninjas')
    sentiment_analysis_sentiment = normalize_sentiment_result(sentiment_result, 'Sentiment Analysis')

    # Проверяем, получены ли результаты от обеих API
    both_successful = ninjas_sentiment is not None and sentiment_analysis_sentiment is not None

    # Сравниваем результаты
    results_match = False
    if both_successful:
        results_match = ninjas_sentiment == sentiment_analysis_sentiment

    return {
        'ninjas_sentiment': ninjas_sentiment,
        'sentiment_analysis_sentiment': sentiment_analysis_sentiment,
        'both_api_successful': both_successful,
        'results_match': results_match,
        'comparison_status': get_comparison_status(ninjas_sentiment, sentiment_analysis_sentiment)
    }


def get_comparison_status(sentiment1: Optional[str], sentiment2: Optional[str]) -> str:
    """
    Определяет статус сравнения результатов
    :sentiment1: Результат первого API
    :sentiment2: Результат второго API
    :return: Статус сравнения
    """
    if sentiment1 is None and sentiment2 is None:
        return "both_failed"
    elif sentiment1 is None:
        return "ninjas_failed"
    elif sentiment2 is None:
        return "sentiment_analysis_failed"
    elif sentiment1 == sentiment2:
        return "match"
    else:
        return "mismatch"