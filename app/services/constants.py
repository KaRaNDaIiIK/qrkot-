from typing import Any, Dict, List


SPREADSHEET_BODY: Dict[str, Any] = {
    'properties': {
        'title': None,
        'locale': 'ru_RU'
    },
    'sheets': [{
        'properties': {
            'sheetType': 'GRID',
            'sheetId': 0,
            'title': None,
            'gridProperties': {
                'rowCount': 100,
                'columnCount': 11
            }
        }
    }]
}

PERMISSIONS_BODY: Dict[str, Any] = {
    'type': 'user',
    'role': 'writer',
    'emailAddress': None
}

TABLE_HEADERS: List[List] = [
    ['Отчёт от', None],
    ['Топ проектов по скорости закрытия'],
    ['№', 'Название проекта', 'Время сбора', 'Описание']
]

UPDATE_CONFIG: Dict[str, str] = {
    'majorDimension': 'ROWS',
    'valueInputOption': 'USER_ENTERED'
}

DATE_FORMAT: str = "%Y/%m/%d %H:%M:%S"
