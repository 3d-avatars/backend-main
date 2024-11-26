import asyncio

import pika

import pika
import aio_pika
from contextlib import asynccontextmanager
from config import get_settings


class AMQPChannelManager:

    @classmethod
    async def prune(cls) -> None:
        if not hasattr(cls, 'instance'):
            return

        await cls.instance._connection.close()
        delattr(cls.instance)

    @asynccontextmanager
    async def get_channel(self):
        if self.connect_refresh:
            await self.refresh()
            self.connect_refresh = False

        channel = await self._connection.channel()
        yield channel
        await channel.close()

    def __init__(self) -> None:
        ...

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(AMQPChannelManager, cls).__new__(cls)
            cls.instance.connect_refresh = True

        return cls.instance  # noqa

    async def refresh(self):
        settings = get_settings()

        self._connection = await aio_pika.connect_robust(
            host=settings.RABBITMQ_HOST,
            port=settings.RABBITMQ_PORT,
            login=settings.RABBITMQ_DEFAULT_USER,
            password=settings.RABBITMQ_DEFAULT_PASSWORD,
        )

        async with self._connection.channel() as declare_channel:
            await declare_channel.declare_queue(
                name=settings.RABBITMQ_TASKS_QUEUE,
            )
