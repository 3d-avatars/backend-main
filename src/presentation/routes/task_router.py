import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi import UploadFile
from fastapi.responses import JSONResponse

from src.domain.entities import TaskStatus
from src.domain.services import TaskController, TaskControllerImpl
from src.presentation.responses import GetTaskStatusResponse, GetTaskResultResponse, CreateTaskResponse

logger = logging.getLogger(__name__)

task_router = APIRouter(
    prefix="/3d-model-generation",
    tags=["Tasks"],
)

@task_router.post(
    path="/tasks",
    description="Upload input image for generating 3d model. Post tasks",
    status_code=status.HTTP_201_CREATED,
    response_model=CreateTaskResponse,
)
async def create_task(
    task_source_file: UploadFile,
    task_controller: TaskController = Depends(TaskControllerImpl),
):
    try:
        task_response = await task_controller.create_task(task_source_file)
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong"
        )

    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content= task_response.model_dump()
    )


@task_router.get(
    path="/tasks/{task_request_uuid}/status",
    description="Get task status",
    status_code=status.HTTP_200_OK,
    response_model=GetTaskStatusResponse,
    response_description=f'Possible status values: {list(map(str, TaskStatus.values()))}'
)
async def get_task_status(
    task_request_uuid: str,
    task_controller: TaskController = Depends(TaskControllerImpl)
):
    try:
        task_status = await task_controller.get_task_status(
            task_request_uuid=uuid.UUID(task_request_uuid),
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong"
        )

    if not task_status:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The task with request uuid {task_request_uuid} not found",
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=GetTaskStatusResponse(
            status = task_status,
        ).model_dump(),
    )


@task_router.get(
    path="/tasks/{task_request_uuid}/result",
    description="Get tasks result as a .glb file",
    status_code=status.HTTP_200_OK,
    response_model=GetTaskResultResponse,
    response_description="Returns URL to S3 storage"
)
async def get_task_result(
    task_request_uuid: str,
    task_controller: TaskController = Depends(TaskControllerImpl)
):
    try:
        task_result = await task_controller.get_task_result(
            task_request_uuid=uuid.UUID(task_request_uuid),
        )
    except Exception as e:
        logger.exception(e)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong"
        )

    if not task_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The task result with requiest uuid {task_request_uuid} not found"
        )

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=GetTaskResultResponse(
            result_file_path=task_result,
        ).model_dump(),
    )
