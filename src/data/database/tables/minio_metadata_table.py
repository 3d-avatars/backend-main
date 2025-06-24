from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import TEXT

from src.data.database.tables import BaseTable


class MinioMetadataTable(BaseTable):
    __tablename__ = "minio_metadata"

    bucket = Column(
        "bucket",
        TEXT,
        nullable=False,
        doc="S3 Bucket where file is stored"
    )

    file_name = Column(
        "file_name",
        TEXT,
        nullable=False,
        unique=True,
        doc="Name of file in bucket"
    )
