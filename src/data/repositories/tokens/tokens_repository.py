from abc import ABC
from abc import abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database.tables import TokenTable
from src.domain.entities import TokenType


class TokensRepository(ABC):

    @abstractmethod
    async def add_token(
        self,
        token: TokenTable,
        session: AsyncSession = None,
    ) -> TokenTable:
        raise NotImplementedError

    @abstractmethod
    async def get_user_id_by_token(
        self,
        token: str,
        token_type: TokenType,
        session: AsyncSession = None,
    ) -> Optional[int]:
        raise NotImplementedError

    @abstractmethod
    async def delete_token(
        self,
        token: str,
        token_type: TokenType,
        session: AsyncSession = None,
    ) -> Optional[TokenTable]:
        raise NotImplementedError
