# Этот модуль для форматирует и выводит результаты поиска и статистики.
from tabulate import tabulate   # ---от вывода в tabulate в итоге я отказался, эту строку можно удалять

# ---В Программе используется только 2 варианта ----вывод результата 5-я-версия--с учетом поля рейтингов--без описания фильмов------
def display_results_5(results):
    if not results:
        print("По вашему запросу ничего не найдено.")
        return

    print(f"Найдено фильмов: {len(results)}")
    print("1 - Вывести топ 10 фильмов ")
    print("2 - Вывести все найденные фильмы")
    choice = input("Введите номер команды: ")

    if choice == '1':
        results = results[:10]
    breit =79   #  количество дефисов  для вывода таблицы
    print("-" * breit)
    print(f"| №  |      Название Фильма       |     Жанр      |   Рейтинг   | Год выпуска |")
    print("-" * breit)
    for idx, row in enumerate(results, 1):
        title, genre, release_year, description, rental_count = row

        print(f"| {idx:<3}| {title:<25}  |   {genre:<11} |     {rental_count:<7} |   {release_year:<10}|")
        #print(f"Год выпуска: {release_year}")
        #print(f"Жанр: {genre}")
        #print(f"Количество прокатов: {rental_count}")
        #print(f"Описание: {description}")
        #print("-" * 60)

    print("-" * breit)
    print(f"Всего найдено результатов: {len(results)}")

    # ---- Вывод популярных запросов  --- табличный вывод методом ручного подбора дефисов (w)
def display_popular_queries(queries):
    w = 44
    print("=" * w)
    print("|       Самые популярные запросы:          |")
    print("-" * w)
    print("| № | Запрос  |  Количество  |  Категория  |")
    print("-" * w)
    for i, query_data in enumerate(queries):
        query, count, search_columns = query_data
        #print(f"{query} — {count} раз(а)")
        print(f"{i+1:<6}{query:<13}  {count:<8}   {search_columns:<11}| ")
    print("-" * w)

# --- ниже идут предыдущие варианты вывода из всех версий приложения , после того как попробовал разные, остановился на двух верхних
# --- все что ниже можно смело удалять, оставил только для практики и истории

# ----2 Вывод в виде таблицы --
def display_popular_queries_2(queries):
    print("-" * 40)
    print("\nПопулярные поисковые запросы:")
    table_data = [
        [idx, query, count]
        for idx, (query, count) in enumerate(queries, 1)
    ]
    headers = ["№", "Запрос", "Количество"]
    print(tabulate(table_data, headers=headers, tablefmt="grid", colalign=("center", "left", "center")))

#-------Вывод результата в таблицу (не удобно выводится описание фильма--------------
def display_results_table(results):
    if not results:
        print("По вашему запросу ничего не найдено.")
        return

    print(f"Найдено фильмов: {len(results)}")
    print("1 - Вывести топ 10 фильмов ")
    print("2 - Вывести все найденные фильмы")
    choice = input("Введите номер команды: ")

    if choice == '1':
        results = results[:10]

    table_data = []
    headers = ["№", "Название", "Жанр", "Рейтинг", "Год выпуска", "Описание"]

    for idx, row in enumerate(results, 1):
        title, genre, release_year, description, rental_count = row
        table_data.append([idx, title, genre, rental_count, release_year, description])

    print(tabulate(table_data, headers=headers, tablefmt="grid"))

    for idx, row in enumerate(results, 1):
        title, genre, release_year, description, rental_count = row
        print(f"\n{idx}. Описание: {description}")

    for idx, row in enumerate(results, 1):
        title, genre, release_year, description, rental_count = row
        table_data.append([idx, title, genre, rental_count, release_year])
        table_data.append([f"Описание: {description}", "", "", "", ""])

    headers = ["№", "Название", "Жанр", "Рейтинг", "Год выпуска"]
    print(
        tabulate(table_data, headers=headers, tablefmt="grid", colalign=("center", "left", "left", "center", "center")))


#-------выодит все построчно --------------
def display_results(results):

    if not results:
        print("По вашему запросу ничего не найдено.")
        return

    print(f"Найдено фильмов: {len(results)}")
    print("1 - Вывести топ 10 фильмов ")
    print("2 - Вывести все найденные фильмы")
    choice = input()

    if choice == '1':
        results = results[:10]

    for row in results:
        title = row[0]
        genre = row[1] if len(row) > 3 else "Жанр не указан"
        release_year = row[2] if len(row) > 1 else "Неизвестно"
        description = row[3] if len(row) > 2 else "Описание отсутствует"

        print("-" * 60)
        print(f"Название: {title}")
        print(f"Жанр: {genre}")
        print(f"Год выпуска: {release_year}")
        print(f"Описание: {description}")
        print("-" * 60)

    print(f"Всего найдено результатов: {len(results)}")




#--------старые версии вывода --------------
def display_results_001(results):
    if not results:
        print("Ничего не найдено.")
        return

    for row in results:
        if len(row) == 3:
            print(f"Название: {row[0]}, Жанр: {row[1]}, Год выпуска: {row[2]}")
        elif len(row) == 2 and isinstance(row[1], int):  # Условие для вывода, если возвращается название и год
            print(f"Название: {row[0]}, Год выпуска: {row[1]}")
        elif len(row) == 2:  # Условие для вывода, если возвращается название и жанр
            print(f"Название: {row[0]}, Жанр: {row[1]}")
        else:
            print(f"Название: {row[0]}")

        print("-" * 40)


def display_results_1(results):
    if results:
        for row in results:
            print(f"Название: {row[0]}, Год выпуска: {row[1]}\nОписание: {row[2]}\n")
    else:
        print("Фильмы не найдены по вашему запросу.")

def display_results_2(results):
   if results:
        for row in results:
            title, description, release_year, genre = row
            print(f"Название: {title}, Жанр: {genre}, Год выпуска: {release_year}")
            print(f"Описание: {description}")
            print("-" * 60)

        else:
            print("Ничего не найдено по вашему запросу.")