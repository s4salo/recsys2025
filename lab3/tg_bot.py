import os
from telebot.async_telebot import AsyncTeleBot
from telebot.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery,
)
from dotenv import load_dotenv
from data_handler import DataHandler
from recommender import VirtualUserRecommender

load_dotenv()

bot = AsyncTeleBot(os.getenv("BOT_TOKEN"))
data_handler = DataHandler()
recommender = VirtualUserRecommender(data_handler)


def create_main_menu() -> ReplyKeyboardMarkup:
    """Создание основного меню бота"""
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    keyboard.add(
        KeyboardButton("/restart"),
        KeyboardButton("/help"),
        KeyboardButton("/my_ratings"),
        KeyboardButton("/rate_more"),
        KeyboardButton("/show_recommendations"),
    )
    return keyboard


def create_rating_keyboard(movie_id: int, iteration: int) -> InlineKeyboardMarkup:
    """
    Создание клавиатуры с оценками фильма

    :param int movie_id: ID фильма
    :param int iteration: номер итерации оценки
    """
    keyboard = InlineKeyboardMarkup(row_width=5)
    keyboard.add(
        InlineKeyboardButton("1", callback_data=f"rating_{movie_id}_{iteration}_1"),
        InlineKeyboardButton("2", callback_data=f"rating_{movie_id}_{iteration}_2"),
        InlineKeyboardButton("3", callback_data=f"rating_{movie_id}_{iteration}_3"),
        InlineKeyboardButton("4", callback_data=f"rating_{movie_id}_{iteration}_4"),
        InlineKeyboardButton("5", callback_data=f"rating_{movie_id}_{iteration}_5"),
        InlineKeyboardButton(
            "Не смотрел(а)", callback_data=f"rating_{movie_id}_{iteration}_skip"
        ),
    )
    return keyboard


def create_recommendations_keyboard() -> InlineKeyboardMarkup:
    """Создание клавиатуры с кнопкой 'Оценить еще'"""
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Оценить еще", callback_data="rate_more"))
    return keyboard


@bot.message_handler(commands=["start", "restart"])
async def handle_start(message: Message):
    """Обработчик команд /start и /restart"""
    user_id = message.from_user.id
    recommender.delete_virtual_user(user_id)
    recommender.create_virtual_user(user_id)
    await bot.send_message(
        message.chat.id,
        "Это бот для рекомендации фильмов!\n"
        "Для начала оцените несколько популярных фильмов.",
        reply_markup=create_main_menu(),
    )
    await show_movie_for_rating(message.chat.id, user_id, 0)


@bot.message_handler(commands=["rate_more"])
async def handle_rate_more(message: Message):
    """Обработчик команды /rate_more"""
    user_id = message.from_user.id
    user_ratings = recommender.get_virtual_user_ratings(user_id)
    if not user_ratings:
        await bot.send_message(
            message.chat.id,
            "У вас еще нет оценок. Используйте /start или /restart чтобы начать оценку фильмов.",
            reply_markup=create_main_menu(),
        )
        return

    await bot.send_message(message.chat.id, "Оцените несколько популярных фильмов.")
    await show_movie_for_rating(message.chat.id, user_id, 0)


@bot.message_handler(commands=["help"])
async def handle_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
Команды:
/start - запустить бота
/help - показать эту справку
/restart - перезапустить бота (сбросить оценки)
/rate_more - оценить еще фильмы (сохраняя предыдущие оценки)
/my_ratings - показать все оценки

Как использовать:
1. Оцените несколько (10) популярных фильмов
2. Получите персональные рекомендации
3. При необходимости оцените еще фильмы для улучшения рекомендаций
    """
    await bot.send_message(message.chat.id, help_text)


@bot.message_handler(commands=["my_ratings"])
async def handle_my_ratings(message: Message):
    """Обработчик команды /my_ratings"""
    user_id = message.from_user.id
    user_ratings = recommender.get_virtual_user_ratings(user_id)
    if not user_ratings:
        await bot.send_message(
            message.chat.id,
            "Вы еще не оценили ни одного фильма.\n"
            "Используйте /start чтобы начать оценку фильмов.",
            reply_markup=create_main_menu(),
        )
        return

    response = f"Ваши оценки ({len(user_ratings)} фильмов):\n"
    for movie_id, rating in user_ratings.items():
        movie_title = data_handler.get_movie_title(movie_id)
        response += f"- {movie_title}: {rating}\n"
    await bot.send_message(message.chat.id, response)


@bot.message_handler(commands=["show_recommendations"])
async def handle_start(message: Message):
    """Обработчик команды /show_recommendations"""
    await show_recommendations(message.chat.id, message.from_user.id)


async def show_movie_for_rating(chat_id: int, user_id: int, iteration: int) -> None:
    """
    Отправка сообщения с оценкой фильма

    :param int chat_id: ID чата
    :param int user_id: ID пользователя
    :param int iteration: номер итерации оценки
    """
    if iteration == 5:
        await bot.send_message(
            chat_id,
            "Формирую персональные рекомендации...",
            reply_markup=create_main_menu(),
        )
        await show_recommendations(chat_id, user_id)
        return

    user_ratings = recommender.get_virtual_user_ratings(user_id)
    rated_movies = set(user_ratings.keys())
    movie_to_rate = None
    while not movie_to_rate:
        popular_movie = data_handler.get_popular_movie()
        movie_to_rate = popular_movie if popular_movie not in rated_movies else None

    movie_title = data_handler.get_movie_title(movie_to_rate)
    genres = data_handler.get_movie_genres(movie_to_rate)
    genres_str = ", ".join(genres) if genres else "Не указаны"
    message = f"Фильм {movie_title}\n"
    message += f"Жанр: {genres_str}\n"
    message += "Как вы оцените этот фильм?"
    keyboard = create_rating_keyboard(movie_to_rate, iteration)
    await bot.send_message(chat_id, message, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.startswith("rating_"))
async def handle_rating_callback(call: CallbackQuery):
    """Обработчик нажатий на кнопки с оценками"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    parts = call.data.split("_")
    movie_id = int(parts[1])
    iteration = int(parts[2])
    rating_action = parts[3]

    if rating_action != "skip":
        rating = int(rating_action)
        recommender.update_virtual_user(user_id, movie_id, rating)
        # пересчитываем сходства для данного фильма относительно всех
        data_handler.compute_movie_similarity(movie_id)
    await bot.answer_callback_query(call.id)
    await show_movie_for_rating(chat_id, user_id, iteration + 1)


@bot.callback_query_handler(func=lambda call: call.data == "rate_more")
async def handle_rate_more_callback(call: CallbackQuery):
    """Обработчик кнопки 'Оценить еще'"""
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    await bot.answer_callback_query(call.id)
    await show_movie_for_rating(chat_id, user_id, 0)


async def show_recommendations(chat_id: int, user_id: int) -> None:
    """
    Показ рекомендаций пользователю

    :param int chat_id: ID чата
    :param int user_id: ID пользователя
    """
    recommendations = recommender.recommend_for_virtual_user(user_id, n=5)
    if not recommendations:
        await bot.send_message(
            chat_id,
            "К сожалению, не удалось найти рекомендации на основе ваших оценок.\n"
            "Попробуйте оценить больше фильмов.",
            reply_markup=create_main_menu(),
        )
        return

    response = f"Персональные рекомендации для вас:\n\n"
    for i, (movie_id, pred_rating, _) in enumerate(recommendations, 1):
        movie_title = data_handler.get_movie_title(movie_id)
        movie_genres = data_handler.get_movie_genres(movie_id)
        genres_str = ", ".join(movie_genres) if movie_genres else "Не указаны"
        response += f"{i}. {movie_title}\n"
        response += f"   Предсказанная оценка: {pred_rating:.2f}\n"
        response += f"   Жанр: {genres_str}\n\n"
    response += "---\n"
    response += "Для улучшения рекомендаций оцените еще несколько фильмов."
    keyboard = create_recommendations_keyboard()
    await bot.send_message(chat_id, response, reply_markup=keyboard)


@bot.message_handler(func=lambda message: True)
async def handle_other_messages(message: Message):
    """Обработчик других сообщений"""
    await bot.send_message(
        message.chat.id,
        "Я не понимаю эту команду. Используйте /help для просмотра доступных команд.",
        reply_markup=create_main_menu(),
    )


async def start_bot():
    data_handler.load_movielens_data()
    print("Бот запущен")
    await bot.polling()
