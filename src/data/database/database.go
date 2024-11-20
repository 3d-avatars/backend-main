package database

import (
	"3d-avatar/backend-main/src/data/database/logger"
	"fmt"

	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/stdlib"
	"github.com/jmoiron/sqlx"
	"github.com/labstack/echo/v4"
)

const driverName = "pgx"

func CreateDBConnection(url string, log echo.Logger) (*sqlx.DB, error) {

	pgCfg, err := pgx.ParseConfig(url)
	if err != nil {
		return nil, fmt.Errorf("failed to parse postgres config: %w", err)
	}

	pgLog := logger.NewPgxLogger(log)
	pgCfg.Tracer = pgLog

	nativeDB := stdlib.OpenDB(*pgCfg)

	nativeDB.SetMaxOpenConns(10)
	nativeDB.SetMaxIdleConns(5)

	return sqlx.NewDb(nativeDB, driverName), nil

}
