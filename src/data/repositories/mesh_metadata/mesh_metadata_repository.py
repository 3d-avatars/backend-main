from abc import abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database.tables import MeshMetadataTable


class MeshMetadataRepository:

    @abstractmethod
    async def get_metadata(
        self,
        metadata_id: int,
        session: AsyncSession = None
    ) -> Optional[MeshMetadataTable]:
        raise NotImplementedError

    @abstractmethod
    async def create_metadata(
        self,
        session: AsyncSession = None,
        **metadata_kwargs,
    ) -> MeshMetadataTable:
        raise NotImplementedError

    @abstractmethod
    async def update_metadata(
        self,
        metadata_id: int,
        session: AsyncSession = None,
        **metadata_kwargs,
    ) -> Optional[MeshMetadataTable]:
        raise NotImplementedError
