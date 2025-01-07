import uuid
from abc import ABC, abstractmethod
from typing import Optional

from fastapi import UploadFile

from src.presentation.responses import CreateTaskResponse
from src.presentation.responses import GetTaskResultResponse
from src.presentation.responses import GetTaskStatusResponse


class TaskController(ABC):

    @abstractmethod
    async def get_task_status(
        self,
        task_request_uuid: uuid.UUID,
    ) -> Optional[GetTaskStatusResponse]:
        raise NotImplementedError

    @abstractmethod
    async def get_task_result(
        self,
        task_request_uuid: uuid.UUID,
    ) -> Optional[GetTaskResultResponse]:
        raise NotImplementedError

    @abstractmethod
    async def create_task(
        self,
        user_id: int,
        source_file: UploadFile,
    ) -> CreateTaskResponse:
        raise NotImplementedError
