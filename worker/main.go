package main

import (
	"3d-avatar/backend-main/src/configs"
	"3d-avatar/backend-main/src/data/rabbit"
	"context"
	"encoding/json"
	"fmt"
	"os"
	"os/signal"
	"strings"
	"syscall"

	"3d-avatar/backend-main/src/data/database"

	"github.com/labstack/echo/v4"
	"github.com/labstack/gommon/log"
	amqp "github.com/rabbitmq/amqp091-go"
)

func main() {
	config, err := configs.New()
	if err != nil {
		log.Fatalf("Failed to create config: %v", err)
	}

	logger := echo.New().Logger
	logger.SetLevel(log.INFO)
	logger.SetHeader("${time_rfc3339} ${level} WORKER")

	worker := NewRabbitWorker(config, logger)
	defer worker.Connection.Close()

	ctx := context.Background()

	ctx, cancel := signal.NotifyContext(ctx, syscall.SIGTERM, syscall.SIGINT)
	defer cancel()

	go func() {
		resultsCh, err := worker.RabbitMqRepository.ReceiveResults()
		if err != nil {
			log.Fatalf("Failed to consume from queue: %w", err)
		}

		for msg := range resultsCh {
			var response rabbit.RabbitResponse

			if err := json.Unmarshal(msg.Body, &response); err != nil {
				logger.Error("Failed to unmarshal json")
			} else {
				path := fmt.Sprintf(
					"/mnt/backend-shared/imaginary-database/%s-%s.glb",
					strings.Split(response.Filename, ".")[0],
					response.Datetime,
				)
				log.Printf("HEEEEEELLLLLLLOOOOO %s", path)

				err = os.WriteFile(
					path,
					response.FileContent,
					0644,
				)
				if err != nil {
					logger.Fatalf("Failed to write response for file %s-%s", response.Filename, response.Datetime)
				}

				worker.DatabaseRepository.UpdateTaskWithFilePath(ctx, &response.Uuid, &path)
			}
		}
	}()

	log.Printf(" [*] Worker is waiting for messages.")
	<-ctx.Done()
}

type WorkerRabbitMqRepository interface {
	ReceiveResults() (<-chan amqp.Delivery, error)
}

type WorkerDatabaseRepository interface {
	UpdateTaskWithFilePath(ctx context.Context, uuid *string, filePath *string) error
}

type Worker struct {
	DatabaseRepository WorkerDatabaseRepository
	RabbitMqRepository WorkerRabbitMqRepository
	Connection         *amqp.Connection
	logger             echo.Logger
}

func NewRabbitWorker(cfg *configs.AppConfig, logger echo.Logger) *Worker {
	db, err := database.CreateDBConnection(cfg.DatabaseCfg.PostgresUrl, logger)
	if err != nil {
		log.Fatal("Failed to create db connection")
	}

	databaseRepository := database.NewDatabaseRepository(db)
	rabbitMqRepository := rabbit.NewRabbitMqRepository(cfg.QueueCfg, "worker")

	if err != nil {
		log.Fatalf("Failed to create connection with rabbitmq: %v", err)
	}

	return &Worker{
		DatabaseRepository: databaseRepository,
		RabbitMqRepository: rabbitMqRepository,
		Connection:         rabbitMqRepository.Connection(),
		logger:             logger,
	}
}
