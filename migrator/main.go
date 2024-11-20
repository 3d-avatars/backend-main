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

	log.Printf("Tring to migrate from %s to %s\n", cfg.DatabaseCfg.MigrationsPath, cfg.DatabaseCfg.PGUrl)

	m, err := migrate.New(
		fmt.Sprintf("file://%s", cfg.DatabaseCfg.MigrationsPath),
		fmt.Sprintf("%s?x-migrations-table=%s&sslmode=disable",
			cfg.DatabaseCfg.PGUrl,
			cfg.DatabaseCfg.MigrationsTable,
		),
	)

	if err != nil {
		log.Fatalf("failed to create migrations: %v", err)
	}

	if err := m.Up(); err != nil {
		if errors.Is(err, migrate.ErrNoChange) {
			fmt.Println("no migrations to apply")
			return
		}
		log.Fatal(err)
	}

	log.Println("migrations successfully applied")
}
