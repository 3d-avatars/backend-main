from contextlib import asynccontextmanager
from typing import Optional

import aio_pika
from aio_pika.abc import AbstractRobustChannel
from aio_pika.abc import AbstractRobustConnection

from config import get_settings


class AMQPChannelManager:

    def __init__(self) -> None:
        self.connect_refresh: bool = True
        self._connection: Optional[AbstractRobustConnection] = None

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(AMQPChannelManager, cls).__new__(cls)
            cls.instance.connect_refresh = True

        return cls.instance  # noqa

    @classmethod
    async def dispose(cls) -> None:
        if not hasattr(cls, 'instance'):
            return

        await cls.instance._connection.close()
        delattr(cls.instance)

    @asynccontextmanager
    async def get_channel(self) -> AbstractRobustChannel:
        if self.connect_refresh:
            await self.refresh()
            self.connect_refresh = False

        channel = await self._connection.channel()
        yield channel
        await channel.close()

    async def refresh(self):
        settings = get_settings()

        self._connection = await aio_pika.connect_robust(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            login=settings.RABBITMQ_DEFAULT_USER,
            password=settings.RABBITMQ_DEFAULT_PASSWORD,
        )

        async with self._connection.channel() as declare_channel:
            await declare_channel.set_qos(prefetch_count=1)
            await declare_channel.declare_queue(
                name=settings.RABBITMQ_TASKS_QUEUE,
            )
