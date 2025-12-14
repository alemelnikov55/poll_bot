import os
import re
from pathlib import Path

import gspread
from typing import List, Dict, Union

from oauth2client.service_account import ServiceAccountCredentials
from gspread.utils import ValueRenderOption
from gspread.exceptions import WorksheetNotFound

from loader import TableSettings

# from loader import TABLE_NAME



abs_path = Path(os.path.dirname(__file__))

# Укажите область доступа
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Замените 'path/to/your/service_account.json' на путь к вашему JSON-файлу
creds = ServiceAccountCredentials.from_json_keyfile_name(f'{abs_path}/credentials.json', scope)

# Подключение к Google Sheets
client = gspread.authorize(creds)

# Откройте таблицу по названию
spreadsheet = client.open(TableSettings.TABLE_NAME)

# Откройте нужный лист по имени
# worksheet = spreadsheet.worksheet("Лист1")


async def get_sheet_task_data(sheet_name: str) -> List[Dict[str, Union[int, str, None]]]:
    """
    Получает данные из таблицы Google Sheets по имени листа

    :param sheet_name: str Название листа
    :return: List[Dict[str, Union[int, str, None]]] Список словарей с данными из таблицы
    """
    try:
        worksheet = spreadsheet.worksheet(sheet_name)
    except WorksheetNotFound as exc:
        raise exc
    data = worksheet.get_all_values(value_render_option=ValueRenderOption.formula)

    # Получаем заголовки из первой строки
    headers = data[0]

    # Создаём список словарей
    result = []

    # Проходим по всем строкам, начиная со второй
    for row in data[1:]:
        row_dict = {}
        for i, value in enumerate(row):
            # Проверяем, является ли значение ссылкой
            if isinstance(value, str) and (value.startswith("=IMAGE")):
                url = re.search(r'\"(.*?)\"', value)
                row_dict[headers[i]] = value[url.span()[0] + 1: url.span()[1] - 1]  # Если это ссылка, сохраняем её
            else:
                row_dict[headers[i]] = value  # В противном случае сохраняем значение
        result.append(row_dict)

    return result



