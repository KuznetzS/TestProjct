# Здесь хранятся SQL-запросы.
#   SQL-запрос SQL-запрос для вставки данных в лог search_queries  (устарел поменял логику записи запросов в файл)
INSERT_QUERY = """
    INSERT INTO search_queries (query) 
    VALUES (%s);
"""
#  SQL-запрос для создания таблицы search_queries_andreas  - запись поисковых запросов
CREATE_SEARCH_QUERIES_TABLE = """
CREATE TABLE IF NOT EXISTS search_queries_andreas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    queries VARCHAR(255) NOT NULL,
    key_word VARCHAR(64),
    film_title VARCHAR(128),
    film_description VARCHAR(64),
    film_year YEAR,
    category_name VARCHAR(25),
    search_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""
#---SQL-запрос для Создание View  таблицы определениe популярности фильмов на основе количества прокатов--
"""  Информация для понимания  связей таблиц на основе которой делался рейтинг
Таблица rental содержит информацию о каждой аренде, зарегистрированной в системе. Поля этой таблицы включают:
•	rental_id: Уникальный идентификатор аренды (первичный ключ).
•	rental_date: Дата и время начала аренды.
•	inventory_id: Идентификатор инвентарной записи, которая была арендована (внешний ключ, ссылается на таблицу inventory).
•	customer_id: Идентификатор клиента, который арендовал фильм (внешний ключ, ссылается на таблицу customer).
•	return_date: Дата и время возврата арендованного фильма. Может быть NULL, если фильм еще не возвращен.
•	staff_id: Идентификатор сотрудника, который обработал аренду (внешний ключ, ссылается на таблицу staff).
•	last_update: Дата и время последнего обновления записи аренды.

Таблица inventory хранит информацию об инвентарных записях фильмов, доступных для аренды. Поля этой таблицы включают:
•	inventory_id: Уникальный идентификатор инвентарной записи (первичный ключ).
•	film_id: Идентификатор фильма, связанный с этой инвентарной записью (внешний ключ, ссылается на таблицу film).
•	store_id: Идентификатор магазина, в котором находится данная инвентарная запись (внешний ключ, ссылается на таблицу store).
•	last_update: Дата и время последнего обновления записи инвентаря.
"""
CREATE_VIEW_FILM = """
CREATE OR REPLACE VIEW view_film AS
SELECT f.film_id, f.title, f.description, f.release_year, rentals.rental_count
FROM   film f
JOIN   (
        SELECT     i.film_id, COUNT(r.rental_id) AS rental_count
        FROM       inventory i
        JOIN       rental r ON i.inventory_id = r.inventory_id
        GROUP BY   i.film_id
    ) AS rentals ON f.film_id = rentals.film_id
ORDER BY     rentals.rental_count DESC
"""
#  SQL-запрос для вставки данных в лог таблицу search_queries_andreas

INSERT_SEARCH_QUERY = """
    INSERT INTO search_queries_andreas (
        queries, key_word, film_title, film_description, film_year, category_name) 
    VALUES (%s, %s, %s, %s, %s, %s);
"""
# ---- Поиск популярных запросов из лог файла ---считает популярные запросы и выводит имя столбца, категории запроса

GET_POPULAR_QUERIES = """
SELECT 
    key_word,
    COUNT(key_word) AS key_word_count,
    GROUP_CONCAT(DISTINCT
        CASE 
            WHEN key_word = film_title THEN 'Название'
            WHEN key_word = film_description THEN 'Описание'
            WHEN key_word = CAST(film_year AS CHAR) THEN 'Год '
            WHEN key_word = category_name THEN 'Жанр'
            ELSE 'Запрос'
        END
    ) AS search_columns
FROM     search_queries_andreas
WHERE    key_word IS NOT NULL AND key_word != ''
GROUP BY key_word
ORDER BY key_word_count DESC
LIMIT 15;    
"""
#   SQL-запрос в первой версии поиска по популярным запросам
"""
    SELECT key_word, COUNT(*) as count 
    FROM search_queries_andreas 
    WHERE key_word IS NOT NULL
    GROUP BY key_word 
    ORDER BY count DESC
    LIMIT 10;
"""

#   SQL-запрос для поиска основной к нему добавляются короткие части кода ---- используется для поиска ключевых слов
SEARCH_MOVIES_BASE_QUERY = """
SELECT f.title, c.name AS genre, f.release_year, f.description
FROM film f
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
"""
#  (эти запросы тоже можно еще раз переписать так как часть кода в них одинаковая и сократить количество строк в файле)
#  новый SQL-запрос для поиска с учетом  рейтинга  VIEW view_film

SEARCH_MOVIES_BASE_QUERY_VIEW = """
SELECT f.title, c.name AS genre, f.release_year, f.description, vf.rental_count
FROM film f
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
JOIN view_film vf ON f.film_id = vf.film_id
"""

# --------SQL-запросы  функции search_by_genre_and_year------------
# ----- новые с учетом рейтинга фильмов
SEARCH_BY_GENRE_AND_YEAR = """
SELECT f.title, c.name AS genre, f.release_year, f.description, vf.rental_count
FROM film f
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
JOIN view_film vf ON f.film_id = vf.film_id
WHERE c.name = %s AND f.release_year = %s
ORDER BY vf.rental_count DESC, f.title 
LIMIT 50
"""

SEARCH_BY_GENRE = """
SELECT f.title, c.name AS genre, f.release_year, f.description, vf.rental_count
FROM film f
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
JOIN view_film vf ON f.film_id = vf.film_id
WHERE c.name = %s
ORDER BY vf.rental_count DESC, f.title 
LIMIT 50
"""

SEARCH_BY_YEAR = """
SELECT f.title, c.name AS genre, f.release_year, f.description, vf.rental_count
FROM film f
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
JOIN view_film vf ON f.film_id = vf.film_id
WHERE f.release_year = %s
ORDER BY vf.rental_count DESC, f.title 
LIMIT 50
"""

GET_ALL_GENRES = """
SELECT category_id, name FROM category
"""