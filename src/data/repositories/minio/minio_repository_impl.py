import logging
from typing import BinaryIO
from typing import List
from typing import Optional

from src.data.minio import MinioManager
from src.data.repositories import MinioRepository

logger = logging.getLogger(__name__)


class MinioRepositoryImpl(MinioRepository):

    def __init__(self):
        self.manager = MinioManager()

    async def upload_file(
        self,
        target_bucket: str,
        file_name: str,
        file_content: BinaryIO,
        file_size: int,
        content_type: str,
    ) -> str:
        self.manager.client.put_object(
            bucket_name=target_bucket,
            object_name=file_name,
            data=file_content,
            length=file_size,
            content_type=content_type,
        )
        logger.info(f"Uploaded file {file_name} to bucket {target_bucket}")
        return await self.download_file(
            target_bucket=target_bucket,
            file_name=file_name,
        )

    async def download_file(
        self,
        target_bucket: str,
        file_name: str,
    ) -> str:
        response: Optional[str] = None

        try:
            response = self.manager.client.presigned_get_object(
                bucket_name=target_bucket,
                object_name=file_name,
            )
            logger.info(f"URL for downloading file {response} from bucket {target_bucket}")
        except Exception as e:
            logger.error(f"Failed to download file with exception {e}")

        if response is None:
            return ""

        http_options_index = response.find("?")
        return response[:http_options_index] if http_options_index != -1 else response

    async def download_all_deca_emotions(
        self,
        target_bucket: str,
    ) -> List[str]:
        response: List[str] = []

        files = self.manager.client.list_objects(
            bucket_name=target_bucket
        )

        for file in files:
            download_url = await self.download_file(
                target_bucket=target_bucket,
                file_name=file.object_name
            )
            response.append(download_url)

        logger.info(f"Got deca emotions urls {response}")
        return response
