import json
import requests
from typing import Any, Dict, List, Optional
from config import USER_AGENT


import os

# Получаем путь к текущему скрипту
script_dir = os.path.dirname(os.path.abspath(__file__))
path_to_json = os.path.join(script_dir, "../data/vacancy_hh.json")
os.makedirs(os.path.dirname(path_to_json), exist_ok=True)

class HeadHunterAPI():
    """Класс для работы с API HeadHunter.
    Реализует методы подключения и получения вакансий"""

    def __init__(self) -> None:
        """Инициализация объекта HeadHunterAPI.
        Устанавливает базовый URL и заголовки для запросов"""
        self.__base_url_vacancies = "https://api.hh.ru/vacancies"
        self.__base_url_employers = "https://api.hh.ru/employers"
        self.__headers = {"User-Agent": USER_AGENT}
        self.__session: Optional[requests.Session] = None

    def _connect(self) -> requests.Response:
        """Устанавливает сессию и проверяет доступность API HeadHunter"""
        try:
            self.__session = requests.Session()
            response = self.__session.get(url=self.__base_url_vacancies, headers=self.__headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            raise ConnectionError(f"Ошибка подключения к API: {e}")

    def get_vacancies(self, keyword: str, per_page: int = 20, area: int = 113) -> List[Dict[str, Any]]:
        """Получает список вакансий по ключевому слову с параметрами пагинации и региона"""
        self._connect()
        params = {"text": keyword, "per_page": per_page, "area": area}
        response = self.__session.get(url=self.__base_url_vacancies, params=params, headers=self.__headers)
        if response.status_code != 200:
            raise ConnectionError(f"Ошибка получения вакансий: {response.status_code}")
        data = response.json()
        if not isinstance(data, dict):
            return []
        items = data.get("items", [])
        if not isinstance(items, list):
            return []
        return items

    def get_employers(self, text: str, per_page: int = 10) -> List[Dict[str, Any]]:
        """Поиск работодателей по тексту"""
        if not self.__session:
            self._connect()
        params = {"text": text, "per_page": per_page}
        response = self.__session.get(url=self.__base_url_employers, params=params, headers=self.__headers)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])

# ДОП МЕТОД
    def loader_company(self, companies_input: str) -> List[Optional[str]]:
        """Ищет работодателей по точному совпадению имени и возвращает их ID.(может работать независимо)"""
        if not self.__session:
            self._connect()

        company_names = [name.strip() for name in companies_input.split(',')]
        employer_ids = []

        for name_co in company_names:
            params = {"text": name_co, "per_page": 15}  # Можно увеличить per_page при необходимости
            try:
                response = self.__session.get(
                    url=self.__base_url_employers,
                    params=params,
                    headers=self.__headers
                )
                response.raise_for_status()
                employers = response.json().get("items", [])

                employer_id = None
                for employer in employers:
                    if employer.get("name") == name_co:
                        employer_id = employer.get("id")
                        print(f"✅ Найден ID '{employer_id}' для компании '{name_co}'")
                        break  # Выходим из цикла после нахождения


                if employer_id is None:
                    print(f"❌ Компания '{name_co}' не найдена.")

                employer_ids.append(employer_id)

            except requests.RequestException as e:
                print(f"⚠️ Ошибка при поиске компании '{name_co}': {e}")
                employer_ids.append(None)

        # Запись найденных ID компаний(тестовая проверка)
        with open(path_to_json, 'w', encoding='utf-8') as file:
            json.dump(employer_ids, file, ensure_ascii=False, indent=4)

        return employer_ids

    def _loader_company_vacancy(self, id_company: list) -> List[Dict]:
        '''Нахождение вакансий от работодателей из списка вакансий по ID работодателя(берем инфу от loader_vacancy)'''
        all_vacancies = []

        for employer_id in id_company:
            if employer_id is None:
                print(f"Пропущен недопустимый ID компании: {employer_id}")
                continue
            params = {"employer_id": employer_id, "per_page": 15}

            try:
                response = self.__session.get(url = self.__base_url_vacancies,
                                              headers=self.__headers,
                                              params=params,
                                              timeout=5)
                response.raise_for_status()
                data = response.json()

                vacancies = data.get("items", [])
                if vacancies:
                    all_vacancies.extend(vacancies)
                    print(f"Найдено {len(vacancies)} вакансий для работодателя {employer_id}")
                else:
                    print(f"Нет вакансий для работодателя {employer_id}")

            except requests.RequestException as e:
                print(f"Ошибка при загрузке вакансий для {employer_id}: {e}")

        with open(path_to_json, 'w', encoding='utf-8') as file:
            json.dump(all_vacancies, file, ensure_ascii=False, indent=4)

        return all_vacancies

    def find_vacancies_by_company_names(self, companies_input: str) -> List[Dict]:
        """Находит компании по имени, получает их ID и возвращает вакансии(метод-обертка вызывающая вакансии от
        loader_company, т.к. loader_company_vacancy не должен вызываться просто так)"""
        employer_ids = self.loader_company(companies_input)
        return self._loader_company_vacancy(employer_ids)

    # Шаг 1: Получаем ID компаний по названию
    #company_ids = api.loader_company("Яндекс,Сбербанк")

    # Шаг 2: По этим ID получаем вакансии
    #vacancies = api.loader_company_vacancy(company_ids)


if __name__ == "__main__":
    api = HeadHunterAPI()
    user_input = "разработчик"
    try:
        vacancies = api.get_vacancies(keyword=user_input, per_page=10)
        print(f"Получено вакансий: {len(vacancies)}")
        for vacancy in vacancies:
            print(f"Вакансия: { vacancy.get('name')}, URL: { vacancy.get('alternate_url')}")
    except Exception as e:
        print(f"Ошибка при получении вакансий: {e}")

    print("\n" + "-"*40 + "\n")


    try:
        employers = api.get_employers(text="мтс", per_page=10)
        print(f"Найдено работодателей: {len(employers)}")
        for employee in employers:
            print(f"Компания: {employee.get('name')}, ID: {employee.get('id')}")
    except Exception as e:
        print(f"Ошибка при поиске работодателей: {e}")
