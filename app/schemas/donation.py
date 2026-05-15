from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DonationBase(BaseModel):
    """Базовая схема пожертвования."""

    full_amount: int = Field(..., gt=0)
    comment: Optional[str] = None

    model_config = ConfigDict(extra='forbid')


class DonationCreate(DonationBase):
    """Схема для создания пожертвования."""

    pass


class DonationDB(DonationBase):
    """Схема для ответа."""

    id: int
    invested_amount: int = 0
    fully_invested: bool = False
    create_date: datetime
    close_date: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class DonationShortDB(DonationBase):
    """Схема для ответа пользователю (без комментария)"""
    id: int
    create_date: datetime

    model_config = ConfigDict(from_attributes=True)
