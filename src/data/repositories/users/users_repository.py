from abc import ABC, abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database.tables import UserTable


class UsersRepository(ABC):

    @abstractmethod
    async def get_user(
        self,
        user_email: str,
        session: AsyncSession = None,
    ) -> Optional[UserTable]:
        raise NotImplementedError

    @abstractmethod
    async def create_user(
        self,
        user: UserTable,
        session: AsyncSession = None,
    ) -> UserTable:
        raise NotImplementedError
