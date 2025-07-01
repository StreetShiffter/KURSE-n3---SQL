
import psycopg2
from config import config
from typing import Dict, Any, List


def process_vacancy(vacancy: Dict[str, Any]) -> Dict[str, Any]:
    """Представление вакансий по конкретным полям"""
    salary = vacancy.get("salary")

    return {
        "id": vacancy["id"],
        "employer_id": vacancy["employer"]["id"],
        "name": vacancy["name"],
        "area": vacancy["area"]["name"] if vacancy.get("area") else None,
        "salary_from": salary["from"] if salary and "from" in salary else None,
        "salary_to": salary["to"] if salary and "to" in salary else None,
        "currency": salary["currency"] if salary and "currency" in salary else None,
        "url": vacancy["alternate_url"],
    }


def insert_employers(vacancies: List[Dict[str, Any]]) -> None:
    """
    Добавляет работодателей в таблицу employers на основе списка вакансий.
    Берёт данные из поля 'employer' каждой вакансии.
    """
    conn = psycopg2.connect(**config())  # type: ignore
    cur = conn.cursor()

    for vac in vacancies:
        try:
            employer = vac.get("employer")

            if not employer or "id" not in employer:
                print("❌ Пропущена запись: нет данных о работодателе")
                continue

            employer_id = employer["id"]
            name = employer.get("name")
            alternate_url = employer.get("alternate_url")
            area = vac.get("area", {}).get("name") if vac.get("area") else None

            cur.execute(
                """
                INSERT INTO employers (id_company, name, alternate_url, area)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (id_company) DO NOTHING
            """,
                (employer_id, name, alternate_url, area),
            )

        except Exception as e:
            print(
                f"❌ Ошибка при добавлении работодателя из вакансии {vac.get('id')}: {e}"
            )

    conn.commit()
    cur.close()
    conn.close()


def insert_vacancies(vacancies: List[Dict[str, Any]]) -> None:
    """Добавляет вакансии работодателей в таблицу vacancies на основе списка работодателей."""
    conn = psycopg2.connect(**config())  # type: ignore
    cur = conn.cursor()

    for vac in vacancies:  # Перебор каждого работодателя
        try:
            employer = vac.get("employer")
            if not employer or "id" not in employer:
                print(f"Пропущена вакансия {vac['id']} — нет данных о работодателе")
                continue

            employer_id = employer[
                "id"
            ]  # получаем ID работодателя для проверки на дубли

            # Проверяем, существует ли работодатель в БД
            cur.execute("SELECT 1 FROM employers WHERE id_company = %s", (employer_id,))
            if cur.fetchone() is None:
                print(
                    f"Пропущена вакансия {vac['id']} — работодатель {employer_id} не найден в БД"
                )
                continue

            # Вставляем вакансию
            cur.execute(
                """
                INSERT INTO vacancies (id, employer_id, name, salary_from, salary_to, currency, url)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO NOTHING
            """,
                (
                    vac["id"],
                    employer_id,
                    vac["name"],
                    (
                        vac["salary"]["from"]
                        if vac.get("salary") and vac["salary"].get("from")
                        else None
                    ),
                    (
                        vac["salary"]["to"]
                        if vac.get("salary") and vac["salary"].get("to")
                        else None
                    ),
                    (
                        vac["salary"]["currency"]
                        if vac.get("salary") and vac["salary"].get("currency")
                        else None
                    ),
                    vac["alternate_url"],
                ),
            )