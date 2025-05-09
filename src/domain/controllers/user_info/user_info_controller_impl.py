from typing import List
from typing import Optional

from fastapi.params import Depends

from src.data.repositories import MinioMetadataRepository
from src.data.repositories import MinioMetadataRepositoryImpl
from src.data.repositories import MinioRepository
from src.data.repositories import MinioRepositoryImpl
from src.data.repositories import TasksRepository
from src.data.repositories import TasksRepositoryImpl
from src.data.repositories import TokensRepository
from src.data.repositories import TokensRepositoryImpl
from src.data.repositories import UsersRepository
from src.data.repositories import UsersRepositoryImpl
from src.domain.controllers.user_info.user_info_controller import UserInfoController
from src.domain.entities import TokenType
from src.presentation.responses import GetUserGenerationHistoryResponse
from src.presentation.responses import GetUserProfileInfoResponse
from src.presentation.responses import UserGenerationHistoryItem


class UserInfoControllerImpl(UserInfoController):

    def __init__(
        self,
        users_repository: UsersRepository = Depends(UsersRepositoryImpl),
        tasks_repository: TasksRepository = Depends(TasksRepositoryImpl),
        minio_metadata_repository: MinioMetadataRepository = Depends(MinioMetadataRepositoryImpl),
        minio_repository: MinioRepository = Depends(MinioRepositoryImpl),
        tokens_repository: TokensRepository = Depends(TokensRepositoryImpl),
    ):
        self.users_repository = users_repository
        self.tasks_repository = tasks_repository
        self.tokens_repository = tokens_repository
        self.minio_metadata_repository = minio_metadata_repository
        self.minio_repository = minio_repository

    async def get_user_generation_history(
        self,
        access_token: str,
    ) -> Optional[GetUserGenerationHistoryResponse]:
        user_id = await self.tokens_repository.get_user_id_by_token(
            token=access_token,
            token_type=TokenType.ACCESS,
        )

        user = await self.users_repository.get_user_by_id(user_id)
        if user is None:
            return None

        tasks_history = await self.tasks_repository.get_completed_tasks_by_user_id(user_id)

        history_items: List[UserGenerationHistoryItem] = []

        for task in tasks_history:
            input_image_metadata = await self.minio_metadata_repository.get_metadata(task.input_file_metadata_id)
            input_image_url = await self.minio_repository.download_file(
                target_bucket=input_image_metadata.bucket,
                file_name=input_image_metadata.file_name,
            )

            item = UserGenerationHistoryItem(
                task_id=task.id,
                task_request_uuid=str(task.request_uuid),
                input_image_url=input_image_url,
                datetime_created=str(task.dt_created),
            )
            history_items.append(item)

        history_items.sort(key=lambda item: item.task_id)

        return GetUserGenerationHistoryResponse(
            items=history_items,
        )

    async def get_user_profile_info(
        self,
        access_token: str,
    ) -> Optional[GetUserProfileInfoResponse]:
        user_id = await self.tokens_repository.get_user_id_by_token(
            token=access_token,
            token_type=TokenType.ACCESS,
        )

        user = await self.users_repository.get_user_by_id(user_id)
        if user is None:
            return None

        task = await self.tasks_repository.get_first_task_of_user(user.id)

        input_image_url = ""
        user_name = user.name if user.name is not None else ""

        if task is not None:
            input_image_metadata = await self.minio_metadata_repository.get_metadata(task.input_file_metadata_id)

            if input_image_metadata is not None:
                input_image_url = await self.minio_repository.download_file(
                    target_bucket=input_image_metadata.bucket,
                    file_name=input_image_metadata.file_name,
                )

        return GetUserProfileInfoResponse(
            name=user_name,
            email=user.email,
            image_url=input_image_url,
        )
