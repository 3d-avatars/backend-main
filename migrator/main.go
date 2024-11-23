package main

import (
	"3d-avatar/backend-main/src/configs"
	"errors"
	"fmt"
	"log"

	"github.com/golang-migrate/migrate/v4"
	_ "github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file"
)

func main() {

	cfg, err := configs.New()
	if err != nil {
		log.Fatalf("Config is required: %v", err)
	}

	log.Printf("Trying to migrate from %s to %s\n", cfg.DatabaseCfg.MigrationsPath, cfg.DatabaseCfg.PostgresUrl)

	migrator, err := migrate.New(
		fmt.Sprintf("file://%s", cfg.DatabaseCfg.MigrationsPath),
		fmt.Sprintf("%s?x-migrations-table=%s&sslmode=disable",
			cfg.DatabaseCfg.PostgresUrl,
			cfg.DatabaseCfg.MigrationsTable,
		),
	)
	if err != nil {
		log.Fatalf("Failed to create migrations: %v", err)
	}

	if err := migrator.Up(); err != nil {
		if errors.Is(err, migrate.ErrNoChange) {
			fmt.Println("No migrations to apply")
			return
		}
		log.Fatal(err)
	}

	log.Println("Migrations successfully applied")
}
