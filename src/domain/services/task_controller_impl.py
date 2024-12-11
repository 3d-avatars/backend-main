import datetime
import logging
import uuid
from typing import Optional

from fastapi import Depends, UploadFile

from config import get_settings
from src.data.database.tables import TaskTable
from src.data.repositories.minio import MinioRepository, MinioRepositoryImpl
from src.data.repositories.minio_metadata import MinioMetadataRepository, MinioMetadataRepositoryImpl
from src.data.repositories.queue import QueueRepository
from src.data.repositories.queue.queue_repository_impl import QueueRepositoryImpl
from src.data.repositories.tasks import TasksRepository, TasksRepositoryImpl
from src.domain.entities import TaskEntity, MinioMetadata
from src.domain.entities.task_entity import TaskStatus
from src.domain.services.task_controller import TaskController
from src.presentation.responses import CreateTaskResponse

logger = logging.getLogger(__name__)


class TaskControllerImpl(TaskController):

    def __init__(
        self,
        minio_repository: MinioRepository = Depends(MinioRepositoryImpl),
        minio_metadata_repository: MinioMetadataRepository = Depends(MinioMetadataRepositoryImpl),
        task_repository: TasksRepository = Depends(TasksRepositoryImpl),
        task_queue: QueueRepository = Depends(QueueRepositoryImpl),
    ):
        self.settings = get_settings()
        self.minio_repository = minio_repository
        self.task_repository = task_repository
        self.minio_metadata_repository = minio_metadata_repository
        self.task_queue = task_queue

    async def get_task_status(
        self,
        task_request_uuid: uuid.UUID
    ) -> TaskStatus:
        task = await self.task_repository.get_task(request_uuid=task_request_uuid)
        return task.status

    async def get_task_result(
        self,
        task_request_uuid: uuid.UUID
    ) -> Optional[str]:
        # TODO remove stub
        return "http://130.193.48.248:9000/glb-files/avatar_male_2024-12-10_00%3A04%3A03_result.glb"
        task = await self.task_repository.get_task(request_uuid=task_request_uuid)
        result_file_id = task.result_file_metadata_id

        if not result_file_id:
            return None

        result_file_metadata = await self.minio_metadata_repository.get_metadata(result_file_id)
        result_file_url = await self.minio_repository.download_file(
            target_bucket=result_file_metadata.bucket,
            file_name=result_file_metadata.file_name,
        )

        return result_file_url

    async def create_task(
        self,
        source_file: UploadFile,
    ) -> CreateTaskResponse:
        request_uuid = uuid.uuid4()
        source_file_name, file_type = source_file.filename.split(".")
        timestamp = datetime.datetime.now()
        timestamp_formatted = timestamp.strftime("%Y-%m-%d_%H:%M:%S")
        minio_file_name = f"{source_file_name}_{timestamp_formatted}.{file_type}"

        source_file_path = await self.minio_repository.upload_file(
            target_bucket=self.settings.MINIO_IMAGES_BUCKET,
            file_name=minio_file_name,
            file_content=source_file.file,
            file_size=source_file.size,
            content_type=source_file.content_type
        )
        metadata = await self.minio_metadata_repository.create_metadata(
            bucket=self.settings.MINIO_IMAGES_BUCKET,
            file_name=minio_file_name,
        )

        task_entity = TaskEntity(
            request_uuid=request_uuid,
            source_file_metadata=MinioMetadata(
                bucket=self.settings.MINIO_IMAGES_BUCKET,
                file_name=minio_file_name,
            ),
            result_file_metadata=MinioMetadata(
                bucket=self.settings.MINIO_GLB_BUCKET,
                file_name="",
            ),
            status=TaskStatus.INITIAL
        )

        await self.task_repository.create_task(
            task=TaskTable(
                request_uuid=request_uuid,
                source_file_metadata_id=metadata.id,
                result_file_metadata_id=None,
                status=task_entity.status,
            )
        )

        await self.task_queue.push_message(
            task_entity.model_dump_json()
        )

        await self.task_repository.update_task(
            request_uuid=request_uuid,
            status=TaskStatus.PENDING
        )

        return CreateTaskResponse(
            request_uuid=str(request_uuid),
            source_file_path=str(source_file_path),
        )
