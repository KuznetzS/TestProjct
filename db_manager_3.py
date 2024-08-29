# модуль  отвечает за подключение к базам данных и выполнение SQL-запросов

import mysql.connector
from local_settings_1 import dbconfig_read
from local_settings_2 import dbconfig_2


# -----Базовый Класс подключения к базе данных--------------
class DatabaseManagerBase:
    def __init__(self, dbconfig):
        self.dbconfig = dbconfig
        self.connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        try:
            self.connection = mysql.connector.connect(**self.dbconfig)
            self.cursor = self.connection.cursor()
        except mysql.connector.Error as err:
            print(f"Error connecting to database: {err}")
            raise

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def is_exist_table(self, table_name):
        try:
            query = "SHOW TABLES LIKE %s"
            self.cursor.execute(query, (table_name,))
            result = self.cursor.fetchone()
            if not result:
                print(f"Таблица <{table_name}> не существует!")
                return False
            return True
        except mysql.connector.Error as err:
            print(f"Ошибка при проверке существования таблицы: {err}")
            return False

    def execute_query(self, query, params=None):
        try:
            self.check_connection()
            self.cursor.execute(query, params or [])
            return self.cursor.fetchall()
        except mysql.connector.Error as err:
            print(f"Ошибка при выполнении запроса: {err}")
            return []

    def execute_update(self, query, params=None):
        try:
            self.check_connection()
            self.cursor.execute(query, params or [])
            self.connection.commit()
        except mysql.connector.Error as err:
            print(f"Ошибка при выполнении обновления записи в таблице: {err}")
            self.connection.rollback()

    def check_connection(self):
        if not self.connection or not self.connection.is_connected():
            print("База данных не подключена. Попытка повторного подключения...")
            self.connect()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()


# ----- Класс подключения к базе данных на чтение-------------
class ReadDatabaseManager(DatabaseManagerBase):
    def __init__(self):
        super().__init__(dbconfig_read)


# ----- Класс подключения к базе данных на запись--------------
class DatabaseManager(DatabaseManagerBase):
    def __init__(self):
        super().__init__(dbconfig_2)


if __name__ == '__main__':
    with DatabaseManager() as db2, ReadDatabaseManager() as db:
        # Проверка подключения
        db.check_connection()
        db2.check_connection()

        # 1. Проверка создания подключения а базе данных
        rows = db.execute_query('SELECT category_id, name FROM category LIMIT 1;')
        assert rows and rows[0] == (1, 'Action'), "Ошибка в запросе категории!"

        # 2. Проверка метода .is_exist_table() проверяем существования нужной нам таблице в бд1 и в бд2
        assert db.is_exist_table('film') == True, "Ошибка: таблица film должна существовать!"
        assert db2.is_exist_table(
            'search_queries_andreas') == True, "Ошибка: таблица search_queries_andreas должна существовать!"

        # 3. Проверка выполнения update в таблице search_queries_andreas
        db2.execute_update("INSERT INTO search_queries_andreas (queries) VALUES (%s);", ("test query",))
        rows = db2.execute_query("SELECT queries FROM search_queries_andreas WHERE queries = %s;", ("test query",))
        assert rows and rows[0][0] == "test query", "Ошибка  записи в запросе к таблице search_queries_andreas!"

        print("Все тесты успешно пройдены!")
