import datetime
import logging
import uuid
from typing import Optional

from fastapi import Depends
from fastapi import UploadFile

from config import get_settings
from src.data.database.tables import TaskTable
from src.data.repositories import MeshMetadataRepository
from src.data.repositories import MeshMetadataRepositoryImpl
from src.data.repositories import MinioMetadataRepository
from src.data.repositories import MinioMetadataRepositoryImpl
from src.data.repositories import MinioRepository
from src.data.repositories import MinioRepositoryImpl
from src.data.repositories import QueueRepository
from src.data.repositories import QueueRepositoryImpl
from src.data.repositories import TasksRepository
from src.data.repositories import TasksRepositoryImpl
from src.domain.controllers import TaskController
from src.domain.entities import MeshMetadata
from src.domain.entities import TaskClientType
from src.domain.entities import TaskInputMetadata
from src.domain.entities import TaskRequestEntity
from src.domain.entities import TaskStatus
from src.presentation.responses import CreateTaskResponse
from src.presentation.responses import GetTaskResultResponse
from src.presentation.responses import GetTaskStatusResponse

logger = logging.getLogger(__name__)


class TaskControllerImpl(TaskController):

    def __init__(
        self,
        task_queue: QueueRepository = Depends(QueueRepositoryImpl),
        task_repository: TasksRepository = Depends(TasksRepositoryImpl),
        minio_repository: MinioRepository = Depends(MinioRepositoryImpl),
        minio_metadata_repository: MinioMetadataRepository = Depends(MinioMetadataRepositoryImpl),
        mesh_metadata_repository: MeshMetadataRepository = Depends(MeshMetadataRepositoryImpl),
    ):
        self.settings = get_settings()
        self.task_queue = task_queue
        self.task_repository = task_repository
        self.minio_repository = minio_repository
        self.minio_metadata_repository = minio_metadata_repository
        self.mesh_metadata_repository = mesh_metadata_repository

    async def get_task_status(
        self,
        task_request_uuid: uuid.UUID
    ) -> Optional[GetTaskStatusResponse]:
        task = await self.task_repository.get_task_by_request_uuid(request_uuid=task_request_uuid)
        if task is None:
            return None

        return GetTaskStatusResponse(status=task.status)

    async def get_task_result(
        self,
        task_request_uuid: uuid.UUID
    ) -> Optional[GetTaskResultResponse]:
        task = await self.task_repository.get_task_by_request_uuid(request_uuid=task_request_uuid)

        result_file_id = task.result_file_metadata_id
        if result_file_id is None:
            return None

        result_file_metadata = await self.minio_metadata_repository.get_metadata(result_file_id)
        result_file_url = await self.minio_repository.download_file(
            target_bucket=result_file_metadata.bucket,
            file_name=result_file_metadata.file_name,
        )

        mesh_metadata_id = task.mesh_metadata_id
        if mesh_metadata_id is None:
            mesh_metadata = None
        else:
            mesh_metadata_raw = await self.mesh_metadata_repository.get_metadata(
                metadata_id=mesh_metadata_id
            )
            mesh_metadata = MeshMetadata(
                skin_color_hex=mesh_metadata_raw.skin_color_hex,
            )

        return GetTaskResultResponse(
            result_file_path=result_file_url,
            mesh_metadata=mesh_metadata
        )

    async def create_task(
        self,
        user_id: Optional[int],
        input_file: UploadFile,
    ) -> CreateTaskResponse:
        request_uuid = uuid.uuid4()
        file_type_index = input_file.filename.rfind(".")

        input_file_name, file_type = input_file.filename[:file_type_index], input_file.filename[file_type_index:]
        input_file_name = input_file_name.replace(" ", "_")[:10]

        timestamp = datetime.datetime.now()
        timestamp_formatted = f"{timestamp.strftime('%Y-%m-%d_%H-%M-%S')}-{timestamp.microsecond // 1000:03d}"
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

        task_request = TaskRequestEntity(
            request_uuid=request_uuid,
            task_client_type=TaskClientType.WEB_SERVICE,
            task_input_metadata=TaskInputMetadata(
                input_file_url=input_file_url,
                emotions_files_urls=emotion_files_urls,
                output_bucket=self.settings.MINIO_3D_FILES_BUCKET
            ),
        )

        await self.task_repository.create_task(
            task=TaskTable(
                request_uuid=request_uuid,
                status=TaskStatus.INITIAL,
                user_id=user_id,
                input_file_metadata_id=input_file_metadata.id,
                result_file_metadata_id=None,
                mesh_metadata_id=None,
            )
        )

        await self.task_queue.push_message(
            task_request.model_dump_json()
        )

        await self.task_repository.update_task(
            request_uuid=request_uuid,
            status=TaskStatus.PENDING
        )

        return CreateTaskResponse(
            request_uuid=str(request_uuid),
            source_file_path=str(input_file_url),
        )
