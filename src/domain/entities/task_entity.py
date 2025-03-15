import uuid
from typing import Optional, List

from pydantic import BaseModel

from src.domain.entities.minio_metadata_entity import MinioMetadata
from src.utils.lru_cached_enum import LruCachedEnum


class TaskStatus(str, LruCachedEnum):
    INITIAL = "INITIAL",
    PENDING = "PENDING",
    IN_PROGRESS = "IN_PROGRESS",
    SUCCESS = "SUCCESS",
    FAILED = "FAILED",


class TaskEntity(BaseModel):
    request_uuid: uuid.UUID
    input_file_url: str
    emotion_files_urls: List[str]
    result_file_metadata: Optional[MinioMetadata]
    status: TaskStatus
