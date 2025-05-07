import uuid
from typing import List

from pydantic import BaseModel

from src.domain.entities.minio_metadata_entity import MinioMetadata
from src.utils.lru_cached_enum import LruCachedEnum


# === INPUT ===

class TaskClientType(str, LruCachedEnum):
    WEB_SERVICE = "WEB_SERVICE",
    EXTERNAL_INTEGRATION = "EXTERNAL_INTEGRATION",

class TaskInputMetadata(BaseModel):
    input_file_url: str
    emotions_files_urls: List[str]
    output_bucket: str

class TaskRequestEntity(BaseModel):
    request_uuid: uuid.UUID
    task_client_type: TaskClientType
    task_input_metadata: TaskInputMetadata

# === PROGRESS ===

class TaskStatus(str, LruCachedEnum):
    INITIAL = "INITIAL",
    PENDING = "PENDING",
    IN_PROGRESS = "IN_PROGRESS",
    SUCCESS = "SUCCESS",
    INVALID_INPUT = "INVALID_INPUT",
    FAILED = "FAILED",

class TaskProgressEntity(BaseModel):
    request_uuid: uuid.UUID
    status: TaskStatus

# === RESULT ===

class MeshMetadata(BaseModel):
    skin_color_hex: str

class TaskResultEntity(BaseModel):
    request_uuid: uuid.UUID
    minio_metadata: MinioMetadata
    mesh_metadata: MeshMetadata
