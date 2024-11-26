import asyncio
import json

from config import get_settings
from src.queue.amqp import AMQPChannelManager
from src.repositories import AbstractRepository, TaskRepository
from src.enums import TaskStatus

from aio_pika.message import AbstractIncomingMessage


class Worker:
    def __init__(self):
        self._channel_manager = AMQPChannelManager()
        self._task_repository: AbstractRepository = TaskRepository()

    async def run(self):

        await self._channel_manager.refresh()

        async with self._channel_manager.get_channel() as channel:

            queue = await channel.declare_queue(get_settings().RABBITMQ_TASKS_QUEUE)

            try:
                await queue.consume(self.handle_task_callback, no_ack=False)
                await asyncio.get_running_loop().create_future()
            except KeyboardInterrupt:
                await self._channel_manager.prune()

    # TODO: make norm handle
    async def handle_task_callback(self, message: AbstractIncomingMessage) -> None:

        decode_body = json.loads(message.body.decode())
        task_id = decode_body['task_id']

        await self._task_repository.update(task_id=task_id, state=TaskStatus.PROCESSING)

        # TODO: generate s3 url
        result_file_path = decode_body['source_file_path']

        await self._task_repository.update(task_id=task_id, result_file_path=result_file_path, state=TaskStatus.SUCCESS)

        await message.ack()


def get_worker():
    return Worker()
