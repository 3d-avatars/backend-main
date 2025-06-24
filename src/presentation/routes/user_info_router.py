import logging

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import Header
from fastapi import status
from starlette.responses import JSONResponse

from src.domain.controllers import AuthorizationController
from src.domain.controllers import AuthorizationControllerImpl
from src.domain.controllers import UserInfoController
from src.domain.controllers import UserInfoControllerImpl
from src.domain.entities import TokenType
from src.presentation.responses import GetUserGenerationHistoryResponse
from src.presentation.responses import GetUserProfileInfoResponse
from src.utils.http_constants import HTTP_CODE_401_MESSAGE
from src.utils.http_constants import HTTP_CODE_403_MESSAGE
from src.utils.http_constants import HTTP_CODE_500_MESSAGE

logger = logging.getLogger(__name__)

USER_HISTORY_404_MESSAGE = "Did not find history for this user"
USER_INFO_404_MESSAGE = "Did not find personal info for this user"

user_info_router = APIRouter(
    prefix="/user-info",
    tags=["User Info"],
    responses={
        401: { "description": HTTP_CODE_401_MESSAGE },
        403: { "description": HTTP_CODE_403_MESSAGE },
    }
)


@user_info_router.get(
    path="/generation-history",
    description="Get history of user's generation tasks",
    status_code=status.HTTP_200_OK,
    response_model=GetUserGenerationHistoryResponse,
    responses={
        404: { "description": USER_HISTORY_404_MESSAGE },
    },
)
async def get_user_generation_history(
    access_token: str = Header(),
    auth_controller: AuthorizationController = Depends(AuthorizationControllerImpl),
    user_info_controller: UserInfoController = Depends(UserInfoControllerImpl),
):
    token_validation_result = await auth_controller.validate_token(access_token, TokenType.ACCESS)
    if token_validation_result.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=token_validation_result.status_code,
            detail=token_validation_result.detail,
        )

    try:
        generation_history_response = await user_info_controller.get_user_generation_history(
            access_token=access_token,
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=HTTP_CODE_500_MESSAGE,
        )

    if generation_history_response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_HISTORY_404_MESSAGE,
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=generation_history_response.model_dump()
    )

@user_info_router.get(
    path="/profile-info",
    description="Get user profile info",
    status_code=status.HTTP_200_OK,
    response_model=GetUserProfileInfoResponse,
    responses={
        404: { "description": USER_INFO_404_MESSAGE }
    },
)
async def get_user_profile_info(
    access_token: str = Header(),
    auth_controller: AuthorizationController = Depends(AuthorizationControllerImpl),
    user_info_controller: UserInfoController = Depends(UserInfoControllerImpl),
):
    token_validation_result = await auth_controller.validate_token(access_token, TokenType.ACCESS)
    if token_validation_result.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=token_validation_result.status_code,
            detail=token_validation_result.detail,
        )

    try:
        user_profile_info_response = await user_info_controller.get_user_profile_info(
            access_token=access_token,
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=HTTP_CODE_500_MESSAGE,
        )

    if user_profile_info_response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=USER_INFO_404_MESSAGE,
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=user_profile_info_response.model_dump()
    )

