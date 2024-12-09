import asyncio
import logging

from aio_pika.abc import AbstractIncomingMessage

from config import get_settings
from src.data.queue import AMQPChannelManager
from src.data.repositories.minio_metadata import MinioMetadataRepository, MinioMetadataRepositoryImpl
from src.data.repositories.tasks import TasksRepository, TasksRepositoryImpl
from src.domain.entities import TaskEntity
from src.domain.entities.task_entity import TaskStatus

logger = logging.getLogger(__name__)

class Worker:
    def __init__(self):
        self.channel_manager = AMQPChannelManager()
        self.task_repository: TasksRepository = TasksRepositoryImpl()
        self.minio_metadata_repository: MinioMetadataRepository = MinioMetadataRepositoryImpl()

    async def run(self):
        await self.channel_manager.refresh()

        async with self.channel_manager.get_channel() as channel:
            queue = await channel.declare_queue(get_settings().RABBITMQ_TASKS_RESULTS_QUEUE)

            try:
                await queue.consume(self.handle_task_callback, no_ack=False)
                await asyncio.get_running_loop().create_future()
            except KeyboardInterrupt:
                await self.channel_manager.dispose()

    async def handle_task_callback(self, message: AbstractIncomingMessage) -> None:
        decoded_task = TaskEntity.model_validate_json(message.body.decode())
        result_file_metadata = decoded_task.result_file_metadata

        if decoded_task.status == TaskStatus.IN_PROGRESS:
            await self.task_repository.update_task(
                request_uuid=decoded_task.request_uuid,
                status=TaskStatus.IN_PROGRESS
            )
            logger.info(f"Updated task status {decoded_task.request_uuid} to PENDING")
        elif result_file_metadata:
            metadata = await self.minio_metadata_repository.create_metadata(
                bucket=result_file_metadata.bucket,
                file_name=result_file_metadata.file_name,
            )
            await self.task_repository.update_task(
                request_uuid=decoded_task.request_uuid,
                result_file_metadata_id=metadata.id,
                status=TaskStatus.SUCCESS
            )
            logger.info(f"Updated task status {decoded_task.request_uuid} to SUCCESS")
        else:
            logger.error(f"Failed to retrieve result file metadata from {decoded_task}")
            await self.task_repository.update_task(
                request_uuid=decoded_task.request_uuid,
                status=TaskStatus.FAILED,
            )

        await message.ack()


def get_worker():
    return Worker()
