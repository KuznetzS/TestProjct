# Модуль, отвечающий за логику поиска фильмов и сохранение запросов.
import re
from queries_sql_3 import GET_POPULAR_QUERIES, GET_ALL_GENRES
from queries_sql_3 import SEARCH_MOVIES_BASE_QUERY, INSERT_SEARCH_QUERY
from queries_sql_3 import SEARCH_BY_GENRE_AND_YEAR, SEARCH_BY_GENRE, SEARCH_BY_YEAR, SEARCH_MOVIES_BASE_QUERY_VIEW


# -----функции запрашивает ввод у пользователя и возвращает только корректное значение
def get_valid_command():
    while True:
        command = input("Введите номер команды: ").strip()
        if command in ['0', '1', '2', '3', '4', '5']:
            return command  # Возвращаем корректный ввод
        else:
            print("Некорректный ввод. Пожалуйста, введите число от 0 до 5.")

# -----функции  получения списка жанров---------------
def get_all_genres(db):
    genres = db.execute_query(GET_ALL_GENRES)
    print("\nДоступные жанры:")
    for genre_id, name in genres:
        print(f"{genre_id:<3} - {name}")
    while True:
        try:
            genre_id = input("Введите номер жанра: ").strip()
            genre = next((name for gid, name in genres if gid == int(genre_id)), None)
            if genre is None:
                print("Введите корректный номер жанра от 1 до 16 :")
                continue  # Возвращаемся к началу цикла
            return genre
        except ValueError:
            print("")
            return None

# -----функции  проверки корректности ввода года------------
def get_valid_year():
    while True:
        year = input("Введите год: ").strip()
        if year.isdigit() and len(year) == 4 and 1980 <= int(year) <= 2023:  #  диапазон годов
            return year
        else:
            print("Неверный ввод года. Введите корректный год в диапазоне 1980-2023.")
            continue


# -----функции  поиска фильмов по жанру или по году----обновленная версия-------------
def search_by_genre(db, db2, genre):
    params = (genre,)
    results = db.execute_query(SEARCH_BY_GENRE, params)
    db2.execute_update(INSERT_SEARCH_QUERY, (genre, genre, None, None, None, genre))
    return results


def search_by_year(db, db2, year):
    params = (int(year),)
    results = db.execute_query(SEARCH_BY_YEAR, params)
    db2.execute_update(INSERT_SEARCH_QUERY, (str(year), str(year), None, None, year, None))
    return results


# -----функция  ищет фильмы по жанру и по году----обновленная версия-------------

def search_by_genre_and_year(db, db2, genre, year):
    # Поиск по жанру и году
    params = (genre, int(year))
    results = db.execute_query(SEARCH_BY_GENRE_AND_YEAR, params)

    if results:
        # Фильмы найдены по жанру и году
        db2.execute_update(INSERT_SEARCH_QUERY, (f"{genre}-{year}", genre, None, None, year, genre))
        return results
    else:
        # Поиск только по жанру
        params_genre = (genre,)
        results_genre = db.execute_query(SEARCH_BY_GENRE, params_genre)

        if results_genre:
            db2.execute_update(INSERT_SEARCH_QUERY, (genre, genre, None, None, None, genre))
            return results_genre
        else:
            # Поиск только по году
            params_year = (int(year),)
            results_year = db.execute_query(SEARCH_BY_YEAR, params_year)

            if results_year:
                db2.execute_update(INSERT_SEARCH_QUERY, (str(year), str(year), None, None, year, None))
                return results_year
            else:
                # Ничего не найдено
                print("Ничего не найдено.")
                db.execute_update(INSERT_SEARCH_QUERY, (f"{genre}-{year}", f"{genre}-{year}", None, None, year, genre))
                return []


# -----функции  получения популярных запросов---------------
def get_popular_queries(db2):
    return db2.execute_query(GET_POPULAR_QUERIES)


# ----Новая функция-- Поиск и логирование по ключевым словам и запись в лог_файл ключевых слов в сответствующие поиску столбцы -----------------
def search_and_log_queries_view(db, db2, user_query):
    # Разбиваем запрос пользователя на ключевые слова, исключая слова короче 4 символов
    keywords = [word.lower() for word in re.findall(r'\w+', user_query) if len(word) > 3]

    if not keywords:
        print("Пожалуйста, введите более конкретный запрос.")
        return []

    # Генерируем условия для поиска фильмов по ключевым словам
    search_conditions = []
    params = []
    for keyword in keywords:
        condition = """
        (LOWER(f.title) LIKE %s 
        OR LOWER(f.description) LIKE %s 
        OR LOWER(c.name) LIKE %s 
        OR CAST(f.release_year AS CHAR) LIKE %s)
        """
        search_conditions.append(condition)
        params.extend([f"%{keyword}%" for _ in range(4)])

    # Строим полный SQL-запрос с учетом рейтинга фильмов
    full_query = SEARCH_MOVIES_BASE_QUERY_VIEW + " WHERE " + " OR ".join(
        search_conditions) + " ORDER BY vf.rental_count DESC, f.title LIMIT 50"

    # Выполняем SQL-запрос и получаем результаты
    results = db.execute_query(full_query, params)

    # Логика записи запроса и ключевых слов в таблицу search_queries_andreas
    cursor = db.connection.cursor()
    for keyword in keywords:
        keyword_found = False

        # Проверяем категорию использует  старый запрос без рейтинга фильмов.  -- LIMIT 1 -- нужен для скорости обработки, чтобы не перебирать всю базу
        cursor.execute(SEARCH_MOVIES_BASE_QUERY + " WHERE LOWER(c.name) LIKE %s LIMIT 1", (f"%{keyword}%",))
        if cursor.fetchone():
            db2.execute_update(INSERT_SEARCH_QUERY, (user_query, keyword, None, None, None, keyword))
            keyword_found = True

        # Проверяем название
        if not keyword_found:
            cursor.execute(SEARCH_MOVIES_BASE_QUERY + " WHERE LOWER(f.title) LIKE %s LIMIT 1", (f"%{keyword}%",))
            if cursor.fetchone():
                db2.execute_update(INSERT_SEARCH_QUERY, (user_query, keyword, keyword, None, None, None))
                keyword_found = True

        # Проверяем описание
        if not keyword_found:
            cursor.execute(SEARCH_MOVIES_BASE_QUERY + " WHERE LOWER(f.description) LIKE %s LIMIT 1", (f"%{keyword}%",))
            if cursor.fetchone():
                db2.execute_update(INSERT_SEARCH_QUERY, (user_query, keyword, None, keyword, None, None))
                keyword_found = True

        # Проверяем год выпуска
        if not keyword_found:
            cursor.execute(SEARCH_MOVIES_BASE_QUERY + " WHERE CAST(f.release_year AS CHAR) LIKE %s LIMIT 1",
                           (f"%{keyword}%",))
            if cursor.fetchone():
                db2.execute_update(INSERT_SEARCH_QUERY, (user_query, keyword, None, None, keyword, None))
                keyword_found = True

        # Если не найдено ни одно совпадение, записываем запрос с пустыми полями
        if not keyword_found:
            db2.execute_update(INSERT_SEARCH_QUERY, (user_query, keyword, None, None, None, None))

    cursor.close()
    return results

# --функция устарела из версии 2 ------- поиск по нескольким ключевым словам строго по запросу ----AND----- поиска по всем ключевым словам

def search_movies_AND(db, user_query):
    # Разбиваем запрос пользователя на ключевые слова, исключая слова короче 3 символов
    keywords = [word.lower() for word in re.findall(r'\w+', user_query) if len(word) >= 3]

    if not keywords:
        print("Пожалуйста, введите более конкретный запрос.")
        return []

    # Создание условий для поиска по ключевым словам
    conditions = []
    for keyword in keywords:
        condition = """
        (LOWER(f.title) LIKE %s 
        OR LOWER(f.description) LIKE %s 
        OR LOWER(c.name) LIKE %s 
        OR CAST(f.release_year AS CHAR) LIKE %s)
        """
        conditions.append(condition)
        # Логирование поискового запроса
        db.execute_update(INSERT_SEARCH_QUERY, (user_query, keyword, None, None, None, None))

    # Соединение условий с помощью оператора AND
    full_query = SEARCH_MOVIES_BASE_QUERY + " WHERE " + " AND ".join(conditions) + " ORDER BY f.title LIMIT 10"

    # Подготовка параметров для запроса по ключевым словам
    params = [f"%{keyword}%" for keyword in keywords for _ in range(4)]
    results = db.execute_query(full_query, params)

    return results


