import psycopg2
from config import DB_CONFIG

def create_database():
    '''СОЗДАНИЕ БАЗЫ ДАННЫХ ЛОКАЛЬНО'''
    conn = psycopg2.connect(
        dbname='postgres',
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        host=DB_CONFIG['host'],
        port=DB_CONFIG.get('port', 5432) # берем порт из DB_CONFIG, если нет, то берем 5432
    )
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute("CREATE DATABASE hh_vacancies")
        print("База данных hh_vacancies создана.")
    except psycopg2.errors.DuplicateDatabase:               # Ошибка если БД создана
        print("База данных hh_vacancies уже существует.")
    finally:
        cur.close()
        conn.close()

def create_tables():
    '''СОЗДАНИЕ ТАБЛИЦ РАБОТОДАТЕЛЕЙ И ВАКАНСИЙ ЛОКАЛЬНО'''
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
        """
    )
    conn = psycopg2.connect(**DB_CONFIG)
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