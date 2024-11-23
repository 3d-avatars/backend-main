package rabbit

import (
	"3d-avatar/backend-main/src/data/database"
)

type RabbitTask struct {
	Uuid        string  `json:"uuid"`
	Datetime    string  `json:"datetime"`
	Filename    string  `json:"filename"`
	FileContent *[]byte `json:"file"`
}

type RabbitResponse struct {
	Uuid        string `json:"uuid"`
	Datetime    string `json:"datetime"`
	Filename    string `json:"filename"`
	FileContent []byte `json:"file"`
}

func (t *RabbitTask) ToDbEntity() database.TaskEntity {
	return database.TaskEntity{
		RequestUuid:    t.Uuid,
		Datetime:       t.Datetime,
		ResultFilePath: "",
	}
}
