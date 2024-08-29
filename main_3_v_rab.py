# main.py
from db_manager_3 import DatabaseManager, ReadDatabaseManager
from search_def_3 import search_by_genre_and_year, get_popular_queries, search_by_genre, search_by_year
from search_def_3 import search_and_log_queries_view, get_all_genres, get_valid_command, get_valid_year
from output import display_popular_queries, display_results_5

def main():
    try:
        with DatabaseManager() as db2, ReadDatabaseManager() as db:

            while True:
                print("\n - Выберите действие:")
                print("-" * 44)
                print("0 - Выход из приложения")
                print("1 - Вывести топ 10 фильмов по жанру")
                print("2 - Вывести топ 10 фильмов по году выпуска")
                print("3 - Поиск по жанру и году")
                print("4 - Поиск по ключевому слову")
                print("5 - Вывести популярные запросы")
                print("-" * 44)

                command = get_valid_command()

                if command == "0":
                    print("Выход из программы.")
                    break

                elif command == "1":
                    genre = get_all_genres(db)
                    if genre:
                        results = search_by_genre(db, db2, genre)
                        print("-" * 44)
                        display_results_5(results)
                    else:
                        print("Неверный номер жанра.")

                elif command == "2":
                    year = get_valid_year()
                    results = search_by_year(db, db2, year)
                    print("-" * 44)
                    display_results_5(results)


                elif command == "3":
                    genre = get_all_genres(db)
                    year = get_valid_year()

                    if genre and year.isdigit():
                        results = search_by_genre_and_year(db, db2, genre, year)
                        print("-" * 44)
                        display_results_5(results)
                    else:
                        print("Неверный ввод жанра или года.")

                elif command == "4":
                    user_input = input(
                        "Введите название фильма, жанр, год выпуска или краткое описание фильма на английском языке : ")
                    user_query = user_input[:250]  # ограничиваем user_query до 250 символов
                    # Ищем фильмы и логируем запросы пользователя по столбцам поиска
                    results = search_and_log_queries_view(db, db2, user_query)
                    print("-" * 60)
                    # display_results_table(results)  #  вариант вывода в таблице не понравился
                    display_results_5(results)

                elif command == "5":
                    queries = get_popular_queries(db2)
                    display_popular_queries(queries)
                    # display_popular_queries_2(queries) # вариант вывода в таблице не понравился
                else:
                    print("Неизвестная команда. Попробуйте еще раз.")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        print("Завершение работы программы.")

if __name__ == "__main__":
    main()
