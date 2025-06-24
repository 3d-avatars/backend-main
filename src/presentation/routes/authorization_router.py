import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import status
from fastapi.params import Header
from starlette.responses import JSONResponse

from src.domain.controllers import AuthorizationController
from src.domain.controllers import AuthorizationControllerImpl
from src.presentation.requests import RegistrationRequestBody
from src.presentation.requests.authorization.authorization_request_body import AuthorizationRequestBody
from src.presentation.responses import RegistrationResponse
from src.presentation.responses import TokenPairResponse
from src.utils.http_constants import HTTP_CODE_401_MESSAGE
from src.utils.http_constants import HTTP_CODE_500_MESSAGE

logger = logging.getLogger(__name__)

AUTH_409_MESSAGE = "User with this email already exists"
AUTH_400_MESSAGE = "Wrong email or password"

authorization_router = APIRouter(
    prefix="/users",
    tags=["Registration & Authorization"],
)

@authorization_router.post(
    path="/registration",
    description="Register new user",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
    responses={
        409: { "description": AUTH_409_MESSAGE },
    },
)
async def registration(
    body: RegistrationRequestBody,
    authorization_controller: AuthorizationController = Depends(AuthorizationControllerImpl),
):
    try:
        result = await authorization_controller.register_user(body.name, body.email, body.password)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=HTTP_CODE_500_MESSAGE,
        )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=AUTH_409_MESSAGE,
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=result.model_dump()
    )


@authorization_router.post(
    path="/authorization",
    description="Authorization",
    status_code=status.HTTP_200_OK,
    response_model=TokenPairResponse,
    responses={
        400: { "description": AUTH_400_MESSAGE },
    },
)
async def authorization(
    body: AuthorizationRequestBody,
    authorization_controller: AuthorizationController = Depends(AuthorizationControllerImpl),
):
    try:
        tokens = await authorization_controller.authenticate_user(body.email, body.password)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=HTTP_CODE_500_MESSAGE,
        )

    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=AUTH_400_MESSAGE,
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=tokens.model_dump()
    )


@authorization_router.get(
    path="/refresh-token",
    description="Create new user's Access Token with Refresh Token",
    status_code=status.HTTP_200_OK,
    response_model=TokenPairResponse,
    responses={
        401: { "description": HTTP_CODE_401_MESSAGE },
    },
)
async def refresh_access_token(
    refresh_token: str = Header(),
    authorization_controller: AuthorizationController = Depends(AuthorizationControllerImpl),
):
    try:
        tokens = await authorization_controller.refresh_access_token(refresh_token)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=HTTP_CODE_500_MESSAGE,
        )

    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=HTTP_CODE_401_MESSAGE,
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=tokens.model_dump()
    )
