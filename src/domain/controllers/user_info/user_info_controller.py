from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities import TokenType
from src.presentation.responses import GetUserGenerationHistoryResponse


class UserInfoController(ABC):

    @abstractmethod
    async def get_user_generation_history(
        self,
        token: str,
        token_type: TokenType,
    ) -> Optional[GetUserGenerationHistoryResponse]:
        raise NotImplementedError
