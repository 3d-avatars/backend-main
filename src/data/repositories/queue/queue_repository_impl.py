import logging

from aio_pika import Message

from config import get_settings
from src.data.queue import AMQPChannelManager
from src.data.repositories.queue import QueueRepository

logger = logging.getLogger(__name__)


class QueueRepositoryImpl(QueueRepository):
    def __init__(self):
        self._channel_manager = AMQPChannelManager()

    async def push_message(self, message_body: str | bytes):
        if isinstance(message_body, str):
            message_body = message_body.encode('utf-8')

        async with self._channel_manager.get_channel() as push_channel:
            await push_channel.default_exchange.publish(
                message=Message(
                    body=message_body,
                ),
                routing_key=get_settings().RABBITMQ_TASKS_QUEUE,
            )
            logger.info(f"Pushed message {message_body} to a queue {get_settings().RABBITMQ_TASKS_QUEUE}")
