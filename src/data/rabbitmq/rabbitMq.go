package rabbitmq

import (
	"3d-avatar/backend-main/src/configs"
	"fmt"

	amqp "github.com/rabbitmq/amqp091-go"
)

func setupRMQ(cfg configs.QueueConfig) (RabbitMqRepository, error) {
	connection, err := amqp.Dial(
		fmt.Sprintf("amqp://%s:%s@%s:%s/", cfg.User, cfg.Password, cfg.Host, cfg.Port),
	)
	if err != nil {
		return nil, fmt.Errorf("failed create connection to rabbitmq: %w", err)
	}

	ch, err := connection.Channel()
	if err != nil {
		return nil, fmt.Errorf("failed create channel for queue declaring %w", err)
	}
	defer ch.Close()

	queueNames := []string{cfg.TasksQueue, cfg.TasksResultsQueue}
	for _, name := range queueNames {
		_, err := declareQueue(ch, &name)
		if err != nil {
			return nil, fmt.Errorf("failed declare queue for %s: %w", name, err)
		}
	}

	return &rabbitMqRepository{
		connection:       connection,
		tasksQueue:       cfg.TasksQueue,
		tasksResultQueue: cfg.TasksResultsQueue,
	}, nil
}

func declareQueue(ch *amqp.Channel, queueName *string) (amqp.Queue, error) {
	return ch.QueueDeclare(
		*queueName,
		false,
		false,
		false,
		false,
		nil,
	)
}
