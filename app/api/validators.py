from http import HTTPStatus

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.models.charity_project import CharityProject


async def check_project_name_duplicate(
    name: str,
    session: AsyncSession,
) -> None:
    """Проверяет, что имя проекта уникально."""
    project = await charity_project_crud.get_project_by_name(name, session)
    if project is not None:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Проект с таким именем уже существует!'
        )


async def check_project_exists(
    project_id: int,
    session: AsyncSession,
) -> CharityProject:
    """Проверяет существование проекта, возвращает объект или 404."""
    project = await charity_project_crud.get(project_id, session)
    if project is None:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND,
            detail='Проект не найден!'
        )
    return project


async def check_project_not_closed(
    project: CharityProject,
) -> None:
    """Проверяет, что проект не закрыт."""
    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нельзя изменять закрытый проект!'
        )


async def check_project_can_be_deleted(
    project: CharityProject,
) -> None:
    """Проверяет, что проект можно удалить."""
    if project.fully_invested:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нельзя удалять закрытый проект!'
        )

    if project.invested_amount > 0:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нельзя удалять проект с уже внесёнными средствами!'
        )


async def check_project_amount_valid(
    project: CharityProject,
    full_amount: int | None,
) -> None:
    """Проверяет, что новое значение не меньше уже внесённой суммы."""
    if full_amount is not None and full_amount < project.invested_amount:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail='Нельзя установить сумму меньше уже внесённой!'
        )
