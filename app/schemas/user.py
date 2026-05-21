from fastapi_users import schemas


class UserRead(schemas.BaseUser[int]):
    """Схема для чтения данных пользователя (ответ API)."""


class UserCreate(schemas.BaseUserCreate):
    """Схема для создания нового пользователя (запрос API)"""


class UserUpdate(schemas.BaseUserUpdate):
    """Схема для частичного обновления пользователя (запрос API)."""
