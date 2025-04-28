import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.sync import update

from src.data.database.connection import SessionProviderMixin
from src.data.database.tables import MeshMetadataTable
from src.data.repositories.mesh_metadata.mesh_metadata_repository import MeshMetadataRepository

logger = logging.getLogger(__name__)


class MeshMetadataRepositoryImpl(MeshMetadataRepository, SessionProviderMixin):

    @SessionProviderMixin.session_provider
    async def get_metadata(
        self,
        metadata_id: int,
        session: AsyncSession = None
    ) -> Optional[MeshMetadataTable]:
        metadata: Optional[MeshMetadataTable] = await session.get(MeshMetadataTable, metadata_id)
        await session.commit()
        logger.info(f"Selected mesh metadata {metadata}")
        return metadata

    @SessionProviderMixin.session_provider
    async def create_metadata(
        self,
        session: AsyncSession = None,
        **metadata_kwargs,
    ) -> MeshMetadataTable:
        new_metadata = MeshMetadataTable(**metadata_kwargs)

        session.add(new_metadata)
        await session.commit()

        logger.info(f"Created new mesh metadata {new_metadata}")
        return new_metadata

    @SessionProviderMixin.session_provider
    async def update_metadata(
        self,
        metadata_id: int,
        session: AsyncSession = None,
        **metadata_kwargs,
    ) -> Optional[MeshMetadataTable]:
        query = update(MeshMetadataTable).where(
            MeshMetadataTable.id == metadata_id
        ).values(
            **metadata_kwargs
        ).returning(MeshMetadataTable)

        update_result: Optional[MeshMetadataTable] = (await session.execute(query)).scalar()
        await session.commit()

        logger.info(f"Updated mesh metadata {update_result}")
        return update_result
