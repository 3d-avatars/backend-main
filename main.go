package main

import (
	_ "3d-avatar/backend-main/docs"
	"3d-avatar/backend-main/src/configs"
	"3d-avatar/backend-main/src/data/database"
	"3d-avatar/backend-main/src/data/rabbit"
	"3d-avatar/backend-main/src/domain/services"
	apiRoutes "3d-avatar/backend-main/src/presentation/api-routes"
	"3d-avatar/backend-main/src/presentation/controllers"
	"fmt"

	echoSwagger "github.com/swaggo/echo-swagger"

	"github.com/labstack/echo/v4"
	"github.com/labstack/echo/v4/middleware"
	"github.com/labstack/gommon/log"
)

const (
	BaseUrl = "/3d-avatar/api"
	ApiV1   = "/v1"
)

// @title			3D Avatar API
// @version		1.0
// @license.name	Apache 2.0
// @BasePath		/3d-avatar/api
func main() {
	config, err := configs.New()
	if err != nil {
		log.Fatalf("Failed to create config: %v", err)
	}

	router := echo.New()

	router.Logger.SetLevel(log.INFO)
	router.Logger.SetHeader("${time_rfc3339} ${level} BACKEND")
	router.Use(middleware.Logger())

	baseUrlRouter := router.Group(BaseUrl)
	apiV1Router := baseUrlRouter.Group(ApiV1)

	setupSwagger(baseUrlRouter)
	setupHandlers(config, apiV1Router, router.Logger)

	router.Logger.Fatal(
		router.Start(
			fmt.Sprintf("%s:%d", config.ServerCfg.Host, config.ServerCfg.Port),
		),
	)
}

func setupSwagger(router *echo.Group) {
	router.GET("/swagger/*", echoSwagger.WrapHandler)
}

func setupHandlers(
	config *configs.AppConfig,
	router *echo.Group,
	logger echo.Logger,
) {
	db, err := database.CreateDBConnection(config.DatabaseCfg.PostgresUrl, logger)
	if err != nil {
		logger.Fatal("Failed to create postgres connectin: %v", err)
	}

	databaseRepository := database.NewDatabaseRepository(db)
	rabbitMqRepository := rabbit.NewRabbitMqRepository(config.QueueCfg, "backend-main")

	mediaService := services.NewGenerate3dModelService(databaseRepository, rabbitMqRepository)
	mediaController := controllers.NewGenerate3dModelController(mediaService)

	apiRoutes.SetupGetRoutes(router, mediaController)
	apiRoutes.SetupPostRoutes(router, mediaController)
}
