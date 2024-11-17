package main

import (
	"3d-avatar/backend-main/src/controllers"
	"3d-avatar/backend-main/src/services"
	"fmt"
	"net/http"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"github.com/labstack/gommon/log"
)

const (
	BaseUrl = "3d-avatar/api"
	ApiV1   = "v1"
)

func main() {
	router := echo.New()

	router.Logger.SetLevel(log.ERROR)
	router.Use(middleware.Logger())

	setupHandlers(router)

	router.Logger.Fatal(router.Start(":5656"))
}

func setupHandlers(router *echo.Echo) {
	mediaService := services.NewMediaUpload()
	mediaController := controllers.NewMediaController(mediaService)

	setupGetRoutes(router)
	setupPostRoutes(router, mediaController)
}

func setupGetRoutes(router *echo.Echo) {
	router.GET(
		fmt.Sprintf("%s/%s", BaseUrl, ApiV1), 
		getHelloWorld,
	)
}

func setupPostRoutes(
	router *echo.Echo,
	mediaController controllers.MediaController,
) {
	router.POST(
		fmt.Sprintf("%s/%s/3d-model-generation/input-image", BaseUrl, ApiV1),
		mediaController.FileUpload,
	)
}

func getHelloWorld(ctx echo.Context) error {
	return ctx.String(http.StatusOK, "{\"hello\": \"Hello, World!\"}")
}
