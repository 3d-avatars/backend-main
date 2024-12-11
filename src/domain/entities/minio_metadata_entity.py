from pydantic import BaseModel


class MinioMetadata(BaseModel):
    bucket: str
    file_name: str
