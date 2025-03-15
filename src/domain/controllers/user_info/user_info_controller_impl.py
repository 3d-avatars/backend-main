from abc import abstractmethod
from typing import Optional, List

from fastapi.params import Depends

from src.data.repositories import MinioMetadataRepository, MinioMetadataRepositoryImpl
from src.data.repositories import MinioRepository, MinioRepositoryImpl
from src.data.repositories import TasksRepository, TasksRepositoryImpl
from src.data.repositories import TokensRepository, TokensRepositoryImpl
from src.data.repositories import UsersRepository, UsersRepositoryImpl
from src.domain.controllers.user_info.user_info_controller import UserInfoController
from src.domain.entities import TokenType
from src.presentation.responses import GetUserGenerationHistoryResponse, UserGenerationHistoryItem


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
        token: str,
        token_type: TokenType,
    ) -> Optional[GetUserGenerationHistoryResponse]:
        user_id = await self.tokens_repository.get_user_id_by_token(
            token=token,
            token_type=token_type,
        )

        user = await self.users_repository.get_user_by_id(user_id)
        if user is None:
            return None

        tasks_history = await self.tasks_repository.get_tasks_by_user_id(user_id)

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
