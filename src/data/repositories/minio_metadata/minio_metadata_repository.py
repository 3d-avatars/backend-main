from abc import abstractmethod
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.data.database.tables import MinioMetadataTable


class MinioMetadataRepository:

    @abstractmethod
    async def get_metadata(
        self,
        metadata_id: int,
        session: AsyncSession = None,
    ) -> Optional[MinioMetadataTable]:
        raise NotImplementedError

    @abstractmethod
    async def create_metadata(
        self,
        session: AsyncSession = None,
        **metadata_kwargs,
    ) -> MinioMetadataTable:
        raise NotImplementedError

    @abstractmethod
    async def update_metadata(
        self,
        metadata_id: int,
        session: AsyncSession = None,
        **metadata_kwargs,
    ) -> Optional[MinioMetadataTable]:
        raise NotImplementedError
