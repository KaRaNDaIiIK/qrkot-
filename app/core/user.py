from typing import Annotated, Optional, Union
from fastapi import Depends, Request
from fastapi_users import (
    BaseUserManager,
    FastAPIUsers,
    IntegerIDMixin,
    InvalidPasswordException,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.db import get_async_session
from app.models import User
from app.schemas import UserCreate


async def get_user_db(
    session: Annotated[AsyncSession, Depends(get_async_session)]
):
    """Асинхронный контекстный менеджер для получения сессии пользователя."""
    yield SQLAlchemyUserDatabase(session, User)

bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')


def get_jwt_strategy() -> JWTStrategy:
    """Создает JWT стратегию аутентификации."""
    return JWTStrategy(secret=settings.secret, lifetime_seconds=3600)


auth_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)


class UserManager(IntegerIDMixin, BaseUserManager[User, int]):

    """класс пользователя с валидацией."""
    async def validate_password(  # type: ignore
        self,
        password: str,
        user: Union[UserCreate, User],  # type: ignore
    ) -> None:
        """
        Валидация пользователя.
        Вернет None в случае успеха.
        """
        if len(password) < 3:
            error = 'Пароль должен содержать не менее 3 символов'
            raise InvalidPasswordException(
                reason=error
            )
        if user.email in password:
            error = 'Пароль не может содержать ваш email'
            raise InvalidPasswordException(
                reason=error
            )

    async def on_after_register(
            self, user: User, request: Optional[Request] = None
    ):
        """
        Метод, описывающий действия после успешной регистрации пользователя.
        """
        print(f'Пользователь {user.email} зарегистрирован.')


async def get_user_manager(user_db=Depends(get_user_db)):
    """Корутина, возвращающая объект класса UserManager."""
    yield UserManager(user_db)


fastapi_users = FastAPIUsers[User, int](
    get_user_manager,
    [auth_backend],
)

current_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)
current_user_optional = fastapi_users.current_user(active=True, optional=True)
