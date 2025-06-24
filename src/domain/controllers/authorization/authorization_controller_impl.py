import logging
from datetime import datetime
from datetime import timedelta
from datetime import timezone
from typing import Optional

from fastapi import Depends
from fastapi import status
from jose import jwt
from passlib.context import CryptContext

from config import get_settings
from src.data.database.tables import TokenTable
from src.data.database.tables import UserTable
from src.data.repositories import TokensRepository
from src.data.repositories import TokensRepositoryImpl
from src.data.repositories import UsersRepository
from src.data.repositories import UsersRepositoryImpl
from src.domain.controllers import AuthorizationController
from src.domain.entities import TokenPayload
from src.domain.entities import TokenType
from src.presentation.responses import RegistrationResponse
from src.presentation.responses import TokenPairResponse
from src.presentation.responses import TokenValidationResponse
from src.utils.http_constants import HTTP_CODE_401_MESSAGE
from src.utils.http_constants import HTTP_CODE_403_MESSAGE

logger = logging.getLogger(__name__)


class AuthorizationControllerImpl(AuthorizationController):

    def __init__(
        self,
        users_repository: UsersRepository = Depends(UsersRepositoryImpl),
        tokens_repository: TokensRepository = Depends(TokensRepositoryImpl),
    ):
        self.config = get_settings()
        self.crypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
        self.users_repository = users_repository
        self.tokens_repository = tokens_repository

    async def register_user(
        self,
        name: str,
        email: str,
        password: str
    ) -> Optional[RegistrationResponse]:
        user = await self.users_repository.get_user_by_email(email)
        if user is not None:
            return None

        user = UserTable(
            name=name,
            email=email,
            hashed_password=self.crypt_context.hash(password)
        )
        await self.users_repository.create_user(user)

        return RegistrationResponse(user_id=user.id)

    async def authenticate_user(
        self,
        email: str,
        password: str,
    ) -> Optional[TokenPairResponse]:
        user = await self.users_repository.get_user_by_email(email)

        if user is not None and self.crypt_context.verify(password, user.hashed_password):
            access_token = self.__create_token(
                user_id=user.id,
                user_email=user.email,
                secret_key=self.config.SECRET_KEY,
                expires_delta=timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES),
            )
            refresh_token = self.__create_token(
                user_id=user.id,
                user_email=user.email,
                secret_key=self.config.REFRESH_SECRET_KEY,
                expires_delta=timedelta(minutes=self.config.REFRESH_TOKEN_EXPIRE_MINUTES),
            )

            await self.tokens_repository.add_token(
                token=TokenTable(
                    token=access_token,
                    type=TokenType.ACCESS,
                    user_id=user.id,
                )
            )
            await self.tokens_repository.add_token(
                token=TokenTable(
                    token=refresh_token,
                    type=TokenType.REFRESH,
                    user_id=user.id,
                )
            )

            return TokenPairResponse(
                access_token=access_token,
                refresh_token=refresh_token,
            )
        else:
            return None

    async def refresh_access_token(
        self,
        refresh_token: str,
    ) -> Optional[TokenPairResponse]:
        token_validation_result = await self.validate_token(refresh_token, TokenType.REFRESH)
        if token_validation_result.status_code != status.HTTP_200_OK:
            return None

        new_access_token = self.__create_token(
            user_id=token_validation_result.token_payload.user_id,
            user_email=token_validation_result.token_payload.user_email,
            secret_key=self.config.SECRET_KEY,
            expires_delta=timedelta(minutes=self.config.ACCESS_TOKEN_EXPIRE_MINUTES),
        )

        await self.tokens_repository.add_token(
            token=TokenTable(
                token=new_access_token,
                type=TokenType.ACCESS,
                user_id=token_validation_result.token_payload.user_id,
            )
        )

        return TokenPairResponse(
            access_token=new_access_token,
            refresh_token=refresh_token
        )

    async def validate_token(
        self,
        token: str,
        token_type: TokenType
    ) -> TokenValidationResponse:
        secret_key = self.config.SECRET_KEY if token_type == TokenType.ACCESS else self.config.REFRESH_SECRET_KEY

        try:
            payload = jwt.decode(
                token=token,
                key=secret_key,
                algorithms=[self.config.HASH_ALGORITHM],
            )
            token_payload = TokenPayload(**payload)

            if datetime.fromtimestamp(token_payload.expire_timestamp) < datetime.now():
                await self.tokens_repository.delete_token(
                    token=token,
                    token_type=token_type,
                )

                return TokenValidationResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=HTTP_CODE_401_MESSAGE,
                )

        except Exception as e:
            logger.exception(e)
            return TokenValidationResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTP_CODE_403_MESSAGE,
            )

        user = await self.users_repository.get_user_by_email(token_payload.user_email)
        if user is None:
            return TokenValidationResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTP_CODE_403_MESSAGE,
            )

        user_id = await self.tokens_repository.get_user_id_by_token(
            token=token,
            token_type=token_type,
        )

        if user_id is None or user.id != user_id:
            return TokenValidationResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=HTTP_CODE_403_MESSAGE,
            )

        return TokenValidationResponse(
            token_payload=token_payload,
            status_code=status.HTTP_200_OK,
            detail="",
        )

    def __create_token(
        self,
        user_id: int,
        user_email: str,
        secret_key: str,
        expires_delta: timedelta,
    ) -> str:
        payload = TokenPayload(
            user_id=user_id,
            user_email=user_email,
            expire_timestamp=(datetime.now(timezone.utc) + expires_delta).timestamp()
        )
        encoded_jwt = jwt.encode(
            payload.model_dump(),
            secret_key,
            self.config.HASH_ALGORITHM
        )
        return encoded_jwt
