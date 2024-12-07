from sqlalchemy import Column, Enum
from sqlalchemy.dialects.postgresql import TEXT, UUID

from src.data.database.tables.base_table import BaseTable
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

    source_file_path = Column(
        "source_file_path",
        TEXT,
        nullable=False,
        doc="S3 Url for generated model",
    )

    result_file_path = Column(
        "result_file_path",
        TEXT,
        nullable=True,
        doc="S3 Url for generated model",
    )
