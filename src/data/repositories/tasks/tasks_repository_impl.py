import logging
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database.connection.session_provider_mixin import SessionProviderMixin
from src.data.database.tables.task_table import TaskTable
from src.data.repositories.tasks.tasks_repository import TasksRepository

logger = logging.getLogger(__name__)


class TasksRepositoryImpl(TasksRepository, SessionProviderMixin):

    @SessionProviderMixin._session_provider
    async def get_tasks(
        self,
        session: AsyncSession = None,
    ) -> List[TaskTable]:

        task_query = select(TaskTable)
        result = list(
            (await session.execute(task_query)).scalars().all()
        )
        await session.commit()

        logger.info(f"Selected tasks {result}")
        return result

    @SessionProviderMixin._session_provider
    async def get_task(
        self,
        request_uuid: uuid.UUID,
        session: AsyncSession = None
    ) -> Optional[TaskTable]:
        task_query = select(TaskTable).where(TaskTable.request_uuid == request_uuid)
        result: Optional[TaskTable] = (await session.execute(task_query)).scalar()

        await session.commit()

        logger.info(f"Selected task {result}")
        return result

    @SessionProviderMixin._session_provider
    async def create_task(
        self,
        task: TaskTable,
        session: AsyncSession = None,
    ) -> TaskTable:
        session.add(task)
        await session.commit()

        logger.info(f"Created task {task}")
        return task

    @SessionProviderMixin._session_provider
    async def update_task(
        self,
        request_uuid: uuid.UUID,
        session: AsyncSession = None,
        **update_task_kwargs,
    ) -> Optional[TaskTable]:
        query = update(TaskTable).where(
            TaskTable.request_uuid == request_uuid,
        ).values(
            **update_task_kwargs,
        ).returning(TaskTable)

        update_result: Optional[TaskTable] = (await session.execute(query)).scalar()
        await session.commit()

        logger.info(f"Updated task {update_result}")
        return update_result

    @SessionProviderMixin._session_provider
    async def delete_task(
        self,
        request_uuid: uuid.UUID,
        session: AsyncSession = None,
    ) -> Optional[TaskTable]:
        result = self.get_task(request_uuid)
        if not result:
            return None

        query = delete(TaskTable).where(
            TaskTable.request_uuid == request_uuid
        ).returning(TaskTable)

        delete_result: Optional[TaskTable] = (await session.execute(query)).scalar()
        await session.commit()

        logger.info(f"Deleted task {delete_result}")
        return delete_result
