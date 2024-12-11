import uuid
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import UploadFile

from src.domain.entities.task_entity import TaskStatus
from src.presentation.responses import CreateTaskResponse


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
    ) -> Optional[str]:
        raise NotImplementedError

    @abstractmethod
    async def create_task(
        self,
        task_source_file: UploadFile,
    ) -> CreateTaskResponse:
        raise NotImplementedError
