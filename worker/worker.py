import asyncio

from aio_pika.abc import AbstractIncomingMessage

from config import get_settings
from src.data.queue import AMQPChannelManager
from src.data.repositories.tasks import TasksRepository, TasksRepositoryImpl
from src.domain.entities import TaskEntity
from src.domain.entities.task_entity import TaskStatus


class Worker:
    def __init__(self):
        self._channel_manager = AMQPChannelManager()
        self._task_repository: TasksRepository = TasksRepositoryImpl()

    async def run(self):
        await self._channel_manager.refresh()

        async with self._channel_manager.get_channel() as channel:
            queue = await channel.declare_queue(get_settings().RABBITMQ_TASKS_RESULTS_QUEUE)

            try:
                await queue.consume(self.handle_task_callback, no_ack=False)
                await asyncio.get_running_loop().create_future()
            except KeyboardInterrupt:
                await self._channel_manager.dispose()

    # TODO: make norm handle
    async def handle_task_callback(self, message: AbstractIncomingMessage) -> None:
        decoded_task = TaskEntity.model_validate_json(message.body.decode())

        # TODO: generate s3 url
        await self._task_repository.update_task(
            request_uuid=decoded_task.request_uuid,
            status=TaskStatus.SUCCESS
        )
        await message.ack()


def get_worker():
    return Worker()
