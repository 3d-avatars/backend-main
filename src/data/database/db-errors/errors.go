package dberrors

import "errors"

var (
	ErrTaskNotFound = errors.New("failed to find any task")
)
