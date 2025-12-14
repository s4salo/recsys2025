import os
import pandas as pd
import random
from dotenv import load_dotenv
from cosine_similarity import cosine_similarity

load_dotenv()


class DataHandler:
    def __init__(self):
        self.ratings = None
        self.movies = None
        self.movie_ratings = None
        self.popular_movies = None
        self.movie_similarity = None

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
            self.compute_movie_ratings()

        except FileNotFoundError:
            print("Файлы данных не найдены")
            print(
                "Скачайте MovieLens 100K и поместите файлы u.data и u.item в директорию, указанную в переменной среды DATA_DIR"
            )

    def compute_movie_ratings(self) -> None:
        """Вычисление всех оценок для каждого фильма"""
        print("Вычисление оценок...")
        self.movie_ratings = {}
        for _, row in self.ratings.iterrows():
            user, movie, rating = row["user_id"], row["item_id"], row["rating"]
            if movie not in self.movie_ratings:
                self.movie_ratings[movie] = {}
            self.movie_ratings[movie][user] = rating

        for _, row in self.movies.iterrows():
            movie = row["item_id"]
            if movie not in self.movie_ratings:
                self.movie_ratings[movie] = {}

    def compute_movie_similarity(self, target_movie: int) -> None:
        """
        Вычисление косинусного сходства между заданным фильмом и всеми остальными.

        :param int target_movie: ID целевого фильма
        """
        if not self.movie_similarity:
            self.movie_similarity = {}
        if target_movie not in self.movie_similarity:
            self.movie_similarity[target_movie] = {}
        # если матрица пустая — инициализируем словари для всех фильмов
        for _, row in self.movies.iterrows():
            movie = row["item_id"]
            if movie not in self.movie_similarity:
                self.movie_similarity[movie] = {}

        for _, row in self.movies.iterrows():
            movie = row["item_id"]
            # вычисляем сходство только если ещё не посчитано
            if movie == target_movie:
                self.movie_similarity[target_movie][movie] = 1.0
                continue
            # избежать повторных вычислений
            if (
                movie in self.movie_similarity
                and target_movie in self.movie_similarity[movie]
                and self.movie_similarity[movie][target_movie] is not None
            ):
                self.movie_similarity[target_movie][movie] = self.movie_similarity[movie][
                    target_movie
                ]
                continue
            similarity = cosine_similarity(
                self.movie_ratings.get(target_movie, {}),
                self.movie_ratings.get(movie, {}),
            )
            # сохраняем симметрично
            self.movie_similarity[target_movie][movie] = similarity
            self.movie_similarity[movie][target_movie] = similarity

    def get_movie_title(self, movie_id: int) -> str:
        """Получение названия фильма по ID"""
        movie_info = self.movies[self.movies["item_id"] == movie_id]
        if len(movie_info) > 0:
            return movie_info["title"].values[0]
        return f"Фильм {movie_id}"

    def get_movie_genres(self, movie_id: int) -> list:
        """Получение жанров фильма"""
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
        if len(movie_info) == 0:
            return genres
        for genre in genre_columns:
            if movie_info[genre].values[0] == 1:
                genres.append(genre)
        return genres

    def get_movies_data(self) -> list:
        """Получение списка ID всех фильмов"""
        return self.movies["item_id"].tolist()

    def get_movie_similarity(self, movie1: int, movie2: int) -> float:
        """Получить значение косинусного сходства между двумя фильмами (если есть)"""
        if (
            self.movie_similarity
            and movie1 in self.movie_similarity
            and movie2 in self.movie_similarity[movie1]
        ):
            return self.movie_similarity[movie1][movie2]
        return 0.0

    def get_popular_movie(self) -> int:
        """
        Возвращает фильм, выбранный случайно с весами, зависящими от количества оценок.
        Чем больше оценок — тем выше шанс.
        """
        all_movies = []
        weights = []
        for movie, user_ratings in self.movie_ratings.items():
            all_movies.append(movie)
            weights.append(len(user_ratings) ** 2 + 1)

        popular_movies = random.choices(all_movies, weights=weights, k=1)
        return popular_movies[0]
