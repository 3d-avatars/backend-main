from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from src.presentation.routes import get_apps_router
from src.data.message_broker.amqp_channel_manager import AMQPChannelManager

settings = get_settings()


async def prune_application_dependencies():
    await AMQPChannelManager.dispose()


def get_application() -> FastAPI:
    application = FastAPI(
        title="3D Avatar API (1.0)",
        debug=True,
        version="0.0.1",
    )

    origins = [
        "http://130.193.48.248:5173",
        "http://localhost:5173",
    ]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(get_apps_router())
    return application


app = get_application()
