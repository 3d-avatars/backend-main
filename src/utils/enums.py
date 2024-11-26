
from enum import Enum


class TaskStatus(str, Enum):
    INITIAL = "INITIAL",
    PROCESSING = "PROCESSING",
    SUCCESS = "SUCCESS",
    FAILED = "FAILED",
