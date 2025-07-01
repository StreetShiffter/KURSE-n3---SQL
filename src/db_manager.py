from typing import Any, List, Tuple  # Убрали неиспользуемый Optional

import psycopg2

from config import config


class DBManager:
    def __init__(self) -> None:
        self.conn = psycopg2.connect(**config())  # type: ignore

    def get_companies_and_vacancies_count(self) -> List[Tuple[Any, ...]]:
        """Получает список всех компаний и количество вакансий у каждой компании"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT employers.name, COUNT(vacancies.id)
                FROM employers
                LEFT JOIN vacancies ON employers.id_company = vacancies.employer_id
                GROUP BY employers.name
                """
            )
            return cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple[Any, ...]]:
        """Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT employers.name,
                       vacancies.name,
                       vacancies.salary_from,
                       vacancies.salary_to,
                       vacancies.currency,
                       vacancies.url
                FROM vacancies
                JOIN employers ON employers.id_company = vacancies.employer_id
                """
            )
            return cur.fetchall()

    def get_avg_salary(self) -> float | None:  # Python 3.10+: используем | вместо Optional
        """Получает среднюю зарплату по всем вакансиям с указанием ЗП"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT AVG((salary_from + salary_to)/2)
                FROM vacancies
                WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
                """
            )
            result = cur.fetchone()
            return result[0] if result else None

    def get_vacancies_with_higher_salary(self, avg_salary: float) -> List[Tuple[Any, ...]]:
        """Получает вакансии с зарплатой выше средней"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT name, salary_from, salary_to, currency, url
                FROM vacancies
                WHERE (salary_from + salary_to)/2 > %s
                  AND salary_from IS NOT NULL
                  AND salary_to IS NOT NULL
                """,
                (avg_salary,),
            )
            return cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[Any, ...]]:
        """Находит вакансии по ключевому слову в названии вакансии"""
        with self.conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, salary_from, salary_to, currency, url
                FROM vacancies
                WHERE name ILIKE %s
                """,
                (f"%{keyword}%",),
            )
            return cur.fetchall()

    def close(self) -> None:
        """Закрывает БД"""
        self.conn.close()
