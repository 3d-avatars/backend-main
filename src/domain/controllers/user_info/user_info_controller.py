from abc import ABC, abstractmethod
from typing import Optional

from src.presentation.responses import GetUserGenerationHistoryResponse
from src.presentation.responses import GetUserProfileInfoResponse


class UserInfoController(ABC):

    @abstractmethod
    async def get_user_generation_history(
        self,
        access_token: str,
    ) -> Optional[GetUserGenerationHistoryResponse]:
        raise NotImplementedError

    @abstractmethod
    async def get_user_profile_info(
        self,
        access_token: str,
    ) -> Optional[GetUserProfileInfoResponse]:
        raise NotImplementedError
