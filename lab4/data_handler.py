import os
import pandas as pd
import random
import numpy as np
from dotenv import load_dotenv

load_dotenv()


class DataHandler:
    def __init__(self):
        self.ratings = None
        self.movies = None
        self.movie_ratings_cnt = None
        self.user_ratings = None

        self.load_movielens_data()

    def load_movielens_data(self) -> None:
        """Загрузка данных MovieLens 100K"""
        data_dir = os.getenv("DATA_DIR")
        try:
            self.ratings = pd.read_csv(
                f"{data_dir}u.data",
                sep="\t",
                header=None,
                names=["user_id", "item_id", "rating", "timestamp"],
            )
            self.movies = pd.read_csv(
                f"{data_dir}u.item",
                sep="|",
                encoding="latin-1",
                header=None,
                names=[
                    "item_id",
                    "title",
                    "release_date",
                    "video_release_date",
                    "IMDb_URL",
                    "unknown",
                    "Action",
                    "Adventure",
                    "Animation",
                    "Children",
                    "Comedy",
                    "Crime",
                    "Documentary",
                    "Drama",
                    "Fantasy",
                    "Film-Noir",
                    "Horror",
                    "Musical",
                    "Mystery",
                    "Romance",
                    "Sci-Fi",
                    "Thriller",
                    "War",
                    "Western",
                ],
            )
            print(f"Загружено {len(self.ratings)} оценок")
            print(f"Фильмов в базе: {len(self.movies)}")
            self.compute_user_ratings()
            self.compute_movie_ratings_cnt()

        except FileNotFoundError:
            print("Файлы данных не найдены")
            print(
                "Скачайте MovieLens 100K и поместите файлы u.data и u.item в директорию, указанную в переменной среды DATA_DIR"
            )

    def compute_user_ratings(self) -> None:
        """Создание словаря оценок пользователей"""
        print("Вычисление оценок...")
        self.user_ratings = {}
        for _, row in self.ratings.iterrows():
            user, movie, rating = row["user_id"], row["item_id"], row["rating"]
            if user not in self.user_ratings:
                self.user_ratings[user] = {}
            self.user_ratings[user][movie] = rating

    def compute_movie_ratings_cnt(self) -> None:
        """Вычисление числа оценок для каждого фильма"""
        self.movie_ratings_cnt = {}
        for _, row in self.ratings.iterrows():
            movie = row["item_id"]
            if movie not in self.movie_ratings_cnt:
                self.movie_ratings_cnt[movie] = 0
            self.movie_ratings_cnt[movie] += 1

        for _, row in self.movies.iterrows():
            movie = row["item_id"]
            if movie not in self.movie_ratings_cnt:
                self.movie_ratings_cnt[movie] = 0

    def get_user_ratings(self) -> dict:
        """
        Получение словаря оценок

        :return dict: словарь оценок пользователей
        """
        return self.user_ratings

    def get_movie_title(self, movie_id: int) -> str:
        """
        Получение названия фильма по ID

        :param int movie_id: ID фильма
        :return str: название фильма
        """
        movie_info = self.movies[self.movies["item_id"] == movie_id]
        if len(movie_info) > 0:
            return movie_info["title"].values[0]
        return f"Фильм {movie_id}"

    def get_movie_genres(self, movie_id: int) -> list:
        """
        Получение жанров фильма

        :param int movie_id: ID фильма
        :return list: список жанров
        """
        genre_columns = [
            "Action",
            "Adventure",
            "Animation",
            "Children",
            "Comedy",
            "Crime",
            "Documentary",
            "Drama",
            "Fantasy",
            "Film-Noir",
            "Horror",
            "Musical",
            "Mystery",
            "Romance",
            "Sci-Fi",
            "Thriller",
            "War",
            "Western",
        ]
        movie_info = self.movies[self.movies["item_id"] == movie_id]
        genres = []
        for genre in genre_columns:
            if movie_info[genre].values[0] == 1:
                genres.append(genre)
        return genres

    def get_movies_data(self) -> list:
        """
        Получение данных о фильмах

        :return list: список ID всех фильмов
        """
        return self.movies["item_id"].tolist()

    def get_popular_movie(self) -> str:
        """
        Получение популярного фильма. Предпочтение отдается фильмам с наибольшим числом оценок

        :return str: популярный фильм
        """
        all_movies = []
        weights = []
        for movie, cnt in self.movie_ratings_cnt.items():
            all_movies.append(movie)
            weights.append(cnt**2 + 1)

        popular_movies = random.choices(all_movies, weights=weights, k=1)
        return popular_movies[0]