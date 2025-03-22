from fastapi import APIRouter

from config import get_settings
from src.presentation.routes.authorization_router import authorization_router
from src.presentation.routes.task_router import task_router
from src.presentation.routes.user_info_router import user_info_router


def get_apps_router():
    router = APIRouter(
        prefix=get_settings().PATH_PREFIX
    )
    router.include_router(authorization_router)
    router.include_router(task_router)
    router.include_router(user_info_router)

    return router
