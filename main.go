package main

import (
	_ "3d-avatar/backend-main/docs"
	apiRoutes "3d-avatar/backend-main/src/api-routes"
	"3d-avatar/backend-main/src/controllers"
	"3d-avatar/backend-main/src/services"
	"fmt"
	"github.com/swaggo/echo-swagger"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"github.com/labstack/gommon/log"
)

const (
	BaseUrl = "3d-avatar/api"
	ApiV1   = "v1"
)

//	@title			3D Avatar API
//	@version		1.0
//	@license.name	Apache 2.0
//	@BasePath		/3d-avatar/api
func main() {
	router := echo.New()

	router.Logger.SetLevel(log.ERROR)
	router.Use(middleware.Logger())

	baseUrlRouter := router.Group(fmt.Sprintf("/%s", BaseUrl))
	apiV1Router := baseUrlRouter.Group(fmt.Sprintf("/%s", ApiV1))

	setupSwagger(baseUrlRouter)
	setupHandlers(apiV1Router)

	router.Logger.Fatal(router.Start(":8080"))
}

func setupSwagger(router *echo.Group) {
	router.GET("/swagger/*", echoSwagger.WrapHandler)
}

func setupHandlers(router *echo.Group) {
	mediaService := services.NewMediaUpload()
	mediaController := controllers.NewMediaController(mediaService)

	apiRoutes.SetupGetRoutes(router)
	apiRoutes.SetupPostRoutes(router, mediaController)
}
