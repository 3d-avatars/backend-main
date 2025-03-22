from pydantic import BaseModel


class RegistrationRequestBody(BaseModel):
    name: str
    email: str
    password: str
