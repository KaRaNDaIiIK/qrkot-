import logging
from datetime import datetime

from aiogoogle import Aiogoogle

from app.core.config import settings
from app.services.constants import (
    SPREADSHEET_BODY,
    PERMISSIONS_BODY,
    TABLE_HEADERS,
    UPDATE_CONFIG,
    DATE_FORMAT
)


logger = logging.getLogger(__name__)


async def create_spreadsheets(wrapper_services: Aiogoogle) -> str:
    """Создает новую Google таблицу для отчета."""
    now_date_time = datetime.now().strftime(DATE_FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')

    spreadsheet_body = SPREADSHEET_BODY.copy()
    spreadsheet_body['properties']['title'] = (
        f'Отчёт по проектам на {now_date_time}'
    )
    spreadsheet_body['sheets'][0]['properties']['title'] = settings.sheet_name

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
    permissions_body = PERMISSIONS_BODY.copy()
    permissions_body['emailAddress'] = settings.email
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
    now_date_time = datetime.now().strftime(DATE_FORMAT)
    service = await wrapper_services.discover('sheets', 'v4')

    sheet_name = getattr(settings, 'sheet_name', 'Отчет')
    update_range = f"{sheet_name}!A1:E30"

    table_values = [row.copy() for row in TABLE_HEADERS]
    table_values[0][1] = now_date_time

    for idx, project in enumerate(projects, 1):
        new_row = [
            str(idx),
            project.get('name', ''),
            str(project.get('duration', '')),
            project.get('description', '')
        ]
        table_values.append(new_row)

    update_body = {
        'majorDimension': UPDATE_CONFIG['majorDimension'],
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
