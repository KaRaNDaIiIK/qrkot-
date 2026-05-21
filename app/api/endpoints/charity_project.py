from datetime import datetime
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.validators import (
    check_project_amount_valid,
    check_project_can_be_deleted,
    check_project_exists,
    check_project_name_duplicate,
    check_project_not_closed,
)
from app.core.db import get_async_session
from app.core.user import current_superuser
from app.crud import charity_project_crud
from app.schemas import (
    CharityProjectCreate,
    CharityProjectDB,
    CharityProjectUpdate,
)
from app.services.investment import invest


router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.post(
    '/',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    summary='Создать новый целевой проект',
    dependencies=[Depends(current_superuser)],
)
async def create_charity_project(
    project: CharityProjectCreate,
    session: SessionDep,
) -> Any:
    """
    Создаёт новый проект и автоматически распределяет пожертвования.
    Только для суперюзеров.
    """
    await check_project_name_duplicate(project.name, session)

    new_project = await charity_project_crud.create(
        project,
        session,
    )

    await invest(session)

    await session.refresh(new_project)

    return new_project


@router.get(
    '/',
    response_model=list[CharityProjectDB],
    response_model_exclude_none=True,
    summary='Получить список всех проектов',
)
async def get_all_projects(
    session: SessionDep,
) -> Any:
    """Возвращает список всех целевых проектов. Для всех."""
    projects = await charity_project_crud.get_multi(session)
    return projects


@router.patch(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    summary='Обновить целевой проект',
    dependencies=[Depends(current_superuser)],
)
async def update_charity_project(
    project_id: int,
    project_update: CharityProjectUpdate,
    session: SessionDep,
) -> Any:
    """Обновляет целевой проект. Только для суперюзеров."""
    project = await check_project_exists(project_id, session)

    await check_project_not_closed(project)
    await check_project_amount_valid(project, project_update.full_amount)

    if project_update.name and project_update.name != project.name:
        await check_project_name_duplicate(project_update.name, session)

    updated_project = await charity_project_crud.update(
        project, project_update, session
    )

    if updated_project.invested_amount >= updated_project.full_amount:
        updated_project.fully_invested = True
        updated_project.close_date = datetime.now()
        await session.commit()
        await session.refresh(updated_project)

    return updated_project


@router.delete(
    '/{project_id}',
    response_model=CharityProjectDB,
    response_model_exclude_none=True,
    summary='Удалить целевой проект',
    dependencies=[Depends(current_superuser)],
)
async def delete_charity_project(
    project_id: int,
    session: SessionDep,
) -> Any:
    """
    Удаляет целевой проект (только незакрытый и без инвестиций).
    Только для суперюзеров.
    """
    project = await check_project_exists(project_id, session)

    await check_project_can_be_deleted(project)

    deleted_project = await charity_project_crud.remove(project, session)
    return deleted_project
