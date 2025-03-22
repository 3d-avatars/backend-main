from abc import ABC, abstractmethod
from typing import Optional

from src.domain.entities import TokenType
from src.presentation.responses import TokenPairResponse
from src.presentation.responses import RegistrationResponse
from src.presentation.responses.authorization.token_validation_response import TokenValidationResponse


class AuthorizationController(ABC):

    @abstractmethod
    async def register_user(
        self,
        name: str,
        email: str,
        password: str
    ) -> Optional[RegistrationResponse]:
        raise NotImplementedError

    @abstractmethod
    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> Optional[TokenPairResponse]:
        raise NotImplementedError

    @abstractmethod
    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> Optional[TokenPairResponse]:
        raise NotImplementedError

    @abstractmethod
    async def validate_token(
        self,
        token: str,
        token_type: TokenType
    ) -> TokenValidationResponse:
        raise NotImplementedError