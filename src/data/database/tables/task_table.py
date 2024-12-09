from sqlalchemy import Column, Enum, ForeignKey, BIGINT
from sqlalchemy.dialects.postgresql import UUID

from src.data.database.tables import BaseTable
from src.domain.entities import TaskStatus


class TaskTable(BaseTable):
    __tablename__ = "task"

    request_uuid = Column(
        "request_uuid",
        UUID,
        unique=True,
        nullable=False,
        doc="Generation request uuid",
    )

    status = Column(
        "status",
        Enum(TaskStatus),
        nullable=False,
        doc="Task status",
        default=TaskStatus.INITIAL
    )

    source_file_metadata_id = Column(
        "source_file_metadata_id",
        BIGINT,
        ForeignKey("minio_metadata.id"),
        nullable=False,
        unique=True,
        doc="S3 metadata for source file",
    )

    result_file_metadata_id = Column(
        "result_file_metadata_id",
        BIGINT,
        ForeignKey("minio_metadata.id"),
        nullable=True,
        unique=True,
        doc="S3 metadata for result file",
    )
