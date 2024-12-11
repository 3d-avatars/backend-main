from fastapi import FastAPI

from config import get_settings
from src.presentation.routes import get_apps_router
from src.data.queue.amqp_channel_manager import AMQPChannelManager

settings = get_settings()


async def prune_application_dependencies():
    await AMQPChannelManager.dispose()


def get_application() -> FastAPI:
    application = FastAPI(
        title="3D Avatar API (1.0)",
        debug=True,
        version="0.0.1",
    )

    application.include_router(get_apps_router())
    return application


app = get_application()
