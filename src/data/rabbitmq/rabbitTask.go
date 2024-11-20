package rabbitmq

import (
	"3d-avatar/backend-main/src/data/database"
	"mime/multipart"
)

type RabbitTask struct {
	Uuid     string `json:"uuid"`
	Datetime string `json:"datetime"`
	Filename string `json:"filename"`
	File     *multipart.File `file:"file"`
}

type RabbitResponse struct {
	Uuid string `json:"uuid"`
	Datetime string `json:"datetime"`
	Filename string `json:"filename"`
	File []byte `file:"file"`
}

func (t *RabbitTask) ToDbEntity() database.TaskEntity {
	return database.TaskEntity{
		RequestUuid:    t.Uuid,
		Datetime:       t.Datetime,
		ResultFilePath: "",
	}
}
