package apiroutes

import (
	_ "3d-avatar/backend-main/src/domain/dtos"
	"3d-avatar/backend-main/src/presentation/controllers"

	"github.com/labstack/echo/v4"
)

func SetupGetRoutes(
	router *echo.Group,
	mediaController controllers.Generate3dModelController,
) {
	getTaskStatus(router, mediaController)
	getResultFile(router, mediaController)
}

// @Summary		Get status of generating 3d model task
// @ID			3d-model-generation-task-status
// @Accept		json
// @Produce		json
// @Param		id	path	string	true	"UUID of task generated after uploading input image"
// @Success		200		{object}	dtos.GetTaskStatusResponse
// @Router		/v1/3d-model-generation/task/:id/status [get]
func getTaskStatus(
	router *echo.Group,
	mediaController controllers.Generate3dModelController,
) {
	router.GET(
		"/3d-model-generation/task/:id/status",
		mediaController.GetTaskStatus,
	)
}

// @Summary		Get result .glb file
// @ID			3d-model-generation-get-result-file
// @Accept		json
// @Produce		model/gltf-binary
// @Param		id	path	string	true	"UUID of task generated after uploading input image"
// @Success		200		{file}	file
// @Router		/v1/3d-model-generation/task/:id/result [get]
func getResultFile(
	router *echo.Group,
	mediaController controllers.Generate3dModelController,
) {
	router.GET(
		"/3d-model-generation/task/:id/result",
		mediaController.GetTaskResultFile,
	)
}
