package logger

import (
	"context"
	"errors"

	"github.com/jackc/pgerrcode"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/labstack/echo/v4"
)

const (
	startDataBaseQuery = "start database query"
	endDataBaseQuery   = "end database query"
)

type PgLogger struct {
	Logger echo.Logger
}

func NewPgxLogger(logger echo.Logger) *PgLogger {
	return &PgLogger{
		Logger: logger,
	}
}

func (p *PgLogger) TraceQueryStart(
	ctx context.Context,
	conn *pgx.Conn,
	data pgx.TraceQueryStartData,
) context.Context {

	p.Logger.Info(startDataBaseQuery, data.SQL)
	return ctx
}

func (p *PgLogger) TraceQueryEnd(
	ctx context.Context,
	conn *pgx.Conn,
	data pgx.TraceQueryEndData,
) {
	var e *pgconn.PgError

	if data.Err != nil {
		if errors.As(data.Err, &e) && e.Code == pgerrcode.UniqueViolation {
			p.Logger.Warn(endDataBaseQuery, data.Err)
			return
		}
		p.Logger.Error(endDataBaseQuery, data.Err)
	}

	p.Logger.Info(endDataBaseQuery, data.CommandTag.String())
}
