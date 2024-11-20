package apiroutes

import (
	_ "3d-avatar/backend-main/src/domain/dtos"
	"3d-avatar/backend-main/src/presentation/controllers"

	"github.com/labstack/echo/v4"
)

func SetupPostRoutes(
	router *echo.Group,
	mediaController controllers.Generate3dModelController,
) {
	uploadInputImage(router, mediaController)
}

// @Summary		Upload input image for generating 3d model
// @ID			3d-model-generation-post-input-image
// @Accept		multipart/form-data
// @Produce		json
// @Param		image	formData	file	true	"Input image"
// @Success		200		{object}	dtos.UploadInputImageResponse
// @Router		/v1/3d-model-generation/input-image [post]
func uploadInputImage(
	router *echo.Group,
	mediaController controllers.Generate3dModelController,
) {
	router.POST(
		"/3d-model-generation/input-image",
		mediaController.UploadInputImage,
	)
}
