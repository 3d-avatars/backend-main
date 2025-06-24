import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database.connection import SessionProviderMixin
from src.data.database.tables import UserTable
from src.data.repositories import UsersRepository

logger = logging.getLogger(__name__)


class UsersRepositoryImpl(UsersRepository, SessionProviderMixin):

    @SessionProviderMixin.session_provider
    async def get_user_by_email(
        self,
        user_email: str,
        session: AsyncSession = None,
    ) -> Optional[UserTable]:
        user_query = select(UserTable).where(UserTable.email == user_email)
        result: Optional[UserTable] = (await session.execute(user_query)).scalar()

        await session.commit()

        logger.info(f"Selected user {result}")
        return result

    @SessionProviderMixin.session_provider
    async def get_user_by_id(
        self,
        user_id: int,
        session: AsyncSession = None,
    ) -> Optional[UserTable]:
        user_query = select(UserTable).where(UserTable.id == user_id)
        result: Optional[UserTable] = (await session.execute(user_query)).scalar()

        await session.commit()

        logger.info(f"Selected user {result}")
        return result

    @SessionProviderMixin.session_provider
    async def create_user(
        self,
        user: UserTable,
        session: AsyncSession = None,
    ) -> UserTable:
        session.add(user)
        await session.commit()

        logger.info(f"Created user {user}")
        return user
