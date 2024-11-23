package controllers

import (
	"3d-avatar/backend-main/src/domain/dtos"
	"3d-avatar/backend-main/src/domain/services"
	"net/http"

	"github.com/labstack/echo/v4"
)

type Generate3dModelController interface {
	UploadInputImage(ctx echo.Context) error
	GetTaskStatus(ctx echo.Context) error
	GetTaskResultFile(ctx echo.Context) error
}

type meshController struct {
	mediaService services.Generate3dModelService
}

func NewGenerate3dModelController(service services.Generate3dModelService) Generate3dModelController {
	return &meshController{
		mediaService: service,
	}
}

func (controller *meshController) UploadInputImage(ctx echo.Context) error {
	fileHeader, err := ctx.FormFile("image")
	if err != nil {
		return ctx.JSON(
			http.StatusInternalServerError,
			&dtos.UploadInputImageResponse{
				Message: "The data type expected to be an image",
			},
		)
	}

	file, err := fileHeader.Open()
	if err != nil {
		return ctx.JSON(
			http.StatusInternalServerError,
			&dtos.UploadInputImageResponse{
				Message: "Failed to retrieve file",
			},
		)
	}
	defer file.Close()

	fileContent := make([]byte, fileHeader.Size)
	if _, err := file.Read(fileContent); err != nil {
		return ctx.JSON(
			http.StatusInternalServerError,
			&dtos.UploadInputImageResponse{
				Message: "Failed to read file content",
			},
		)
	}

	requestUuid, err := controller.mediaService.UploadFile(
		ctx.Request().Context(),
		&fileContent,
		&fileHeader.Filename,
	)

	if err != nil {
		return ctx.JSON(
			http.StatusInternalServerError,
			&dtos.UploadInputImageResponse{
				Message: "An internal server error occured while processing the image.",
			},
		)
	}

	return ctx.JSON(
		http.StatusOK,
		&dtos.UploadInputImageResponse{
			Message:     "Image uploaded successfully",
			RequestUuid: requestUuid,
		},
	)
}

func (controller *meshController) GetTaskStatus(ctx echo.Context) error {
	taskUuid := ctx.Param("id")

	state, err := controller.mediaService.GetTaskStatus(ctx.Request().Context(), &taskUuid)
	if err != nil {
		return ctx.JSON(
			http.StatusInternalServerError,
			&dtos.GetTaskStatusResponse{
				Message: "Failed to retrieve task status",
			},
		)
	}

	return ctx.JSON(
		http.StatusOK,
		&dtos.GetTaskStatusResponse{
			Message: "Task status retrieved successfully",
			Status:  state,
		},
	)
}

func (controller *meshController) GetTaskResultFile(ctx echo.Context) error {
	taskUuid := ctx.Param("id")

	resultFilePath, err := controller.mediaService.GetResultFilePath(ctx.Request().Context(), &taskUuid)
	if err != nil {
		return ctx.JSON(
			http.StatusInternalServerError,
			&dtos.GetResultFileResponse{
				Message: "Failed to read file",
			},
		)

	}

	return ctx.File(resultFilePath)
}
