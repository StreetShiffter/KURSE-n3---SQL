import psycopg2

from config import config


def create_database() -> None:
    """СОЗДАНИЕ БАЗЫ ДАННЫХ ЛОКАЛЬНО"""
    # Получаем параметры подключения (включая dbname)
    params = config()
    db_name = params.get("dbname")  # Берём имя БД из конфига

    # Подключаемся к Postgres без указания БД (используем 'postgres' или 'template1')
    conn = psycopg2.connect(**{k: v for k, v in params.items() if k != "dbname"})  # type: ignore
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f"CREATE DATABASE {db_name}")
        print(f"База данных {db_name} создана.")
    except psycopg2.errors.DuplicateDatabase:  # Ошибка если БД создана
        print(f"База данных {db_name} уже существует.")
    finally:
        cur.close()
        conn.close()


def create_tables() -> None:
    """СОЗДАНИЕ ТАБЛИЦ РАБОТОДАТЕЛЕЙ И ВАКАНСИЙ ЛОКАЛЬНО"""
    commands = (
        """
        CREATE TABLE IF NOT EXISTS employers (
            id_company VARCHAR(20) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            alternate_url TEXT,
            area VARCHAR(100)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS vacancies (
            id VARCHAR(20) PRIMARY KEY,
            employer_id VARCHAR(20) NOT NULL,
            name VARCHAR(255) NOT NULL,
            salary_from INTEGER,
            salary_to INTEGER,
            currency VARCHAR(10),
            url TEXT,
            FOREIGN KEY (employer_id)
                REFERENCES employers (id_company)
                ON DELETE CASCADE
        )
        """,
    )
    conn = psycopg2.connect(**config())  # type: ignore
    cur = conn.cursor()
    try:
        for command in commands:
            cur.execute(command)
        conn.commit()
        print("✅ Таблицы успешно созданы или уже существуют.")
    except Exception as e:
        print(f"❌ Ошибка при создании таблиц: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()
