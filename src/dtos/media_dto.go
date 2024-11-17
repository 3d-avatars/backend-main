package dtos

import (
	"github.com/labstack/echo/v4"
)

type MediaDto struct {
	Message string    `json:"message"`
	Data    *echo.Map `json:"data"`
}
