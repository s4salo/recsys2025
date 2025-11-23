from typing import Any

import aiohttp
from config import get_config

config = get_config()


async def query_llm_api(url: str, payload: dict) -> Any | None:
    """
    Асинхронный POST-запрос к RapidAPI LLM.
    """
    headers = {
        "x-rapidapi-key": config["rapidapi_key"],
        "x-rapidapi-host": config["rapidapi_host"],
        "Content-Type": "application/json"
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload,timeout=aiohttp.ClientTimeout(total=120)) as resp:
                resp.raise_for_status()
                return await resp.json()
    except Exception as e:
        print(f"[API ERROR] {e}")
        return None


async def get_gpt4_response(user_query: str, context: str = "") -> str:
    """
    GPT-4 API через RapidAPI
    """
    payload = {
        "messages": [
            {"role": "system", "content": context},
            {"role": "user", "content": user_query}
        ],
        "web_access": False
    }

    response = await query_llm_api(config["gpt4_url"], payload)
    if response and "result" in response:
        return response["result"]
    return "Не удалось получить ответ от GPT-4 API."


async def get_llama3_response(user_query: str, context: str = "") -> str:
    """
    LLaMA3 API через RapidAPI
    """
    payload = {
        "messages": [
            {"role": "system", "content": context},
            {"role": "user", "content": user_query}
        ],
        "web_access": False
    }

    response = await query_llm_api(config["llama3_url"], payload)
    print(response["result"])
    if response and "result" in response:
        return response["result"]
    return "Не удалось получить ответ от LLaMA3 API."
