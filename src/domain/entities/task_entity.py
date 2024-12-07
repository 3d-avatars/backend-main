import uuid

from pydantic import BaseModel

from src.utils.lru_cached_enum import LruCachedEnum


class TaskStatus(str, LruCachedEnum):
    INITIAL = "INITIAL",
    IN_PROGRESS = "IN_PROGRESS",
    SUCCESS = "SUCCESS",
    FAILED = "FAILED",


class TaskEntity(BaseModel):
    request_uuid: uuid.UUID
    source_file_path: str
    result_file_path: str
    status: TaskStatus
