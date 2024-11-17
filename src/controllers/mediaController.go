package controllers

import (
	"3d-avatar/backend-main/src/dtos"
	"3d-avatar/backend-main/src/models"
	"3d-avatar/backend-main/src/services"
	"net/http"

	"github.com/labstack/echo/v4"
)

type MediaController interface {
	FileUpload(ctx echo.Context) error
}

type mediaController struct {
	MediaUpload services.MediaUpload
}

func NewMediaController(service services.MediaUpload) MediaController {
	return &mediaController{
		MediaUpload: service,
	}
}

func (controller *mediaController) FileUpload(ctx echo.Context) error {
	fileHeader, err := ctx.FormFile("image")
	if err != nil {
		return ctx.JSON(
			http.StatusInternalServerError,
			&dtos.MediaDto{
				Message: "The data type expected to be an image",
			},
		)
	}

	file, err := fileHeader.Open()
	if err != nil {
		return ctx.JSON(
			http.StatusInternalServerError,
			&dtos.MediaDto{
				Message: "Failed to retrieve file from header",
			},
		)
	}
	defer file.Close()

	mediaFile := models.MediaFile{
		Filename: fileHeader.Filename,
		File:     file,
	}

	if err := controller.MediaUpload.FileUpload(&mediaFile); err != nil {
		return ctx.JSON(
			http.StatusInternalServerError,
			&dtos.MediaDto{
				Message: "An internal server error occured when saving the image.",
			},
		)
	}

	return ctx.JSON(
		http.StatusOK,
		&dtos.MediaDto{
			Message: "Image uploaded successfully",
		},
	)
}
