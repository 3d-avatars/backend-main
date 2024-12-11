from abc import abstractmethod
from typing import BinaryIO


class MinioRepository:

    @abstractmethod
    async def upload_file(
        self,
        target_bucket: str,
        file_name: str,
        file_content: BinaryIO,
        file_size: int,
        content_type: str,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    async def download_file(
        self,
        target_bucket: str,
        file_name: str,
    ) -> str:
        raise NotImplementedError
