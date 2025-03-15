import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from src.data.database.connection import SessionProviderMixin
from src.data.database.tables.token_table import TokenTable
from src.data.repositories.tokens.tokens_repository import TokensRepository
from src.domain.entities import TokenType

logger = logging.getLogger(__name__)


class TokensRepositoryImpl(TokensRepository, SessionProviderMixin):

    @SessionProviderMixin.session_provider
    async def add_token(
        self,
        token: TokenTable,
        session: AsyncSession = None,
    ) -> TokenTable:
        session.add(token)
        await session.commit()

        logger.info(f"Added token {token}")
        return token

    @SessionProviderMixin.session_provider
    async def get_user_id_by_token(
        self,
        token: str,
        token_type: TokenType,
        session: AsyncSession = None,
    ) -> Optional[int]:
        token_query = select(TokenTable).where(
            TokenTable.token == token,
            TokenTable.type == token_type,
        )
        result: Optional[TokenTable] = (await session.execute(token_query)).scalar()

        await session.commit()

        logger.info(f"Selected user id by token {result}")
        return result

    @SessionProviderMixin.session_provider
    async def delete_token(
        self,
        token: str,
        token_type: TokenType,
        session: AsyncSession = None,
    ) -> Optional[TokenTable]:
        query = delete(TokenTable).where(
            TokenTable.token == token,
            TokenTable.type == token_type,
        ).returning(TokenTable)

        result: Optional[TokenTable] = (await session.execute(query)).scalar()
        await session.commit()

        logger.info(f"Delete token {result}")
        return result
