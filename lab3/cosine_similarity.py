from math import sqrt


def cosine_similarity(ratings1: dict, ratings2: dict) -> float:
    """
    Косинусное сходство между двумя векторами оценок (словарями user->rating).

    :param dict ratings1: оценки первого фильма (user_id -> rating)
    :param dict ratings2: оценки второго фильма (user_id -> rating)
    :return float: косинусное сходство в диапазоне [0,1] (или 0, если нет общей информации)
    """
    common_users = []
    for user in ratings1.keys():
        if user in ratings2.keys():
            common_users.append(user)
    n = len(common_users)
    if n < 2:
        return 0

    dot = 0.0
    norm1 = 0.0
    norm2 = 0.0
    for u in common_users:
        r1 = ratings1[u]
        r2 = ratings2[u]
        dot += r1 * r2

    # Вычислим нормы по оценкам
    for u in common_users:
        norm1 += ratings1[u] ** 2
        norm2 += ratings2[u] ** 2

    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot / (sqrt(norm1) * sqrt(norm2))
