package apiroutes

import (
	"3d-avatar/backend-main/src/controllers"
	_ "3d-avatar/backend-main/src/dtos"

	"github.com/labstack/echo/v4"
)

func SetupPostRoutes(
	router *echo.Group,
	mediaController controllers.MediaController,
) {
	uploadImage(router, mediaController)
}

//	@Summary	Upload input image for generating 3d model
//	@ID			3d-model-generation-post-input-image
//	@Accept		multipart/form-data
//	@Produce	json
//	@Param		image	formData	file	true	"Input image"
//	@Success	200		{object}	dtos.MediaDto
//	@Router		/v1/3d-model-generation/input-image [post]
func uploadImage(
	router *echo.Group,
	mediaController controllers.MediaController,
) {
	router.POST(
		"/3d-model-generation/input-image",
		mediaController.FileUpload,
	)
}
