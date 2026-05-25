from aiogoogle import Aiogoogle
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.core.google_client import get_service
from app.core.user import current_superuser
from app.crud.charity_project import charity_project_crud
from app.services.google_api import update_spreadsheets_value


router = APIRouter()


@router.post(
    '/',
    response_model=dict,
    summary='Получить отчет по проектам',
    dependencies=[Depends(current_superuser)],
)
async def get_report(
    session: AsyncSession = Depends(get_async_session),
    wrapper_services: Aiogoogle = Depends(get_service)
):
    """
    Формирует отчет в Google Sheets о закрытых проектах.
    Только для суперюзеров.
    """

    projects = await charity_project_crud.get_projects_by_completion_rate(
        session
    )

    await update_spreadsheets_value(
        settings.spreadsheet_id,  # type: ignore
        projects,
        wrapper_services
    )

    return {
        "status": "success",
        "message": "Отчет успешно создан",
        "url": (
            f"https://docs.google.com/spreadsheets/d/{settings.spreadsheet_id}"
        ),
        "projects_count": len(projects),
        "projects": projects
    }
