from src.queue.base_queue import AbstractTaskQueue
from aio_pika import Message

from config import get_settings

from src.queue.amqp.connection import AMQPChannelManager


class AMQPQueue(AbstractTaskQueue):
    def __init__(self):
        self._channel_manager = AMQPChannelManager()

    async def push_message(self, message_body: str | bytes):
        if isinstance(message_body, str):
            message_body = message_body.encode('utf-8')

        async with self._channel_manager.get_channel() as push_channel:
            await push_channel.default_exchange.publish(
                Message(message_body),
                routing_key=get_settings().RABBITMQ_TASKS_QUEUE,
            )

    async def retrieve_message(self):
        raise NotImplementedError
