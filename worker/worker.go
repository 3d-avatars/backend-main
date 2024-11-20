package main

import (
	"3d-avatar/backend-main/src/configs"
	"3d-avatar/backend-main/src/data/database"
	"3d-avatar/backend-main/src/data/rabbitmq"
	"context"

	"github.com/labstack/echo/v4"
	"github.com/labstack/gommon/log"
	amqp "github.com/rabbitmq/amqp091-go"
)

type WorkerRabbitMqRepository interface {
	ReceiveResults(resultsCh *chan []byte)
}

type WorkerDatabaseRepository interface {
	UpdateTaskWithFilePath(ctx context.Context, uuid *string, filePath *string) error
}

type Worker struct {
	DatabaseRepository WorkerDatabaseRepository
	RabbitMqRepository WorkerRabbitMqRepository
	Connection *amqp.Connection
	logger echo.Logger
}

func NewRabbitWorker(cfg *configs.AppConfig, logger echo.Logger) *Worker {
	db, err := database.CreateDBConnection(cfg.DatabaseCfg.PGUrl, logger)
	if err != nil {
		log.Fatal("Failed to create db connection")
	}

	databaseRepository := database.NewDatabaseRepository(db)
	rabbitMqRepository := rabbitmq.NewRabbitMqRepository(cfg.QueueCfg)

	if err != nil {
		log.Fatalf("Failed to create connection with rabbitmq: %v", err)
	}

	return &Worker{
		DatabaseRepository: databaseRepository,
		RabbitMqRepository: rabbitMqRepository,
		Connection: rabbitMqRepository.Connection(),
		logger: logger,
	}
}
