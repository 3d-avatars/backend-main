package models

import (
	"mime/multipart"
)

type MediaFile struct {
	Filename string         `json:"filename"`
	File     multipart.File `json:"file,omitempty" validate:"required"`
}
