from typing import Optional

from pydantic import BaseModel

from src.domain.entities import TokenPayload


class TokenValidationResponse(BaseModel):
    token_payload: Optional[TokenPayload] = None
    status_code: int
    detail: str
