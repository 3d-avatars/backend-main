package main

import (
	"3d-avatar/backend-main/src/configs"
	"3d-avatar/backend-main/src/data/rabbitmq"
	"context"
	"encoding/json"
	"fmt"
	"os"

	"github.com/labstack/echo/v4"
	"github.com/labstack/gommon/log"
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
	resultsCh := make(chan []byte)

	go func() {
		for bytes := range resultsCh {
			var response rabbitmq.RabbitResponse
			if err := json.Unmarshal(bytes, &response); err != nil {
				logger.Fatalf("Failed to unmarshal json")
			}

			workDir, err := os.Getwd()
			if err != nil {
				logger.Fatalf("Failed to get current working directory")
			}
			path := fmt.Sprintf("%s/imaginary-database/%s-%s", workDir, response.Filename, response.Datetime)

			err = os.WriteFile(
				path,
				response.File,
				0644,
			)
			if err != nil {
				logger.Fatalf("Failed to write response for file %s-%s", response.Filename, response.Datetime)
			}

			worker.DatabaseRepository.UpdateTaskWithFilePath(ctx, &response.Uuid, &path)
		}

		worker.RabbitMqRepository.ReceiveResults(&resultsCh)
	}()
}
