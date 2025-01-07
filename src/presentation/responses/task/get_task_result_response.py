from pydantic import BaseModel


class GetTaskResultResponse(BaseModel):
    result_file_path: str