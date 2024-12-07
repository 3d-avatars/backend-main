import logging
import uuid

from fastapi import Depends, UploadFile

from src.data.repositories.queue import QueueRepository
from src.data.repositories.queue.queue_repository_impl import QueueRepositoryImpl
from src.data.repositories.tasks import TasksRepository, TasksRepositoryImpl
from src.domain.entities import TaskEntity
from src.domain.entities.task_entity import TaskStatus
from src.domain.services.task_controller import TaskController

logger = logging.getLogger(__name__)


class TaskControllerImpl(TaskController):

    def __init__(
        self,
        task_repository: TasksRepository = Depends(TasksRepositoryImpl),
        task_queue: QueueRepository = Depends(QueueRepositoryImpl),
    ):
        self.task_repository = task_repository
        self.task_queue = task_queue

    async def get_task_status(
        self,
        task_request_uuid: uuid.UUID
    ) -> TaskStatus:
        task = await self.task_repository.get_task(request_uuid=task_request_uuid)
        return task.status

    async def get_task_result(
        self,
        task_request_uuid: uuid.UUID
    ) -> str:
        task = await self.task_repository.get_task(request_uuid=task_request_uuid)
        return task.result_file_path

    async def create_task(
        self,
        task_source_file: UploadFile,
    ) -> TaskEntity:
        request_uuid = uuid.uuid4()
        task = await self.task_repository.get_task(
            request_uuid=request_uuid,
        )

        if task is not None:
            return TaskEntity(
                request_uuid=task.request_uuid,
                source_file_path=task.source_file_path,
                result_file_path=task.result_file_path,
                status=task.status,
            )

        # TODO: Load source to blob storage and get source url
        source_file_path = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        task_entity = TaskEntity(
            request_uuid=request_uuid,
            source_file_path=source_file_path,
            result_file_path="",
            status=TaskStatus.INITIAL
        )

        new_task = await self.task_repository.create_task(task=task_entity)

        await self.task_queue.push_message(
            new_task.model_dump_json()
        )

        new_task = await self.task_repository.update_task(
            request_uuid=request_uuid,
            status=TaskStatus.IN_PROGRESS
        )

        return new_task
