import numpy as np
import random
import math
from data_handler import DataHandler


class SVDppRecommender:
    def __init__(
        self, data_handler: DataHandler, n_factors=20, n_epochs=25, lr=0.05, reg=0.02
    ):
        """
        Инициализация SVD++

        :param n_factors: количество латентных факторов
        :param n_epochs: количество эпох обучения
        :param lr: скорость обучения
        :param reg: параметр регуляризации
        """
        self.dh = data_handler
        self.n_factors = n_factors
        self.n_epochs = n_epochs
        self.lr = lr
        self.reg = reg

        self.all_items = self.dh.get_movies_data()
        user_ratings = self.dh.get_user_ratings()

        scale = 0.1 / math.sqrt(self.n_factors)
        self.num_users = len(user_ratings)
        self.user_factors = np.random.normal(
            scale=scale, size=(self.num_users, self.n_factors)
        )
        self.user_biases = np.zeros(self.num_users)
        self.num_items = len(self.all_items)
        self.item_factors = np.random.normal(
            scale=scale, size=(self.num_items, self.n_factors)
        )
        self.item_biases = np.zeros(self.num_items)

        all_ratings = []
        for items in user_ratings.values():
            all_ratings.extend(items.values())
        self.global_mean = np.mean(all_ratings) if all_ratings else 0

        user_ids = list(user_ratings.keys())
        self.user_to_idx = {uid: i for i, uid in enumerate(user_ids)}
        self.idx_to_user = {i: uid for i, uid in enumerate(user_ids)}
        self.item_to_idx = {iid: i for i, iid in enumerate(self.all_items)}
        self.idx_to_item = {i: iid for i, iid in enumerate(self.all_items)}

        self.user_items = {}
        self.user_ratings = {}
        for user_id, ratings in user_ratings.items():
            user_idx = self.user_to_idx[user_id]
            self.user_items[user_idx] = []
            self.user_ratings[user_idx] = {}
            for item_id, rating in ratings.items():
                item_idx = self.item_to_idx[item_id]
                self.user_items[user_idx].append(item_idx)
                self.user_ratings[user_idx][item_idx] = rating

        self.virtual_users = {}
        self.trained_for_user = {}

        self.train()

    def get_user_implied_vector(self, user_idx: int) -> np.ndarray:
        """
        Вычисление вектора неявных предпочтений пользователя
        (среднее по всем предметам, с которыми взаимодействовал пользователь)

        :param user_idx: индекс пользователя
        :return: вектор неявных предпочтений
        """
        if user_idx not in self.user_items or not self.user_items[user_idx]:
            return np.zeros(self.n_factors)

        items = self.user_items[user_idx]
        implied_sum = np.sum([self.item_factors[item] for item in items], axis=0)
        return implied_sum / len(items)

    def predict(self, user_id: int, item_id: int) -> float:
        """
        Предсказание оценки пользователя для фильма

        :param user_id: ID пользователя
        :param item_id: ID фильма
        :return: предсказанная оценка
        """
        if user_id not in self.user_to_idx or item_id not in self.item_to_idx:
            return self.global_mean

        user_idx = self.user_to_idx[user_id]
        item_idx = self.item_to_idx[item_id]
        prediction = (
            self.global_mean + self.user_biases[user_idx] + self.item_biases[item_idx]
        )
        user_vector = self.user_factors[user_idx] + self.get_user_implied_vector(
            user_idx
        )
        prediction += np.dot(user_vector, self.item_factors[item_idx])
        return np.clip(prediction, 1.0, 5.0)

    def train(self):
        """Обучение модели SVD++"""
        print(f"Обучение модели SVD++ ({self.n_epochs} эпох):")
        for epoch in range(self.n_epochs):
            total_loss = 0
            num = 0
            for user_idx in range(self.num_users):
                implied_vector = self.get_user_implied_vector(user_idx)
                for item_idx, true_rating in self.user_ratings[user_idx].items():
                    prediction = (
                        self.global_mean
                        + self.user_biases[user_idx]
                        + self.item_biases[item_idx]
                    )
                    prediction += np.dot(
                        self.user_factors[user_idx] + implied_vector,
                        self.item_factors[item_idx],
                    )

                    error = true_rating - prediction
                    total_loss += error**2

                    user_grad = (
                        error * self.item_factors[item_idx]
                        - self.reg * self.user_factors[user_idx]
                    )
                    item_grad = (
                        error * (self.user_factors[user_idx] + implied_vector)
                        - self.reg * self.item_factors[item_idx]
                    )
                    user_bias_grad = error - self.reg * self.user_biases[user_idx]
                    item_bias_grad = error - self.reg * self.item_biases[item_idx]

                    self.user_factors[user_idx] += self.lr * user_grad
                    self.item_factors[item_idx] += self.lr * item_grad
                    self.user_biases[user_idx] += self.lr * user_bias_grad
                    self.item_biases[item_idx] += self.lr * item_bias_grad

                    num += 1

            self.lr *= 0.95
            avg_loss = total_loss / num
            print(f"  эпоха {epoch + 1}/{self.n_epochs}, Loss: {avg_loss:.4f}")

    def create_virtual_user(self, user_id: int) -> None:
        """
        Создание виртуального пользователя

        :param int user_id: ID пользователя
        """
        self.virtual_users[user_id] = {}
        self.trained_for_user[user_id] = False

        new_idx = len(self.idx_to_user)
        self.user_to_idx[user_id] = new_idx
        self.idx_to_user[new_idx] = user_id

        scale = 0.1 / math.sqrt(self.n_factors)
        new_user_factor = np.random.normal(scale=scale, size=self.n_factors)
        self.user_factors = np.vstack([self.user_factors, new_user_factor])
        self.user_biases = np.append(self.user_biases, 0.0)

        self.user_items[new_idx] = []
        self.user_ratings[new_idx] = {}
        self.num_users += 1
        print(f"Создан виртуальный пользователь {user_id}")

    def update_virtual_user(self, user_id: int, item_id: int, rating: int) -> None:
        """
        Добавление оценки фильма для виртуального пользователя

        :param int user_id: ID пользователя
        :param int item_id: ID фильма
        :param int rating: оценка фильма
        """
        self.virtual_users[user_id][item_id] = rating
        self.trained_for_user[user_id] = False
        user_idx = self.user_to_idx[user_id]
        item_idx = self.item_to_idx[item_id]
        self.user_items[user_idx].append(item_idx)
        self.user_ratings[user_idx][item_idx] = rating
        print(
            f"Добавлена оценка {rating} фильма {item_id} для виртуального пользователя {user_id}"
        )

    def delete_virtual_user(self, user_id: int) -> None:
        """
        Удаление оценок виртуального пользователя

        :param int user_id: ID пользователя
        """
        if user_id in self.virtual_users.keys():
            del self.virtual_users[user_id]
            print(f"Удален виртуальный пользователь {user_id}")

    def train_for_user(self, user_id: int):
        """
        Дообучение модели только для конкретного пользователя

        :param user_id: ID пользователя
        """
        print(f"Дообучение модели для пользователя {user_id}")
        user_idx = self.user_to_idx[user_id]
        for _ in range(self.n_epochs):
            implied_vector = self.get_user_implied_vector(user_idx)
            for item_idx, true_rating in self.user_ratings[user_idx].items():
                prediction = (
                    self.global_mean
                    + self.user_biases[user_idx]
                    + self.item_biases[item_idx]
                )
                prediction += np.dot(
                    self.user_factors[user_idx] + implied_vector,
                    self.item_factors[item_idx],
                )

                error = true_rating - prediction

                user_grad = (
                    error * self.item_factors[item_idx]
                    - self.reg * self.user_factors[user_idx]
                )
                user_bias_grad = error - self.reg * self.user_biases[user_idx]

                self.user_factors[user_idx] += self.lr * user_grad
                self.user_biases[user_idx] += self.lr * user_bias_grad

            self.lr *= 0.95

        self.trained_for_user[user_id] = True

    def recommend_for_virtual_user(self, user_id: int, n_recommendations: int) -> list:
        """
        Рекомендация предметов для пользователя

        :param user_id: ID пользователя
        :param n_recommendations: количество рекомендаций
        :return: список рекомендаций
        """
        if user_id not in self.user_to_idx:
            print(f"Виртуальный пользователь {user_id} не найден")
            return []

        if not (self.trained_for_user[user_id]):
            self.train_for_user(user_id)

        rated_items = set(self.virtual_users[user_id].keys())
        predictions = []
        for item_id in self.all_items:
            if item_id not in rated_items:
                pred = self.predict(user_id, item_id)
                predictions.append((item_id, pred))
        predictions.sort(key=lambda x: x[1], reverse=True)
        return predictions[:n_recommendations]

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