from sqlalchemy import CheckConstraint, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.db import InvestmentBase


class Donation(InvestmentBase):
    """Модель пожертвования.

     Поля:
    - comment: комментарий к пожертвованию
    - full_amount: сумма пожертвования
    - invested_amount: сколько уже распределено по проектам
    - fully_invested: полностью ли распределено пожертвование
    - create_date: дата пожертвования
    - close_date: дата полного распределения средств.
    - user_id: ID пользователя (null для анонимных пожертвований)
    """

    __table_args__ = (
        CheckConstraint('full_amount > 0', name='full_amount_positive'),
    )

    comment: Mapped[str] = mapped_column(
        Text,
        nullable=True,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('user.id'),
        nullable=True
    )

    def __repr__(self) -> str:
        """Возвращает формальное строковое представление пожертвования."""
        return (
            f"<Donation(id={self.id}, amount={self.full_amount}, "
            f"invested={self.invested_amount}, "
            f"closed={self.fully_invested})>"
        )

    def __str__(self) -> str:
        """Возвращает пользовательское представление пожертвования."""
        remaining = self.full_amount - self.invested_amount
        if self.fully_invested:
            status = "Полностью распределено"
        else:
            status = f"Осталось распределить: {remaining}"
        return f"Пожертвование: {self.full_amount} руб.\nСтатус: {status}"
