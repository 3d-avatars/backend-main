from enum import Enum

from pydantic import BaseModel

class TokenType(str, Enum):
    ACCESS = "Access"
    REFRESH = "Refresh"


class TokenPayload(BaseModel):
    user_id: int
    user_email: str
    expire_timestamp: float
