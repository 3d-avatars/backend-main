import logging

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.params import Header
from starlette.responses import JSONResponse

from src.domain.controllers import AuthorizationController, AuthorizationControllerImpl
from src.presentation.requests import RegistrationRequestBody
from src.presentation.requests.authorization.authorization_request_body import AuthorizationRequestBody
from src.presentation.responses import RegistrationResponse
from src.presentation.responses import TokenPairResponse

logger = logging.getLogger(__name__)

authorization_router = APIRouter(
    prefix="/users",
    tags=["Registration & Authorization"]
)

@authorization_router.post(
    path="/registration",
    description="Register new user",
    status_code=status.HTTP_201_CREATED,
    response_model=RegistrationResponse,
)
async def registration(
    body: RegistrationRequestBody,
    authorization_controller: AuthorizationController = Depends(AuthorizationControllerImpl),
):
    try:
        result = await authorization_controller.register_user(body.email, body.password)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )

    if not result:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
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
            detail="Something went wrong",
        )

    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong email or password",
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=tokens.model_dump()
    )


@authorization_router.get(
    path="/refresh-token",
    description="Refresh user's Access Token with Refresh Token",
    status_code=status.HTTP_200_OK,
    response_model=TokenPairResponse,
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
            detail="Something went wrong",
        )

    if tokens is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=tokens.model_dump()
    )
