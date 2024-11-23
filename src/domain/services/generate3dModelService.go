package services

import (
	"context"
	"os"
	"time"

	"3d-avatar/backend-main/src/data/database"
	"3d-avatar/backend-main/src/data/rabbit"

	"github.com/google/uuid"
)

type Generate3dModelService interface {
	UploadFile(ctx context.Context, fileContent *[]byte, filename *string) (string, error)
	GetTaskStatus(ctx context.Context, taskUuid *string) (string, error)
	GetResultFilePath(ctx context.Context, taskUuid *string) (string, error)
}

type meshService struct {
	databaseRepository database.DatabaseRepository
	rabbitMqRepostiry  rabbit.RabbitMqRepository
}

func NewGenerate3dModelService(
	databaseRepository database.DatabaseRepository,
	rabbitMqRepostiry rabbit.RabbitMqRepository,
) Generate3dModelService {
	return &meshService{
		databaseRepository: databaseRepository,
		rabbitMqRepostiry:  rabbitMqRepostiry,
	}
}

func (service *meshService) UploadFile(
	ctx context.Context,
	fileContent *[]byte,
	filename *string,
) (string, error) {
	rabbitTask := rabbit.RabbitTask{
		Uuid:     uuid.New().String(),
		Datetime: time.Now().Format(time.DateTime),
		Filename: *filename,
		FileContent:     fileContent,
	}

	requestUuid := rabbitTask.Uuid
	err := service.rabbitMqRepostiry.SendTask(ctx, &rabbitTask)
	if err != nil {
		return requestUuid, err
	}

	dbEntity := rabbitTask.ToDbEntity()
	dbEntity.State = database.TaskInProgress

	if err := service.databaseRepository.InsertTask(ctx, &dbEntity); err != nil {
		return requestUuid, err
	}

	return requestUuid, nil
}

func (service *meshService) GetTaskStatus(
	ctx context.Context,
	uuid *string,
) (string, error) {
	state, err := service.databaseRepository.GetTaskStatus(ctx, uuid)
	if err != nil {
		return "", err
	}

	var taskState string
	switch state {
	case database.TaskInitial:
		taskState = "initial"
	case database.TaskInProgress:
		taskState = "in_progress"
	case database.TaskSuccess:
		taskState = "success"
	case database.TaskFailed:
		taskState = "failed"
	}

	return taskState, nil
}

func (service *meshService) GetResultFilePath(
	ctx context.Context,
	taskUuid *string,
) (string, error) {
	filepath, err := service.databaseRepository.GetResultFilePath(ctx, taskUuid)
	if _, existErr := os.Stat(filepath); err != nil || existErr != nil {
		return "", err
	}

	return filepath, nil
}
