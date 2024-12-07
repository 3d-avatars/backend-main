import logging
import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy import update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database.connection.session_provider_mixin import SessionProviderMixin
from src.data.database.tables.task_table import TaskTable
from src.data.repositories.tasks.tasks_repository import TasksRepository
from src.domain.entities import TaskEntity

logger = logging.getLogger(__name__)


class TasksRepositoryImpl(TasksRepository, SessionProviderMixin):

    @SessionProviderMixin._session_provider
    async def get_tasks(
        self,
        session: AsyncSession = None,
    ) -> List[TaskEntity]:

        task_query = select(TaskTable)
        result = (await session.execute(task_query)).scalars().all()
        await session.commit()

        return list(
            map(
                lambda task: TaskEntity(
                    request_uuid=task.request_uuid,
                    source_file_path=task.source_file_path,
                    result_file_path=task.result_file_path,
                    status=task.status
                ),
                result,
            )
        )

    @SessionProviderMixin._session_provider
    async def get_task(
        self,
        request_uuid: uuid.UUID,
        session: AsyncSession = None
    ) -> Optional[TaskEntity]:
        task_query = select(TaskTable).where(TaskTable.request_uuid == request_uuid)
        result: Optional[TaskTable] = (await session.execute(task_query)).scalar()

        await session.commit()

        if not result:
            return None
        return TaskEntity(
            request_uuid=result.request_uuid,
            source_file_path=result.source_file_path,
            result_file_path=result.result_file_path,
            status=result.status,
        )

    @SessionProviderMixin._session_provider
    async def create_task(
        self,
        task: TaskEntity,
        session: AsyncSession = None,
    ) -> TaskEntity:
        new_task = TaskTable(
            request_uuid=task.request_uuid,
            source_file_path=task.source_file_path,
            result_file_path=task.result_file_path,
            status=task.status,
        )

        session.add(new_task)
        await session.commit()
        return task

    @SessionProviderMixin._session_provider
    async def update_task(
        self,
        request_uuid: uuid.UUID,
        session: AsyncSession = None,
        **update_task_kwargs,
    ) -> Optional[TaskEntity]:
        query = update(TaskTable).where(
            TaskTable.request_uuid == request_uuid,
        ).values(
            **update_task_kwargs,
        ).returning(TaskTable)

        update_result: Optional[TaskTable] = (await session.execute(query)).scalar()
        await session.commit()

        if not update_result:
            return None
        return TaskEntity(
            request_uuid=update_result.request_uuid,
            source_file_path=update_result.source_file_path,
            result_file_path=update_result.result_file_path,
            status=update_result.status,
        )

    @SessionProviderMixin._session_provider
    async def delete_task(
        self,
        request_uuid: uuid.UUID,
        session: AsyncSession = None,
    ) -> Optional[TaskEntity]:
        result = self.get_task(request_uuid)
        if not result:
            return None

        query = delete(TaskTable).where(
            TaskTable.request_uuid == request_uuid
        ).returning(TaskTable)

        delete_result: Optional[TaskTable] = (await session.execute(query)).scalar()
        await session.commit()

        if not delete_result:
            return None
        return TaskEntity(
            request_uuid=delete_result.request_uuid,
            source_file_path=delete_result.source_file_path,
            result_file_path=delete_result.result_file_path,
            status=delete_result.status
        )
