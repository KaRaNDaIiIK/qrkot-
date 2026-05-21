from typing import Annotated, Any, Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.core.user import (
    current_superuser,
    current_user,
    current_user_optional,
)
from app.crud import donation_crud
from app.models import User
from app.schemas import (
    DonationCreate,
    DonationDB,
    DonationShortDB,
)
from app.services.investment import invest


router = APIRouter()
SessionDep = Annotated[AsyncSession, Depends(get_async_session)]


@router.post(
    '/',
    response_model=DonationShortDB,
    response_model_exclude_none=True,
    summary='Сделать пожертвование',
)
async def create_donation(
    donation: DonationCreate,
    session: SessionDep,
    user: Annotated[Optional[User], Depends(current_user_optional)] = None,
) -> Any:
    """Создаёт пожертвование и автоматически распределяет средства проектам."""
    new_donation = await donation_crud.create(
        donation,
        session,
        user
    )
    await invest(session)
    await session.refresh(new_donation)
    return new_donation


@router.get(
    '/',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
    summary='Получить список всех пожертвований',
    dependencies=[Depends(current_superuser)],
)
async def get_all_donations(
    session: SessionDep,
) -> Any:
    """Возвращает список всех пожертвований. Только для суперюзеров."""
    donations = await donation_crud.get_multi(session)
    return donations


@router.get(
    '/my',
    response_model=list[DonationShortDB],
    response_model_exclude_none=True,
    summary='Получить список всех пожертвований пользователя',
)
async def get_my_donations(
    session: SessionDep,
    user: Annotated[User, Depends(current_user)],
):
    """
    Возвращает список всех пожертвований пользователя.
    Только для авторезированных.
    """
    donations = await donation_crud.get_by_user(
        session,
        user.id,
    )
    return donations
