from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TEXT

from src.data.database.tables import BaseTable


class MeshMetadataTable(BaseTable):
    __tablename__ = "mesh_metadata"

    skin_color_hex = Column(
        "skin_color_hex",
        TEXT,
        nullable=False,
        doc="3D model skin color in hex format"
    )
