package rabbit

import (
	"3d-avatar/backend-main/src/configs"
	"context"
	"encoding/json"
	"fmt"
	"log"

	amqp "github.com/rabbitmq/amqp091-go"
)

type RabbitMqRepository interface {
	SendTask(ctx context.Context, task *RabbitTask) error
	ReceiveResults() (<-chan amqp.Delivery, error)
	Connection() *amqp.Connection
}

type rabbitMqRepository struct {
	connection       *amqp.Connection
	tasksQueue       string
	tasksResultQueue string
}

func NewRabbitMqRepository(cfg configs.QueueConfig, clientName string) RabbitMqRepository {
	repo, err := setupRMQ(cfg, clientName)
	if err != nil {
		log.Fatalf("Failed to create rabbitmq repo: %v", err)
	}
	return repo
}

func (repo *rabbitMqRepository) SendTask(ctx context.Context, task *RabbitTask) error {
	ch, err := repo.connection.Channel()
	if err != nil {
		return fmt.Errorf("failed create channel for queue declaring %w", err)
	}
	defer ch.Close()

	queue, err := declareQueue(ch, &repo.tasksQueue)
	if err != nil {
		return fmt.Errorf("failed declare queue for %s: %w", repo.tasksQueue, err)
	}

	bytes, err := json.Marshal(task)
	if err != nil {
		return fmt.Errorf("failed to convert task to bytes: %w", err)
	}

	err = ch.PublishWithContext(
		ctx,
		"",
		queue.Name,
		true,
		false,
		amqp.Publishing{
			ContentType: "application/json",
			Body:        bytes,
		},
	)
	if err != nil {
		return fmt.Errorf("failed to send task: %w", err)
	}
	return nil
}

func (repo *rabbitMqRepository) ReceiveResults() (<-chan amqp.Delivery, error) {
	ch, err := repo.connection.Channel()
	if err != nil {
		log.Fatalf("failed create channel for queue declaring %v", err)
	}
	defer ch.Close()

	queue, err := declareQueue(ch, &repo.tasksResultQueue)
	if err != nil {
		log.Fatalf("Failed declare queue for %s: %v", repo.tasksResultQueue, err)
	}

	msgs, err := ch.Consume(
		queue.Name,
		"",
		true,
		false,
		false,
		false,
		nil,
	)
	if err != nil {
		return nil, fmt.Errorf("failed to consume from queue %s: %v", repo.tasksResultQueue, err)
	}
	return msgs, nil
}

func (repo *rabbitMqRepository) Connection() *amqp.Connection {
	return repo.connection
}
