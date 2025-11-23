import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from api_handler import get_gpt4_response, get_llama3_response
from config import get_config

config = get_config()
bot = Bot(token=config["tg_bot_token"])
dp = Dispatcher()

# Модель по умолчанию
current_model = "gpt4"

# Задаем контекст
CULINARY_CONTEXT = (
    "You are a professional culinary assistant and gastronomic advisor. "
    "You help users find interesting dishes and cuisines based on their tastes. "
    "Avoid unnecessary details — respond concisely and only about cooking and food. "
    "If user asks general or irrelevant question, gently guide them back to culinary topics."
    "Only use russian language to answer, do not use complicated text formatting, do not use highlighting."
)


@dp.message(CommandStart())
async def start_command(message: Message):
    await message.answer(
        "Привет! Я твой кулинарный советчик.\n\n"
        "Могу быть полезным во всех кулинарных темах, могу что-то посоветовать или даже дать фирменный рецепт!\n\n"
        "Популярные запросы:\n"
        "Посоветуй рецепт шоколадного печенья.\n"
        "«Я люблю итальянскую кухню, но пицца и паста надоели — что попробовать еще?»\n\n"
        "Также, можешь выбрать модель, с помощью которой я буду думать:\n"
        "/setmodel gpt — GPT\n"
        "/setmodel llama — LLAMA"
    )


@dp.message(Command("setmodel"))
async def set_model(message: Message):
    global current_model
    parts = message.text.split()
    if len(parts) != 2:
        return await message.answer("Выбрать модель можно так: /setmodel gpt или /setmodel llama")
    model = parts[1].lower().strip()
    if model in ["gpt", "llama"]:
        current_model = model
        await message.answer(f"Модель установлена: {current_model.upper()}")
    else:
        await message.answer("Неизвестная модель. Попробуй команды /setmodel gpt или /setmodel llama.")


@dp.message()
async def handle_user_query(message: Message):
    print(message.text)
    query = message.text.strip()
    try:
        if current_model == "llama":
            answer = await get_llama3_response(query, CULINARY_CONTEXT)
        else:
            answer = await get_gpt4_response(query, CULINARY_CONTEXT)

        if not answer:
            answer = "Не удалось получить ответ от API."

        # Длинные ответы разбиваем
        max_len = 4000
        for i in range(0, len(answer), max_len):
            await message.answer(answer[i:i + max_len])

    except Exception as e:
        await message.answer(f"Ошибка при обработке запроса: {e}")


async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
