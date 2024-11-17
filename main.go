package main

import (
	"net/http"
	
	"github.com/labstack/echo/v4"
)

func main() {
	e := echo.New()
	e.GET("/", getHelloWorld)
	e.Logger.Fatal(e.Start(":1323"))
}

func getHelloWorld(ctx echo.Context) error {
	return ctx.String(http.StatusOK, "{\"hello\": \"Hello, World!\"}")
}
