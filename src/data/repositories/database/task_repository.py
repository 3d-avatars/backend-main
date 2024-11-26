import logging
import uuid


from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, literal_column
from sqlalchemy import select

from src.repositories.mixins.session_provider_mixin import SessionProviderMixin
from src.repositories.base_repository import AbstractRepository

from src.constants import *

from src.models.task_model import Task


logger = logging.getLogger(__name__)


class TaskRepository(AbstractRepository, SessionProviderMixin):

    @SessionProviderMixin._session_provider
    async def update(
            self,
            task_id: uuid.UUID,
            _session: AsyncSession = None,
            **task_info_kwargs,
    ):
        query = update(Task).where(
            Task.id == task_id,
        ).values(
            **task_info_kwargs,
        ).returning(literal_column('*'))

        update_result = (await _session.execute(query)).first()
        await _session.commit()

        return update_result

    @SessionProviderMixin._session_provider
    async def delete(self, task_id: int, _session: AsyncSession = None):

        delete_task = await _session.get(Task, task_id)
        if not delete_task:
            return

        await _session.delete(delete_task)

    @SessionProviderMixin._session_provider
    async def get_single(self, task_id: int, _session: AsyncSession = None):
        return await _session.get(Task, task_id)

    @SessionProviderMixin._session_provider
    async def create(
            self,
            _session: AsyncSession = None,
            **task_info_kwargs,
    ):
        new_task = Task(**task_info_kwargs)

        _session.add(new_task)
        await _session.commit()
        return new_task

    @SessionProviderMixin._session_provider
    async def get(self, _session: AsyncSession = None, **task_filter_kwargs):

        task_filter_query = select(Task)

        if LIMIT_DB_STATEMENT in task_filter_kwargs and OFFSET_DB_STATEMENT in task_filter_kwargs:
            task_filter_query = (
                task_filter_query
                .limit(task_filter_kwargs[LIMIT_DB_STATEMENT])
                .offset(task_filter_kwargs[OFFSET_DB_STATEMENT])
            )
            task_filter_kwargs.pop(LIMIT_DB_STATEMENT)
            task_filter_kwargs.pop(OFFSET_DB_STATEMENT)

        if ORDER_BY_DB_STATEMENT in task_filter_kwargs:
            task_filter_query = task_filter_query.order_by(task_filter_kwargs[ORDER_BY_DB_STATEMENT])
            task_filter_kwargs.pop(ORDER_BY_DB_STATEMENT)

        if len(task_filter_kwargs):
            task_filter_query = task_filter_query.filter_by(**task_filter_kwargs)
        res = (
            await _session.execute(
                task_filter_query
            )
        ).scalars()

        await _session.commit()
        return res

