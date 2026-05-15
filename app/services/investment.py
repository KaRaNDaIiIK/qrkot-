from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.charity_project import charity_project_crud
from app.crud.donation import donation_crud


async def invest(
    session: AsyncSession,
) -> None:
    """Распределяет неинвестированные средства по открытым проектам."""
    open_projects = await charity_project_crud.get_open_projects(session)
    donations = await donation_crud.get_not_fully_invested(session)

    p_idx, d_idx = 0, 0
    p_len = len(open_projects)
    d_len = len(donations)

    while p_idx < p_len and d_idx < d_len:
        project = open_projects[p_idx]
        donation = donations[d_idx]

        needed = project.full_amount - project.invested_amount
        available = donation.full_amount - donation.invested_amount
        to_invest = min(needed, available)

        project.invested_amount += to_invest
        donation.invested_amount += to_invest

        if project.invested_amount >= project.full_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
            p_idx += 1

        if donation.invested_amount >= donation.full_amount:
            donation.fully_invested = True
            donation.close_date = datetime.now()
            d_idx += 1

    await session.commit()
