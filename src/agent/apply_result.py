from dataclasses import dataclass
from pathlib import Path


@dataclass
class ApplyResult:
    file_path: Path
    modification_type: str
    success: bool
    message: str = ""

    VALID_TYPES = {
        "create",
        "update",
        "delete"
    }

    def __post_init__(self):
        self.file_path = Path(self.file_path)

        if not str(self.file_path).strip():
            raise ValueError(
                "Apply result file path cannot be empty."
            )

        if self.modification_type not in self.VALID_TYPES:
            raise ValueError(
                f"Unsupported modification type: " 
                f"{self.modification_type}"
            )

        if not isinstance(self.success, bool):
            raise TypeError(
                "Apply result success must be a boolean."
            )

        if not isinstance(self.message, str):
            raise TypeError(
                "Apply result message must be a string."
            )

    @property
    def is_success(self):
        return self.success

    @property
    def is_failure(self):
        return not self.success
