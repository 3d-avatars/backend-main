from pydantic import BaseModel


class GetTaskStatusResponse(BaseModel):
    status: str
