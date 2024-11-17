FROM golang:1.23.3-alpine AS builder

ENV CGO_ENABLED=0
ENV GOOS=linux

WORKDIR /build
ADD ./go.mod go.mod
ADD ./go.sum go.sum

RUN go mod download

COPY . .

RUN go build -o /app/backend-main ./main.go

FROM alpine

RUN apk update --no-cache && apk add --no-cache ca-certificates

ENV APP_PORT=8080
ENV APP_HOST=0.0.0.0

COPY --from=builder /app /app

WORKDIR /app

CMD ./backend-main
