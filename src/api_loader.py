import requests
from config import USER_AGENT
import re
from pprint import pprint
import json
import os

# Получаем путь к текущему скрипту
script_dir = os.path.dirname(os.path.abspath(__file__))
path_to_json = os.path.join(script_dir, "../data/vacancy_hh.json")
os.makedirs(os.path.dirname(path_to_json), exist_ok=True)

''' ШАГ 1 - ПОИСК ID КОМПАНИЙ - ✅ '''

def loader_vacancy(companies_input: str):
    """Ищет работодателя ТОЛЬКО по названию компании и возвращает его ID."""
    company_names = [name.strip() for name in companies_input.split(',')]
    employer_ids = []

    for name_co in company_names:
        url = "https://api.hh.ru/employers"
        headers = {'User-Agent': USER_AGENT}
        params = {"text": name_co}

        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            employers = response.json().get("items", [])

            if employers:
                employer_id = employers[0]['id']# При соблюдении условия берем первый id из employer
                employer_ids.append(employer_id)
                print(f"Найден ID '{employer_id}' для компании '{name_co}'")
            else:
                employer_ids.append(None)
                print(f"Компания '{name_co}' не найдена.")

        except requests.RequestException as e:
            print(f"Ошибка при поиске компании '{name_co}': {e}")
            employer_ids.append(None)

    return employer_ids


'''Шаг 2: Определяем ID компании из списка вакансий и производим поиск вакансий от ПОЛУЧЕННЫХ РАБОТОДАТЕЛЕЙ - ✅ '''
def loader_company(id_company):
    '''Нахождение вакансий от работодателей из списка вакансий по ID работодателя'''
    url = "https://api.hh.ru/vacancies"
    headers = {'User-Agent': USER_AGENT}
    all_vacancies = []

    for employer_id in id_company:
        if employer_id is None:
            print(f"Пропущен недопустимый ID компании: {employer_id}")
            continue
        params = {"employer_id": employer_id, "per_page": 10}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
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

'''Шаг 3: Определяем вакансии по топ 10 ID компании из списка  - ✅ '''
def company_top(id_list):
    '''Получение вакансий из списка ID компаний'''
    all_vacancies = []
    url = "https://api.hh.ru/vacancies"  # один раз, так как URL не меняется
    headers = {"User-Agent": USER_AGENT}

    for item in id_list:
        params = {"employer_id": item, "per_page": 100}

        try:
            response = requests.get(url, headers=headers, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            all_vacancies.extend(data.get("items", []))

        except requests.RequestException as e:
            print(f"Ошибка при загрузке вакансий для {item}: {e}")

    with open(path_to_json, 'w', encoding='utf-8') as file:
        json.dump(all_vacancies, file, ensure_ascii=False, indent=4)

    return all_vacancies

#ДОП ФУНКЦИЯ ✅ (нужно передавать по одному ID компании)
def get_company_name(loader_company):
    '''Вывод названий компаний по ID'''
    url = f"https://api.hh.ru/employers/{loader_company}"
    headers = {"User-Agent": USER_AGENT}

    try:
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        data = response.json()
        return data["name"]
    except (requests.RequestException, KeyError):
        return "Неизвестная компания"




employer_id_top = [
            '9013908',  # НЭВЗ ✅
            '39305',    # Газпром нефть ✅
            '4592004',  # билайн ✅
            '749858',   # ВТБ ✅
            '80',       # Альфа-Банк ✅
            '3443',     # дом.рф ✅
            '592442',   # Mail.ru Group ✅
            '4996233',  # Роснефть
            '11454714', # Магнит ✅
            '9777667',  # Росатом ✅
        ]


if __name__ == '__main__':
    user_input = input("Введите список компании через запятую или одну: ").lower()
    step1=loader_vacancy(user_input)
    step2 = loader_company(step1)
    # step3=company_top(employer_id_top)
    # for i in employer_id_top:
    #     step4 = get_company_name(i)
    #
    #     pprint(f'{i} - ID компании {step4}')


