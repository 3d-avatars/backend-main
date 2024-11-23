package configs

import (
	"fmt"

	"github.com/ilyakaznacheev/cleanenv"
)

type AppConfig struct {
	ServerCfg   ServerConfig
	DatabaseCfg DatabaseConfig
	QueueCfg    QueueConfig
}

type ServerConfig struct {
	Host string `env:"APP_HOST" env-required:"true"`
	Port int    `env:"APP_PORT" env-required:"true"`
}

type DatabaseConfig struct {
	PostgresUrl     string `env:"PG_URL" env-required:"true"`
	MigrationsPath  string `env:"MIGRATIONS_PATH" env-required:"true"`
	MigrationsTable string `env:"MIGRATIONS_TABLE" env-required:"true"`
}

type QueueConfig struct {
	RabbitMqUrl       string `env:"RABBITMQ_URL" env-required:"true"`
	TasksQueue        string `env:"RABBITMQ_TASKS_QUEUE" env-required:"true"`
	TasksResultsQueue string `env:"RABBITMQ_TASKS_RESULTS_QUEUE" env-required:"true"`
}

func New() (*AppConfig, error) {
	var cfg AppConfig

	if err := cleanenv.ReadEnv(&cfg); err != nil {
		return nil, fmt.Errorf("error while reading env: %w", err)
	}

	return &cfg, nil
}
