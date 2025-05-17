import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

from config import get_settings

logger = logging.getLogger(__name__)


class SessionManager:

    @asynccontextmanager
    async def get_session(self):
        logger.info("Requesting database connection")
        async with self.session_maker() as session:
            try:
                logger.info("Acquired database connection")
                yield session
            finally:
                logger.info("Closing database connection")
                await session.close()

    def __init__(self) -> None:
        self.refresh()

    def __new__(cls):
        if not hasattr(cls, "instance"):
            logger.info("Creating new session manager instance")
            cls.instance = super(SessionManager, cls).__new__(cls)
        return cls.instance  # noqa

    def refresh(self) -> None:
        logger.info(f"Creating new database connection")
        self.engine = create_async_engine( # noqa
            get_settings().database_uri,
            pool_size=50,
            max_overflow=20,
            pool_timeout=30,
            pool_recycle=60,
            pool_pre_ping=True,
            echo=True,
        )
        self.session_maker = sessionmaker( # noqa
            self.engine,
            class_= AsyncSession,
            expire_on_commit=False
        )
