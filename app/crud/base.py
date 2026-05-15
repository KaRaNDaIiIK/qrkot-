from typing import Any, Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class CRUDBase:
    """Базовый класс для CRUD операций."""

    def __init__(self, model):
        self.model = model

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ):
        """Уневерсальный метод для получения объекта по id."""
        db_obj = await session.execute(
            select(self.model).where(self.model.id == obj_id)
        )
        return db_obj.scalars().first()

    async def get_multi(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Any]:
        """Универсальный метод для получения всех объектов заданной модели."""
        db_objs = await session.execute(
            select(self.model).offset(skip).limit(limit)
        )
        return db_objs.scalars().all()

    async def create(
        self,
        obj_in,
        session: AsyncSession,
    ):
        """Универсальный метод для добавления записи в базу."""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj
