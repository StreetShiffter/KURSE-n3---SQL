# Сторонние библиотеки
import psycopg2
from config import config

# Локальные модули
from src.api_class import HeadHunterAPI
from src.utils import insert_employers, insert_vacancies, clear_employers_table, clear_vacancies_table
from src.database import create_database, create_tables
from src.db_manager import DBManager


def user_interface(text):
    if text == 'да':
        api = HeadHunterAPI()
        user_input = input("Введите название вакансии(например, 'Разработчик'): ").lower()
        try:
            # Шаг 1: получаем список вакансий по ключевому слову
            vacancies = api.get_vacancies(keyword=user_input, per_page=10)

            print(f"Получено вакансий: {len(vacancies)}")

            # Шаг 2: сохраняем всех работодателей из этих вакансий
            insert_employers(vacancies)

            # Шаг 3: сохраняем сами вакансии (теперь работодатели уже в БД)
            insert_vacancies(vacancies)

            # Шаг 4: выводим информацию о вакансиях

            manager = DBManager()
            print("\nВыберите действие:")
            print("1. Вывести компании и количество вакансий")
            print("2. Вывести все вакансии")
            print("3. Средняя зарплата")
            print("4. Вакансии с зарплатой выше средней")
            print("5. Поиск вакансий по ключевому слову")

            choice = input("Введите номер действия: ")

            if choice == "1":
                res = manager.get_companies_and_vacancies_count()
                print("\n🏢 Компании и количество вакансий:")
                for name, count in res:
                    print(f"{name}: {count} вакансий")
                    print("*"*50)

            elif choice == "2":
                res = manager.get_all_vacancies()
                print("\n💼 Все вакансии:")
                for item in res:
                    print(item)
                    print("*" * 50)

            elif choice == "3":
                avg = manager.get_avg_salary()
                print(f"\n💰 Средняя зарплата: {avg:.2f}")
                print("*" * 50)

            elif choice == "4":
                avg = manager.get_avg_salary()
                res = manager.get_vacancies_with_higher_salary(avg)
                print(f"\n📈 Вакансии с зарплатой выше средней ({avg:.2f}):")
                for item in res:
                    print(item)
                    print("*" * 50)

            elif choice == "5":
                word = input("Введите ключевое слово: ")
                res = manager.get_vacancies_with_keyword(word)
                print(f"\n🔎 Результаты поиска по '{word}':")
                for item in res:
                    print(item)
                    print("*" * 50)

            else:
                print("❗ Неверный выбор")


        except Exception as e:
            print(f"Ошибка при обработке вакансий: {e}")

        finally:
            manager.close()

    else:
        api = HeadHunterAPI()
        user_input = input('Введите от 1 или список интересующих компаний через запятую: ').lower()
        api.find_vacancies_by_company_names(user_input)






if __name__ == "__main__":
        create_database()
        create_tables()
        clear_employers_table()
        clear_vacancies_table()

        while True:
            user_question = input("Получить вакансии из топ 10 компаний: да/нет ").strip().lower()
            if user_question in ['да', 'нет']:
                break
            else:
                print('❗ Введите только "да" или "нет"!')

        user_interface(user_question)
# for vacancy in vacancies:
#     employer = vacancy.get('employer', {})
#     employer_name = employer.get('name', 'Не указано')
#     vacancy_name = vacancy.get('name')
#
#     print(f"\nВакансия: {vacancy_name}")
#     print(f"Работодатель: {employer_name}")




# elif text == 'нет':
#     user_input = input("Введите список от одной до 10 компаний через пробел: ").lower().strip()
#     names = user_input.split()
#     if len(names) > 10:
#         print("❗ Введите не более 10 компаний")
#         return
#
#     print("🔍 Загрузка данных из API...")
#     load = loader_vacancy(user_input)  # Вакансии по ключевому слову
#     filter = loader_company(load)  # Все вакансии этих компаний
#
#     if not load:
#         print("❌ Не найдено ни одного работодателя.")
#         return
#
#     print(f"✅ Найдено {len(load)} уникальных работодателей")
#     insert_employers(filter)
#
#     print("💼 Сохранение вакансий...")
#     if not filter:
#         print("❌ Нет вакансий для сохранения")
#         return
#     print(f"✅ Найдено {len(filter)} вакансий")
#     insert_vacancies(filter)
#
#     print("\nВыберите действие:")
#     print("1. Вывести компании и количество вакансий")
#     print("2. Вывести все вакансии")
#     print("3. Средняя зарплата")
#     print("4. Вакансии с зарплатой выше средней")
#     print("5. Поиск вакансий по ключевому слову")
#
#     choice = input("Введите номер действия: ")
#
#     if choice == "1":
#         res = manager.get_companies_and_vacancies_count()
#         print("\n🏢 Компании и количество вакансий:")
#         for name, count in res:
#             print(f"{name}: {count} вакансий")
#
#     elif choice == "2":
#         res = manager.get_all_vacancies()
#         print("\n💼 Все вакансии:")
#         for item in res:
#             print(item)
#
#     elif choice == "3":
#         avg = manager.get_avg_salary()
#         print(f"\n💰 Средняя зарплата: {avg:.2f}")
#
#     elif choice == "4":
#         avg = manager.get_avg_salary()
#         res = manager.get_vacancies_with_higher_salary(avg)
#         print(f"\n📈 Вакансии с зарплатой выше средней ({avg:.2f}):")
#         for item in res:
#             print(item)
#
#     elif choice == "5":
#         word = input("Введите ключевое слово: ")
#         res = manager.get_vacancies_with_keyword(word)
#         print(f"\n🔎 Результаты поиска по '{word}':")
#         for item in res:
#             print(item)
#
#     else:
#         print("❗ Неверный выбор")
# else:
#     print('Введите только "да" или "нет"!')
#
# manager.close()