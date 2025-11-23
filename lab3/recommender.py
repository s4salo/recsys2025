from data_handler import DataHandler


class VirtualUserRecommender:
    def __init__(self, data_handler: DataHandler):
        self.dh = data_handler
        self.virtual_users = {}

    def create_virtual_user(self, user_id: int) -> None:
        """
        Создание виртуального пользователя

        :param int user_id: ID пользователя
        """
        self.virtual_users[user_id] = {}
        print(f"Создан виртуальный пользователь {user_id}")

    def update_virtual_user(self, user_id: int, movie_id: int, rating: int) -> None:
        """
        Добавление оценки фильма для виртуального пользователя

        :param int user_id: ID пользователя
        :param int movie_id: ID фильма
        :param int rating: оценка фильма
        """
        if user_id not in self.virtual_users:
            self.create_virtual_user(user_id)
        self.virtual_users[user_id][movie_id] = rating
        movie_title = self.dh.get_movie_title(movie_id)

        print(
            f"Добавлена оценка {rating} фильма '{movie_title}' (ID: {movie_id}) для виртуального пользователя {user_id}"
        )

    def delete_virtual_user(self, user_id: int) -> None:
        """
        Удаление оценок виртуального пользователя

        :param int user_id: ID пользователя
        """
        if user_id in self.virtual_users.keys():
            del self.virtual_users[user_id]
            print(f"Удален виртуальный пользователь {user_id}")

    def predict_rating(self, user_id: int, movie_id: int) -> tuple[float, float]:
        """
        Предсказание оценки для виртуального пользователя и фильма

        :param int user_id: ID пользователя
        :param int movie_id: ID фильма
        :return tuple[float, float]: предсказанная оценка и сумма схожестей
        """
        user_ratings = self.virtual_users.get(user_id, {})
        if movie_id in user_ratings.keys():
            return user_ratings[movie_id], 0

        similarities = []
        for rated_movie, rating in user_ratings.items():
            sim = self.dh.get_movie_similarity(rated_movie, movie_id)
            if sim > 0:
                similarities.append((sim, rating))
        if not similarities:
            # если нет похожих фильмов — возвращаем среднюю оценку виртуального пользователя
            mean = self.get_virtual_user_mean(user_id)
            return mean, 0

        numerator = 0.0
        denominator = 0.0
        for sim, rating in similarities:
            numerator += sim * rating
            denominator += sim
        if denominator == 0:
            return self.get_virtual_user_mean(user_id), 0
        return numerator / denominator, denominator

    def get_virtual_user_mean(self, user_id: int) -> float:
        """
        Расчет средней оценки виртуального пользователя

        :param int user_id: ID пользователя
        :return float: средняя оценка
        """
        ratings = list(self.virtual_users.get(user_id, {}).values())
        if not ratings:
            return 3.0  # нейтральное значение, если оценок нет
        return sum(ratings) / len(ratings)

    def recommend_for_virtual_user(self, user_id: int, n=5) -> list:
        """
        Рекомендация топ-n фильмов для виртуального пользователя

        :param int user_id: ID пользователя
        :param int n: количество рекомендаций
        :return list: список рекомендаций
        """
        if user_id not in self.virtual_users:
            print(f"Виртуальный пользователь {user_id} не найден")
            return []

        user_ratings = self.virtual_users[user_id]
        rated_movies = set(user_ratings.keys())
        all_movies = set(self.dh.get_movies_data())
        unrated_movies = all_movies - rated_movies
        predictions = []

        movies_to_process = list(unrated_movies)
        for movie_id in movies_to_process:
            pred_rating, sim_sum = self.predict_rating(user_id, movie_id)
            predictions.append((movie_id, pred_rating, sim_sum))
        predictions.sort(key=lambda x: (x[1], x[2]), reverse=True)
        if len(predictions) > n:
            predictions = predictions[:n]

        print(f"Вычислены рекомендации для виртуального пользователя {user_id}")
        for pred_movie in predictions:
            print(f"Фильм {self.dh.get_movie_title(pred_movie[0])}")
            sims = []
            for rated_movie in rated_movies:
                sims.append(
                    (
                        self.dh.get_movie_similarity(pred_movie[0], rated_movie),
                        rated_movie,
                    )
                )
            top_sims = sorted(
                [x for x in sims if x[0] > 0], key=lambda x: x[0], reverse=True
            )[:3]
            for sim, movie_id in top_sims:
                print(
                    f"  {self.dh.get_movie_title(movie_id)}, схожесть: {sim}, оценка пользователя: {self.virtual_users[user_id][movie_id]}"
                )
        return predictions

    def get_virtual_user_ratings(self, user_id: int) -> dict:
        """
        Получение профиля виртуального пользователя

        :param int user_id: ID пользователя
        :return dict: словарь оценок
        """
        if user_id in self.virtual_users:
            return self.virtual_users[user_id]
        else:
            print(f"Виртуальный пользователь {user_id} не найден")
            return {}
