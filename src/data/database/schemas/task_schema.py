import datetime
import typing
import uuid

from src.schemas.base_schema import Base
from src.enums import TaskStatus

from pydantic import Field


class TaskStateUpdateRequest(Base):
    state: TaskStatus


class Task(Base):
    id: int
    request_uuid: uuid.UUID
    source_file_path: str
    result_file_path: typing.Optional[str]
    state: TaskStatus

    dt_created: datetime.datetime
    dt_updated: datetime.datetime


class TaskFilter(Base):
    request_uuid: typing.Optional[uuid.UUID] = None
    state: typing.Optional[TaskStatus] = None

    source_file_path: typing.Optional[str] = None
    result_file_path: typing.Optional[str] = None

    limit: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)
    order_by: typing.Literal["dt_created", "dt_updated"] = "dt_created"

