import logging

from fastapi import APIRouter, Depends, HTTPException, status, Header
from starlette.responses import JSONResponse

from src.domain.controllers import AuthorizationController, AuthorizationControllerImpl
from src.domain.controllers import UserInfoController, UserInfoControllerImpl
from src.domain.entities import TokenType
from src.presentation.responses.user_info.get_user_generation_history_response import GetUserGenerationHistoryResponse

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
            token=access_token,
            token_type=TokenType.ACCESS
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
