import uuid
from typing import List

from pydantic import BaseModel

class GetUserProfileInfoResponse(BaseModel):
    image_url: str
    name: str
    email: str
