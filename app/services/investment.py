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

    project_index, donation_index = 0, 0
    projects_count = len(open_projects)
    donations_count = len(donations)

    while project_index < projects_count and donation_index < donations_count:
        project = open_projects[project_index]
        donation = donations[donation_index]

        needed_amount = project.full_amount - project.invested_amount
        available_amount = donation.full_amount - donation.invested_amount
        amount_to_invest = min(needed_amount, available_amount)

        project.invested_amount += amount_to_invest
        donation.invested_amount += amount_to_invest

        if project.invested_amount >= project.full_amount:
            project.fully_invested = True
            project.close_date = datetime.now()
            project_index += 1

        if donation.invested_amount >= donation.full_amount:
            donation.fully_invested = True
            donation.close_date = datetime.now()
            donation_index += 1

    await session.commit()
