package rabbitmq

import (
	"3d-avatar/backend-main/src/data/database"
	"mime/multipart"
)

type RabbitTask struct {
	Uuid     string
	Datetime string
	File     *multipart.File
}

func (t *RabbitTask) ToDbEntity() database.TaskEntity {
	return database.TaskEntity{
		RequestUuid:    t.Uuid,
		Datetime:       t.Datetime,
		ResultFilePath: "",
	}
}
