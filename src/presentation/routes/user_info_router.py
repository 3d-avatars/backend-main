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

logger = logging.getLogger(__name__)

user_info_router = APIRouter(
    prefix="/user-info",
    tags=["User Info"],
)

@user_info_router.get(
    path="/generation-history",
    description="Get history of user's generation tasks",
    status_code=status.HTTP_200_OK,
    response_model=GetUserGenerationHistoryResponse,
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
            detail="Something went wrong",
        )

    if generation_history_response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Didnt find history for this user"
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
            detail="Something went wrong",
        )

    if user_profile_info_response is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Didnt find history for this user"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=user_profile_info_response.model_dump()
    )

