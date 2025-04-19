import logging
import uuid

from fastapi import APIRouter
from fastapi import Depends
from fastapi import HTTPException
from fastapi import UploadFile
from fastapi import status
from starlette.responses import JSONResponse

from src.domain.controllers import TaskController
from src.domain.controllers import TaskControllerImpl
from src.domain.entities import TaskStatus
from src.presentation.responses import CreateTaskResponse
from src.presentation.responses import GetTaskResultResponse
from src.presentation.responses import GetTaskStatusResponse

logger = logging.getLogger(__name__)

integrations_router = APIRouter(
    prefix="/integrations",
    tags=["Integrations"],
)

mesh_generation_integrations_router = APIRouter(
    prefix="/3d-model-generation",
)

@mesh_generation_integrations_router.post(
    path="/tasks",
    description="Upload input image for generating 3d model",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateTaskResponse,
)
async def create_task(
    task_source_file: UploadFile,
    task_controller: TaskController = Depends(TaskControllerImpl),
):
    try:
        task_response = await task_controller.create_task(
            user_id=None,
            input_file=task_source_file,
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong",
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=task_response.model_dump(),
    )

@mesh_generation_integrations_router.get(
    path="/tasks/{task_request_uuid}/status",
    description="Get task status",
    status_code=status.HTTP_200_OK,
    response_model=GetTaskStatusResponse,
    response_description=f"Possible status values: {list(map(str, TaskStatus.values()))}"
)
async def get_task_status(
    task_request_uuid: str,
    task_controller: TaskController = Depends(TaskControllerImpl),
):
    try:
        task_status = await task_controller.get_task_status(
            task_request_uuid=uuid.UUID(task_request_uuid),
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong"
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

@mesh_generation_integrations_router.get(
    path="/tasks/{task_request_uuid}/result",
    description="Get task result as url to 3d model",
    status_code=status.HTTP_200_OK,
    response_model=GetTaskResultResponse,
)
async def get_task_result(
    task_request_uuid: str,
    task_controller: TaskController = Depends(TaskControllerImpl),
):
    try:
        task_result = await task_controller.get_task_result(
            task_request_uuid=uuid.UUID(task_request_uuid),
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong"
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
