from configparser import ConfigParser
from typing import Dict



def config(filename="database.ini", section="postgresql") -> Dict[str, str]:
    """
    Получаем параметры подключения к базе данных из файла конфигурации
    """
    parser = ConfigParser()
    parser.read(filename, encoding='utf-8')
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(
            'Section {0} is not found in the {1} file.'.format(section, filename))
    return db

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 OPR/118.0.0.0 (Edition std-2)"

# DB_CONFIG = {
#     'dbname': 'hh_vacancies',
#     'user': 'postgres',
#     'password': 12345,
#     'host': 'localhost',
#     'port': 5432
# }