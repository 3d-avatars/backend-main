from pydantic import BaseModel


class CreateTaskResponse(BaseModel):
    request_uuid: str
    source_file_path: str
