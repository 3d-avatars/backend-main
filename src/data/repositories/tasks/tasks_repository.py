import uuid
from abc import ABC, abstractmethod
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities import TaskEntity


class TasksRepository(ABC):

    @abstractmethod
    async def get_tasks(
        self,
        session: AsyncSession = None,
    ) -> List[TaskEntity]:
        raise NotImplementedError

    @abstractmethod
    async def get_task(
        self,
        request_uuid: uuid.UUID,
        session: AsyncSession = None,
    ) -> Optional[TaskEntity]:
        raise NotImplementedError

    @abstractmethod
    async def create_task(
        self,
        task: TaskEntity,
        session: AsyncSession = None,
    ) -> TaskEntity:
        raise NotImplementedError

    @abstractmethod
    async def update_task(
        self,
        request_uuid: uuid.UUID,
        session: AsyncSession = None,
        **update_task_kwargs,
    ) -> Optional[TaskEntity]:
        raise NotImplementedError

    @abstractmethod
    async def delete_task(
        self,
        request_uuid: uuid.UUID,
        session: AsyncSession = None,
    ) -> Optional[TaskEntity]:
        raise NotImplementedError
