import logging

from fastapi import APIRouter

from config import get_settings
from .task_router import router as task_route


def get_apps_router():

    router = APIRouter(
        prefix=get_settings().PATH_PREFIX
    )

    router.include_router(task_route)

    return router
