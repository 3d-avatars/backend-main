import uuid
from abc import ABC, abstractmethod

from fastapi import UploadFile

from src.domain.entities import TaskEntity
from src.domain.entities.task_entity import TaskStatus


class TaskController(ABC):

    @abstractmethod
    async def get_task_status(
        self,
        task_request_uuid: uuid.UUID,
    ) -> TaskStatus:
        raise NotImplementedError

    @abstractmethod
    async def get_task_result(
        self,
        task_request_uuid: uuid.UUID,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def create_task(
        self,
        task_source_file: UploadFile,
    ) -> TaskEntity:
        raise NotImplementedError
