from typing import Any, Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_async_session
from app.crud.donation import donation_crud
from app.schemas.donation import DonationCreate, DonationDB, DonationShortDB
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
) -> Any:
    """Создаёт пожертвование и автоматически распределяет средства проектам."""
    new_donation = await donation_crud.create(donation, session)

    await invest(session)

    await session.refresh(new_donation)

    return new_donation


@router.get(
    '/',
    response_model=list[DonationDB],
    response_model_exclude_none=True,
    summary='Получить список всех пожертвований',
)
async def get_all_donations(
    session: SessionDep,
) -> Any:
    """Возвращает список всех пожертвований."""
    donations = await donation_crud.get_multi(session)
    return donations
