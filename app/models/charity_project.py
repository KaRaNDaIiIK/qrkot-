from sqlalchemy import CheckConstraint, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import InvestmentBase


class CharityProject(InvestmentBase):
    """Модель целевого проекта.

     Поля:
    - name: название проекта
    - description: описание проекта
    - full_amount: сколько нужно собрать
    - invested_amount: сколько уже собрали
    - fully_invested: закрыт ли проект
    - create_date: дата создания
    - close_date: дата закрытия.
    """

    __table_args__ = (
        CheckConstraint('full_amount > 0', name='full_amount_positive'),
        CheckConstraint('length(name) >= 5', name='name_min_length'),
        CheckConstraint('length(description) >= 10', name='desc_min_length'),
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    def __repr__(self) -> str:
        """Возвращает формальное строковое представление проекта."""
        return (
            f"<CharityProject(id={self.id}, name='{self.name}', "
            f"full_amount={self.full_amount}, "
            f"invested={self.invested_amount}, "
            f"closed={self.fully_invested})>"
        )

    def __str__(self) -> str:
        """Возвращает пользовательское строковое представление проекта."""
        status = "Закрыт" if self.fully_invested else "Открыт"
        return (
            f"Проект: {self.name}\n"
            f"Собрано: {self.invested_amount} из {self.full_amount}\n"
            f"Статус: {status}"
        )
