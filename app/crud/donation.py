from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models.donation import Donation


class CRUDDonation(CRUDBase):
    """CRUD для пожертвований."""

    async def get_not_fully_invested(
        self,
        session: AsyncSession,
    ) -> list[Donation]:
        """Получить пожертвования с нераспределёнными средствами."""
        query = select(Donation).where(
            Donation.fully_invested.is_(False)
        ).order_by(Donation.create_date)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_by_user(
        self,
        session: AsyncSession,
        user_id: int,
    ) -> list[Donation]:
        """Получить пожертвования пользователя."""
        query = select(Donation).where(Donation.user_id == user_id)
        result = await session.execute(query)
        return list(result.scalars().all())


donation_crud = CRUDDonation(Donation)
