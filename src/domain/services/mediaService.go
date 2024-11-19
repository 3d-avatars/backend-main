package services

import (
	"fmt"
	"io"
	"os"

	"3d-avatar/backend-main/src/data/models"
)

type MediaUpload interface {
	FileUpload(file *models.MediaFile) error
}

type mediaUpload struct{}

func NewMediaUpload() MediaUpload {
	return &mediaUpload{}
}

func (*mediaUpload) FileUpload(file *models.MediaFile) error {
	imagePath := fmt.Sprintf(
		"/Users/danilov6083/GolandProjects/backend-main/imaginary-database/%s",
		file.Filename,
	)

	dstFile, err := os.Create(imagePath)
	if err != nil {
		return err
	}
	defer dstFile.Close()

	if _, err = io.Copy(dstFile, file.File); err != nil {
		return err
	}

	return nil
}
