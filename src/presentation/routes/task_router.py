import typing
import uuid

from fastapi import APIRouter, Depends, HTTPException, status, Query, Header
from fastapi import UploadFile

from fastapi.responses import JSONResponse, RedirectResponse

from src.schemas.task_schema import (
    Task,
    TaskFilter,
    TaskStateUpdateRequest
)

from src.services import BaseService, TaskService
from src.enums import TaskStatus


router = APIRouter(
    prefix='/3d-model-generation',
    tags=['task'],
)


@router.get(
    '/',
    status_code=status.HTTP_200_OK,
    response_model=typing.List[Task],
)
async def get_task_list(
        task_filter: typing.Annotated[TaskFilter, Query()],
        task_service: BaseService = Depends(TaskService),
):
    tasks = await task_service.get(task_filter)
    return list(map(Task.from_orm, tasks))


@router.get(
    '/{task_id}',
    status_code=status.HTTP_200_OK,
    response_model=Task,
)
async def get_task(
        task_id: int,
        task_service: BaseService = Depends(TaskService),
):
    task = await task_service.get_single(task_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    return task


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=Task,
    description="Upload input image for generating 3d model. Post task",
)
async def create_task(
        task_source_file: UploadFile,
        x_request_id: typing.Annotated[uuid.UUID, Header()],
        task_service: BaseService = Depends(TaskService),
):
    new_task = await task_service.create(
        x_request_id,
        task_source_file,
    )
    return new_task


@router.patch(
    '/{task_id}/state',
    status_code=status.HTTP_200_OK,
    description="Update generating status of task",
)
async def update_task_status(
        task_id: int,
        task_state_payload: TaskStateUpdateRequest,
        task_service: BaseService = Depends(TaskService),
):
    return await task_service.update(
        task_id,
        task_state_payload,
    )


@router.get(
    '/{task_id}/result',
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    description="Get task state",
)
async def get_task_status(task_id: int, task_service: BaseService = Depends(TaskService)):
    task = await task_service.get_single(task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"The task {task_id} not found"
        )

    if task.state == TaskStatus.FAILED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The generation has been failed.",
        )

    if task.state != TaskStatus.SUCCESS and not task.result_file_path:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The resulting 3d model has not yet been generated.",
        )

    return RedirectResponse(url=task.result_file_path)


@router.get(
    '/{task_id}/state',
    status_code=status.HTTP_200_OK,
    description="Get task result as a .glb file",
)
async def get_task_result(task_id: int, task_service: BaseService = Depends(TaskService)):
    task = await task_service.get_single(task_id=task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return JSONResponse(status_code=status.HTTP_200_OK, content={
        "state": task.state,
    })


@router.delete(
    '/{task_id}',
    status_code=status.HTTP_204_NO_CONTENT,
    description="Delete task, source and result files",
)
async def delete_task(task_id: int, task_service: BaseService = Depends(TaskService)):
    return await task_service.delete(task_id)
