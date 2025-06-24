import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.sync import update

from src.data.database.connection import SessionProviderMixin
from src.data.database.tables import MinioMetadataTable
from src.data.repositories import MinioMetadataRepository

logger = logging.getLogger(__name__)


class MinioMetadataRepositoryImpl(MinioMetadataRepository, SessionProviderMixin):

    @SessionProviderMixin.session_provider
    async def get_metadata(
        self,
        metadata_id: int,
        session: AsyncSession = None,
    ) -> Optional[MinioMetadataTable]:
        metadata: Optional[MinioMetadataTable] = await session.get(MinioMetadataTable, metadata_id)
        await session.commit()
        logger.info(f"Selected minio metadata {metadata}")
        return metadata

    @SessionProviderMixin.session_provider
    async def create_metadata(
        self,
        session: AsyncSession = None,
        **metadata_kwargs,
    ) -> MinioMetadataTable:
        new_metadata = MinioMetadataTable(**metadata_kwargs)

        session.add(new_metadata)
        await session.commit()

        logger.info(f"Created new minio metadata {new_metadata}")
        return new_metadata

    @SessionProviderMixin.session_provider
    async def update_metadata(
        self,
        metadata_id: int,
        session: AsyncSession = None,
        **metadata_kwargs,
    ) -> Optional[MinioMetadataTable]:
        query = update(MinioMetadataTable).where(
            MinioMetadataTable.id == metadata_id
        ).values(
            **metadata_kwargs,
        ).returning(MinioMetadataTable)

        update_result: Optional[MinioMetadataTable] = (await session.execute(query)).scalar()
        await session.commit()

        logger.info(f"Updated minio metadata {update_result}")
        return update_result
