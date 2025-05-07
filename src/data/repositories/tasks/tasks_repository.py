import uuid
from abc import ABC
from abc import abstractmethod
from typing import List
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database.tables import TaskTable


class TasksRepository(ABC):

    @abstractmethod
    async def get_tasks(
        self,
        session: AsyncSession = None,
    ) -> List[TaskTable]:
        raise NotImplementedError

    @abstractmethod
    async def get_tasks_by_user_id(
        self,
        user_id: int,
        session: AsyncSession = None,
    ) -> List[TaskTable]:
        raise NotImplementedError

    @abstractmethod
    async def get_completed_tasks_by_user_id(
        self,
        user_id: int,
        session: AsyncSession = None,
    ) -> List[TaskTable]:
        raise NotImplementedError

    @abstractmethod
    async def get_first_task_of_user(
        self,
        user_id: int,
        session: AsyncSession = None,
    ) -> Optional[TaskTable]:
        raise NotImplementedError

    @abstractmethod
    async def get_task_by_request_uuid(
        self,
        request_uuid: uuid.UUID,
        session: AsyncSession = None,
    ) -> Optional[TaskTable]:
        raise NotImplementedError

    @abstractmethod
    async def create_task(
        self,
        task: TaskTable,
        session: AsyncSession = None,
    ) -> TaskTable:
        raise NotImplementedError

    @abstractmethod
    async def update_task(
        self,
        request_uuid: uuid.UUID,
        session: AsyncSession = None,
        **update_task_kwargs,
    ) -> Optional[TaskTable]:
        raise NotImplementedError

    @abstractmethod
    async def delete_task(
        self,
        request_uuid: uuid.UUID,
        session: AsyncSession = None,
    ) -> Optional[TaskTable]:
        raise NotImplementedError
