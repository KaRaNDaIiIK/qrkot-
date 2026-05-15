from datetime import datetime
from typing import AsyncGenerator

from sqlalchemy import Boolean, DateTime, Integer
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    declared_attr,
    mapped_column,
)

from app.core.config import settings


class Base(DeclarativeBase):
    pass


class CommonMixin:
    """Общий миксин для всех моделей."""

    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()  # type: ignore

    id: Mapped[int] = mapped_column(Integer, primary_key=True)


engine = create_async_engine(
    settings.database_url
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    expire_on_commit=False
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Генератор асинхронных сессий для работы с базой данных."""
    async with AsyncSessionLocal() as async_session:
        yield async_session


class InvestmentBase(CommonMixin, Base):
    """Абстрактная модель для инвестиционных объектов проекта."""
    __abstract__ = True

    full_amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )
    invested_amount: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        index=True,
    )
    fully_invested: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )
    create_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        index=True,
    )
    close_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=True,
    )
