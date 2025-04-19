from pydantic import BaseModel

from src.domain.entities.task_entity import MeshMetadata


class GetTaskResultResponse(BaseModel):
    result_file_path: str
    mesh_metadata: MeshMetadata
