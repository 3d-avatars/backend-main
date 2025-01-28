import datetime
import logging
import uuid
from typing import Optional

from fastapi import Depends, UploadFile

from config import get_settings
from src.data.database.tables import TaskTable
from src.data.repositories import MinioMetadataRepository, MinioMetadataRepositoryImpl
from src.data.repositories import MinioRepository, MinioRepositoryImpl
from src.data.repositories import QueueRepository, QueueRepositoryImpl
from src.data.repositories import TasksRepository, TasksRepositoryImpl
from src.domain.entities import TaskEntity, MinioMetadata
from src.domain.entities import TaskStatus
from src.domain.controllers import TaskController
from src.presentation.responses import CreateTaskResponse, GetTaskResultResponse, GetTaskStatusResponse

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
    ) -> Optional[GetTaskStatusResponse]:
        task = await self.task_repository.get_task(request_uuid=task_request_uuid)
        if task is None:
            return None

        return GetTaskStatusResponse(status=task.status)

    async def get_task_result(
        self,
        task_request_uuid: uuid.UUID
    ) -> Optional[GetTaskResultResponse]:
        task = await self.task_repository.get_task(request_uuid=task_request_uuid)
        result_file_id = task.result_file_metadata_id

        if result_file_id is None:
            return None

        result_file_metadata = await self.minio_metadata_repository.get_metadata(result_file_id)
        result_file_url = await self.minio_repository.download_file(
            target_bucket=result_file_metadata.bucket,
            file_name=result_file_metadata.file_name,
        )

        return GetTaskResultResponse(result_file_path=result_file_url)

    async def create_task(
        self,
        user_id: int,
        input_file: UploadFile,
    ) -> CreateTaskResponse:
        request_uuid = uuid.uuid4()
        file_type_index = input_file.filename.rfind(".")

        input_file_name, file_type = input_file.filename[:file_type_index], input_file.filename[file_type_index:]
        input_file_name = input_file_name.replace(" ", "_")[:10]

        timestamp = datetime.datetime.now()
        timestamp_formatted = f"{timestamp.strftime('%Y-%m-%d_%H:%M:%S')}:{timestamp.microsecond // 1000:03d}"
        minio_file_name = f"{input_file_name}_{timestamp_formatted}{file_type}"

        input_file_url = await self.minio_repository.upload_file(
            target_bucket=self.settings.MINIO_IMAGES_BUCKET,
            file_name=minio_file_name,
            file_content=input_file.file,
            file_size=input_file.size,
            content_type=input_file.content_type
        )
        input_file_metadata = await self.minio_metadata_repository.create_metadata(
            bucket=self.settings.MINIO_IMAGES_BUCKET,
            file_name=minio_file_name,
        )
        emotion_files_urls = await self.minio_repository.download_all_deca_emotions(
            target_bucket=self.settings.MINIO_DECA_EMOTIONS_BUCKET,
        )

        task_entity = TaskEntity(
            request_uuid=request_uuid,
            input_file_url=input_file_url,
            emotion_files_urls=emotion_files_urls,
            result_file_metadata=MinioMetadata(
                bucket=self.settings.MINIO_3D_FILES_BUCKET,
                file_name="",
            ),
            status=TaskStatus.INITIAL
        )

        await self.task_repository.create_task(
            task=TaskTable(
                request_uuid=request_uuid,
                status=task_entity.status,
                user_id=user_id,
                input_file_metadata_id=input_file_metadata.id,
                result_file_metadata_id=None,
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
            source_file_path=str(input_file_url),
        )
