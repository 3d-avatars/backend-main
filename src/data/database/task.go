package database

const (
	TaskInitial    TaskState = iota
	TaskInProgress TaskState = iota
	TaskSuccess    TaskState = iota
	TaskFailed     TaskState = iota
)

type TaskState int16

type TaskEntity struct {
	ID             int       `db:"id"`
	RequestUuid    string    `db:"request_uuid"`
	Datetime       string    `db:"datetime"`
	State          TaskState `db:"state"`
	ResultFilePath string    `db:"result_file_path"`

	CreatedAT string `json:"created_at" db:"created_at"`
	UpdatedAT string `json:"updated_at" db:"updated_at"`
}
