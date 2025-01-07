from pydantic import BaseModel


class RegistrationResponse(BaseModel):
    user_id: int
