from enum import Enum

class SourceTypeEnum(Enum):
    app = "app"
    file = "file"


class StatusEnum(Enum):
    completed = "completed"
    in_progress = "in progress"
    not_started = "not started"
    checked = "checked"