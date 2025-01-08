from pydantic import BaseModel


class RegistrationRequestBody(BaseModel):
    email: str
    password: str
