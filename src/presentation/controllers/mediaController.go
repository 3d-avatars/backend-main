package controllers

import (
	"3d-avatar/backend-main/src/domain/dtos"
	"3d-avatar/backend-main/src/domain/services"
	"net/http"

	"github.com/labstack/echo/v4"
)

type MediaController interface {
	UploadInputImage(ctx echo.Context) error
	GetTaskStatus(ctx echo.Context) error
	GetTaskResultFile(ctx echo.Context) error
}

type mediaController struct {
	mediaService services.MediaService
}

func NewMediaController(service services.MediaService) MediaController {
	return &mediaController{
		mediaService: service,
	}
}

func (controller *mediaController) UploadInputImage(ctx echo.Context) error {
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

	requestUuid, err := controller.mediaService.UploadFile(ctx.Request().Context(), &file)

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

func (controller *mediaController) GetTaskStatus(ctx echo.Context) error {
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

func (controller *mediaController) GetTaskResultFile(ctx echo.Context) error {
	taskUuid := ctx.Param("id")

	resultFilePath, err := controller.mediaService.
		GetResultFilePath(ctx.Request().Context(), &taskUuid)
	if err != nil {

	}

	return ctx.File(resultFilePath)
}
