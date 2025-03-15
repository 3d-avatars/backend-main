import uuid
from typing import List

from pydantic import BaseModel

class UserGenerationHistoryItem(BaseModel):
    task_id: int
    task_request_uuid: str
    input_image_url: str
    datetime_created: str

class GetUserGenerationHistoryResponse(BaseModel):
    items: List[UserGenerationHistoryItem]
