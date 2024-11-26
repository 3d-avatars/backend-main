import json
import logging
import uuid

from fastapi import Depends, UploadFile

from src.queue.base_queue import AbstractTaskQueue
from src.queue.amqp.amqp_queue import AMQPQueue
from src.repositories import AbstractRepository, TaskRepository
from src.services.base_service import BaseService
from src.schemas.task_schema import TaskFilter, TaskStateUpdateRequest


logger = logging.getLogger(__name__)


class TaskService(BaseService):

    def __init__(
            self,
            repository: AbstractRepository = Depends(TaskRepository),
            task_queue: AbstractTaskQueue = Depends(AMQPQueue),
    ):
        super().__init__(repository)
        self.task_queue = task_queue

    async def create(
            self,
            request_uuid: uuid.UUID,
            task_source_file: UploadFile,
    ):
        # TODO: Load source to blob storage and get source url
        source_file_path = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        task_request_uuid = (
            await self.repository.get(
                request_uuid=request_uuid,
            )
        ).first()

        if task_request_uuid is not None:
            return task_request_uuid

        # creating a record before starting 3D generation process
        new_task = await self.repository.create(
            request_uuid=request_uuid,
            source_file_path=source_file_path,
        )

        # Send to queue for start 3d generating
        await self.task_queue.push_message(
            json.dumps(
                {
                    "task_id": new_task.id,
                    "source_file_path": source_file_path,
                }
            )
        )

        return new_task

    async def update(
            self,
            task_id: int,
            task_info: TaskStateUpdateRequest,
    ):
        return await self.repository.update(
            task_id=task_id,
            **task_info.model_dump()
        )

    # TODO: delete also source and result files
    async def delete(self, task_id: int):
        return await self.repository.delete(
            task_id=task_id,
        )

    async def get_single(self, task_id: int):
        return await self.repository.get_single(
            task_id=task_id,
        )

    async def get(self, task_filter: TaskFilter):
        return await self.repository.get(**task_filter.model_dump(exclude_none=True, exclude_unset=True))
