package dtos

type UploadInputImageResponse struct {
	Message     string `json:"message"`
	RequestUuid string `json:"request_uuid"`
}

type GetTaskStatusResponse struct {
	Message string `json:"message"`
	Status  string `json:"status"`
}
