from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject
from app.schemas import CharityProjectUpdate


class CRUDCharityProject(CRUDBase):
    """CRUD для целевых проектов."""

    async def get_open_projects(
        self,
        session: AsyncSession,
    ) -> list[CharityProject]:
        """Получить все открытые проекты."""
        query = select(CharityProject).where(
            CharityProject.fully_invested.is_(False)
        ).order_by(CharityProject.create_date)

        result = await session.execute(query)
        return list(result.scalars().all())

    async def get_project_by_name(
        self,
        name: str,
        session: AsyncSession,
    ) -> CharityProject | None:
        """Получить проект по имени."""
        query = select(CharityProject).where(CharityProject.name == name)
        result = await session.execute(query)
        return result.scalars().first()

    async def remove(
        self,
        db_obj: CharityProject,
        session: AsyncSession,
    ) -> CharityProject:
        """Универсальный метод для удаления записи."""
        await session.delete(db_obj)
        await session.commit()
        return db_obj

    async def update(
        self,
        db_obj: CharityProject,
        obj_in: CharityProjectUpdate,
        session: AsyncSession,
    ) -> CharityProject:
        """Универсальный метод для обновления записи."""
        update_data = obj_in.model_dump(exclude_unset=True)

        for field, value in update_data.items():
            setattr(db_obj, field, value)

        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def get_projects_by_completion_rate(
        self,
        session: AsyncSession,
    ) -> list[dict]:
        """
        Возвращает закрытые проекты, отсортированные по скорости сбора средств.
        """
        result = await session.execute(
            select(CharityProject).where(
                CharityProject.fully_invested.is_(True)
            )
        )
        projects = result.scalars().all()

        projects_with_duration = []
        for project in projects:
            # Вычисляем разницу
            delta = project.close_date - project.create_date

            projects_with_duration.append({
                "id": project.id,
                "name": project.name,
                "duration": str(delta),
                "duration_days": delta.days,
                "description": project.description,
                "full_amount": project.full_amount,
                "invested_amount": project.invested_amount,
                "create_date": project.create_date,
                "close_date": project.close_date,
            })

        projects_with_duration.sort(
            key=lambda x: x["duration_days"]  # type: ignore
        )

        return projects_with_duration  # type: ignore


charity_project_crud = CRUDCharityProject(CharityProject)
