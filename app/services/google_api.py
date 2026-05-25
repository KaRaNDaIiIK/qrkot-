import logging
from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings


logger = logging.getLogger(__name__)
FORMAT = "%Y/%m/%d %H:%M:%S"


async def create_spreadsheets(wrapper_services: Aiogoogle) -> str:
    """Создает новую Google таблицу для отчета."""
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')

    spreadsheet_body = {
        'properties': {
            'title': f'Отчёт по проектам на {now_date_time}',
            'locale': 'ru_RU'
        },
        'sheets': [{
            'properties': {
                'sheetType': 'GRID',
                'sheetId': 0,
                'title': settings.sheet_name,
                'gridProperties': {
                    'rowCount': 100,
                    'columnCount': 11
                }
            }
        }]
    }

    response = await wrapper_services.as_service_account(
        service.spreadsheets.create(
            json=spreadsheet_body  # type: ignore[call-arg]
        )
    )
    spreadsheet_id = response['spreadsheetId']  # type: ignore
    return spreadsheet_id


async def set_user_permissions(
    spreadsheet_id: str,
    wrapper_services: Aiogoogle
) -> None:
    """Выдает права на редактирование таблицы пользователю из настроек."""
    permissions_body = {
        'type': 'user',
        'role': 'writer',
        'emailAddress': settings.email
    }
    service = await wrapper_services.discover('drive', 'v3')

    await wrapper_services.as_service_account(
        service.permissions.create(
            fileId=spreadsheet_id,  # type: ignore[call-arg]
            json=permissions_body,  # type: ignore[call-arg]
            fields="id"  # type: ignore[call-arg]
        )
    )


async def update_spreadsheets_value(
    spreadsheet_id: str,
    projects: list,
    wrapper_services: Aiogoogle
) -> None:
    """Обновляет данные в Google таблице."""
    logger.info(f"Начало обновления таблицы {spreadsheet_id}")
    logger.info(f"Количество проектов для записи: {len(projects)}")
    now_date_time = datetime.now().strftime(FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')

    sheet_name = getattr(settings, 'sheet_name', 'Отчет')
    update_range = f"{sheet_name}!A1:E30"

    table_values = [
        ['Отчёт от', now_date_time],
        ['Топ проектов по скорости закрытия'],
        ['№', 'Название проекта', 'Время сбора', 'Описание']
    ]

    for idx, project in enumerate(projects, 1):
        new_row = [
            str(idx),
            project.get('name', ''),
            str(project.get('duration', '')),
            project.get('description', '')
        ]
        table_values.append(new_row)

    update_body = {
        'majorDimension': 'ROWS',
        'values': table_values
    }

    request = service.spreadsheets.values.update(  # type: ignore
        spreadsheetId=spreadsheet_id,  # type: ignore
        range=update_range,  # type: ignore
        valueInputOption='USER_ENTERED',  # type: ignore
        json=update_body  # type: ignore
    )
    await wrapper_services.as_service_account(request)

    logger.info(f"Таблица {spreadsheet_id} успешно обновлена")
