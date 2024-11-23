package database

import (
	dberrors "3d-avatar/backend-main/src/data/database/db-errors"
	"context"
	"database/sql"
	"errors"
	"fmt"

	"github.com/jmoiron/sqlx"
)

type DatabaseRepository interface {
	InsertTask(ctx context.Context, task *TaskEntity) error
	UpdateTaskWithFilePath(ctx context.Context, uuid *string, filePath *string) error
	GetTaskStatus(ctx context.Context, uuid *string) (TaskState, error)
	GetResultFilePath(ctx context.Context, uuid *string) (string, error)
}

type databaseRepository struct {
	db *sqlx.DB
}

func NewDatabaseRepository(db *sqlx.DB) DatabaseRepository {
	return &databaseRepository{
		db: db,
	}
}

func (repo *databaseRepository) InsertTask(
	ctx context.Context,
	task *TaskEntity,
) error {
	const insertTaskQuery = `
	INSERT INTO tasks (request_uuid, datetime, state, result_file_path) VALUES ($1, $2, $3, $4)
	`
	_, err := repo.db.ExecContext(
		ctx,
		insertTaskQuery,
		task.RequestUuid,
		task.Datetime,
		task.State,
		task.ResultFilePath,
	)
	if err != nil {
		return fmt.Errorf("failed to insert task: %w", err)
	}
	return nil
}

func (repo *databaseRepository) UpdateTaskWithFilePath(
	ctx context.Context,
	uuid *string,
	filePath *string,
) error {
	const updateTaskQuery = `
	UPDATE tasks 
	SET result_file_path = $1
	WHERE request_uuid = $2
	`
	_, err := repo.db.ExecContext(
		ctx,
		updateTaskQuery,
		filePath,
		uuid,
	)
	if err != nil {
		return fmt.Errorf("failed to update task with uuid %s and path %s", *uuid, *filePath)
	}
	return nil
}

func (repo *databaseRepository) GetTaskStatus(
	ctx context.Context,
	uuid *string,
) (TaskState, error) {
	const getTaskStatusQuery = `
	SELECT state FROM tasks
	WHERE request_uuid = $1
	`
	var taskState TaskState
	if err := repo.db.GetContext(ctx, &taskState, getTaskStatusQuery, uuid); err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return -1, dberrors.ErrTaskNotFound
		}
		return -1, fmt.Errorf("failed to get task state: %w", err)
	}
	return taskState, nil
}

func (repo *databaseRepository) GetResultFilePath(
	ctx context.Context,
	uuid *string,
) (string, error) {
	const getResultFilePathQuery = `
	SELECT result_file_path FROM tasks
	WHERE request_uuid = $1
	`
	var resultFilePath string
	if err := repo.db.GetContext(ctx, &resultFilePath, getResultFilePathQuery, uuid); err != nil {
		if errors.Is(err, sql.ErrNoRows) {
			return "", dberrors.ErrTaskNotFound
		}
		return "", fmt.Errorf("failed to get task file path: %w", err)
	}
	return resultFilePath, nil
}
