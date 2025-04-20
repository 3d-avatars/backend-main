import asyncio
import logging

from aio_pika.abc import AbstractIncomingMessage
from pydantic import ValidationError
from src.data.message_broker import AMQPChannelManager

from config import get_settings
from src.data.repositories import MeshMetadataRepository
from src.data.repositories import MeshMetadataRepositoryImpl
from src.data.repositories import MinioMetadataRepository
from src.data.repositories import MinioMetadataRepositoryImpl
from src.data.repositories import TasksRepository
from src.data.repositories import TasksRepositoryImpl
from src.domain.entities.task_entity import TaskProgressEntity
from src.domain.entities.task_entity import TaskResultEntity
from src.domain.entities.task_entity import TaskStatus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Worker:
    def __init__(self):
        self.channel_manager = AMQPChannelManager()
        self.task_repository: TasksRepository = TasksRepositoryImpl()
        self.minio_metadata_repository: MinioMetadataRepository = MinioMetadataRepositoryImpl()
        self.mesh_metadata_repository: MeshMetadataRepository = MeshMetadataRepositoryImpl()

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
        decoded_message = message.body.decode()

        try:
            decoded_task = TaskProgressEntity.model_validate_json(decoded_message)
            logger.error(f"Received task progress entity {decoded_task}")

        except ValidationError:
            try:
                decoded_task = TaskResultEntity.model_validate_json(decoded_message)
                logger.error(f"Received task result entity {decoded_task}")

            except ValidationError:
                logger.error(f"Failed to validate message {decoded_message}")
                return

        if isinstance(decoded_task, TaskProgressEntity):
            await self.task_repository.update_task(
                request_uuid=decoded_task.request_uuid,
                status=decoded_task.status,
            )
            logger.info(f"Updated task status {decoded_task.request_uuid} to {decoded_task.status}")

        elif isinstance(decoded_task, TaskResultEntity):
            minio_metadata = await self.minio_metadata_repository.create_metadata(
                bucket=decoded_task.minio_metadata.bucket,
                file_name=decoded_task.minio_metadata.file_name,
            )
            mesh_metadata = await self.mesh_metadata_repository.create_metadata(
                skin_color_hex=decoded_task.mesh_metadata.skin_color_hex,
            )

            await self.task_repository.update_task(
                request_uuid=decoded_task.request_uuid,
                status=TaskStatus.SUCCESS,
                result_file_metadata_id=minio_metadata.id,
                mesh_metadata_id=mesh_metadata.id,
            )
            logger.info(f"Updated task status {decoded_task.request_uuid} to SUCCESS")

        await message.ack()


def get_worker():
    return Worker()
