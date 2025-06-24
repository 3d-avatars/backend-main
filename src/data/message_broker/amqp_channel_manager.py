import asyncio
import logging
from contextlib import asynccontextmanager
from typing import Optional

import aio_pika
from aio_pika.abc import AbstractRobustChannel
from aio_pika.abc import AbstractRobustConnection

from config import get_settings

logger = logging.getLogger(__name__)


class AMQPChannelManager:

    def __init__(self) -> None:
        self._connection: Optional[AbstractRobustConnection] = None
        self._lock = asyncio.Lock()
        self._channel: Optional[AbstractRobustChannel] = None

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(AMQPChannelManager, cls).__new__(cls)
        return cls.instance # noqa

    @classmethod
    async def dispose(cls) -> None:
        if not hasattr(cls, "instance"):
            return

        instance = cls.instance # noqa

        if instance._connection and not instance._connection.is_closed:
            await instance._connection.close()
            instance._connection = None
            instance._channel = None

    @asynccontextmanager
    async def get_channel(self) -> AbstractRobustChannel:
        await self.__ensure_connection()
        try:
            yield self._channel
        except Exception as e:
            logger.exception(f"Error in RabbitMQ channel manager: {e}")
            self._connection = None
            self._channel = None
            raise
        finally:
            logger.info(f"Closing RabbitMQ connection")
            await self._connection.close()

    async def __ensure_connection(self) -> None:
        if self._connection is None or self._connection.is_closed or self._channel is None or self._channel.is_closed:
            async with self._lock:
                if self._connection is None or self._connection.is_closed:
                    settings = get_settings()

                    if self._connection and not self._connection.is_closed:
                        await self._connection.close()

                    logger.info("Creating new RabbitMQ connection")
                    self._connection = await aio_pika.connect_robust(
                        host=settings.RABBITMQ_HOST,
                        port=settings.RABBITMQ_PORT,
                        login=settings.RABBITMQ_DEFAULT_USER,
                        password=settings.RABBITMQ_DEFAULT_PASSWORD,
                        heartbeat=60,
                    )

                if self._channel is None or self._channel.is_closed:
                    logger.info("Creating new RabbitMQ channel")
                    self._channel = await self._connection.channel()
                    await self._channel.set_qos(prefetch_count=1)

                    await self._channel.declare_queue(
                        name=settings.RABBITMQ_TASKS_QUEUE,
                        durable=True,
                    )
