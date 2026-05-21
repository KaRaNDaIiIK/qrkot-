from fastapi import APIRouter
from fastapi.routing import APIRoute

from app.core.user import auth_backend, fastapi_users
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter()

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix='/auth/jwt',
    tags=['Аутентификация'],
)

router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['Аутентификация'],
)

users_router = fastapi_users.get_users_router(UserRead, UserUpdate)
users_router.routes = [
    route for route in users_router.routes
    if not (isinstance(route, APIRoute) and route.name == 'users:delete_user')
]

for route in users_router.routes:
    if isinstance(route, APIRoute):
        if route.name == 'users:current_user':
            route.summary = 'Текущий пользователь'
        elif route.name == 'users:patch_current_user':
            route.summary = 'Обновить текущего пользователя'
        elif route.name == 'users:user':
            route.summary = 'Получить пользователя по ID'
        elif route.name == 'users:patch_user':
            route.summary = 'Обновить пользователя по ID'

router.include_router(
    users_router,
    prefix='/users',
    tags=['Пользователи'],
)
