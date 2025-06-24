from pydantic import BaseModel


class AuthorizationRequestBody(BaseModel):
    email: str
    password: str
