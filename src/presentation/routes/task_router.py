import logging
import uuid

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status
from fastapi.params import Header
from fastapi.responses import JSONResponse

from src.domain.controllers import AuthorizationController
from src.domain.controllers import AuthorizationControllerImpl
from src.domain.controllers import TaskController
from src.domain.controllers import TaskControllerImpl
from src.domain.entities import TaskClientType
from src.domain.entities import TaskStatus
from src.domain.entities import TokenType
from src.presentation.responses import CreateTaskResponse
from src.presentation.responses import GetTaskResultResponse
from src.presentation.responses import GetTaskStatusResponse
from src.utils.http_constants import HTTP_CODE_401_MESSAGE
from src.utils.http_constants import HTTP_CODE_403_MESSAGE
from src.utils.http_constants import HTTP_CODE_500_MESSAGE

logger = logging.getLogger(__name__)

TASK_415_MESSAGE = "Only image files are accepted"
TASK_STATUS_404_MESSAGE = "The task with specified request uuid was not found"
TASK_RESULT_404_MESSAGE = "The task result with specified request uuid not found"


task_router = APIRouter(
    prefix="/3d-model-generation",
    tags=["Tasks"],
    responses={
        401: { "description": HTTP_CODE_401_MESSAGE },
        403: { "description": HTTP_CODE_403_MESSAGE },
    }
)


@task_router.post(
    path="/tasks",
    description="Upload input image for generating 3d model",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateTaskResponse,
    responses={
        415: {"description": TASK_415_MESSAGE},
    },
)
async def create_task(
    task_source_file: UploadFile,
    access_token: str = Header(),
    task_controller: TaskController = Depends(TaskControllerImpl),
    authorization_controller: AuthorizationController = Depends(AuthorizationControllerImpl),
):
    token_validation_result = await authorization_controller.validate_token(access_token, TokenType.ACCESS)
    if token_validation_result.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=token_validation_result.status_code,
            detail=token_validation_result.detail,
        )

    if "image" not in task_source_file.content_type:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=TASK_415_MESSAGE,
        )

    try:
        task_response = await task_controller.create_task(
            user_id=token_validation_result.token_payload.user_id,
            input_file=task_source_file,
            client_type=TaskClientType.WEB_SERVICE,
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=HTTP_CODE_500_MESSAGE,
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=task_response.model_dump(),
    )


@task_router.get(
    path="/tasks/{task_request_uuid}/status",
    description="Get task status",
    status_code=status.HTTP_200_OK,
    response_model=GetTaskStatusResponse,
    response_description=f"Possible status values: {list(map(str, TaskStatus.values()))}",
    responses={
        404: { "description": TASK_STATUS_404_MESSAGE },
    },
)
async def get_task_status(
    task_request_uuid: str,
    access_token: str = Header(),
    task_controller: TaskController = Depends(TaskControllerImpl),
    authorization_controller: AuthorizationController = Depends(AuthorizationControllerImpl),
):
    token_validation_result = await authorization_controller.validate_token(access_token, TokenType.ACCESS)
    if token_validation_result.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=token_validation_result.status_code,
            detail=token_validation_result.detail,
        )

    try:
        task_status = await task_controller.get_task_status(
            task_request_uuid=uuid.UUID(task_request_uuid),
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=HTTP_CODE_500_MESSAGE,
        )

    if task_status is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The task with request uuid {task_request_uuid} not found",
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=task_status.model_dump(),
    )


@task_router.get(
    path="/tasks/{task_request_uuid}/result",
    description="Get task result as url to 3d model",
    status_code=status.HTTP_200_OK,
    response_model=GetTaskResultResponse,
    response_description="Returns URL to S3 storage",
    responses={
        404: { "description": TASK_RESULT_404_MESSAGE },
    },
)
async def get_task_result(
    task_request_uuid: str,
    access_token: str = Header(),
    task_controller: TaskController = Depends(TaskControllerImpl),
    authorization_controller: AuthorizationController = Depends(AuthorizationControllerImpl),
):
    token_validation_result = await authorization_controller.validate_token(access_token, TokenType.ACCESS)
    if token_validation_result.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=token_validation_result.status_code,
            detail=token_validation_result.detail,
        )

    try:
        task_result = await task_controller.get_task_result(
            task_request_uuid=uuid.UUID(task_request_uuid),
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=HTTP_CODE_500_MESSAGE,
        )

    if task_result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The task result with request uuid {task_request_uuid} not found"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=task_result.model_dump(),
    )
