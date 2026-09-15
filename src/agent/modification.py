from dataclasses import dataclass
from pathlib import Path


@dataclass
class Modification:
    file_path: Path
    original_content: str
    new_content: str
    description: str = ""
    modification_type: str = "update"

    VALID_TYPES = {"create", "update", "delete"}

    def __post_init__(self):
        self.file_path = Path(self.file_path)

        if not str(self.file_path).strip():
            raise ValueError("Modification file path cannot be empty.")

        if not isinstance(self.original_content, str):
            raise TypeError("Original content must be a string.")

        if not isinstance(self.new_content, str):
            raise TypeError("New content must be a string.")

        if not isinstance(self.description, str):
            raise TypeError("Modification description must be a string.")

        if self.modification_type not in self.VALID_TYPES:
            raise ValueError(
                f"Unsupported modification type: {self.modification_type}"
            )

        self._validate_operation()

    def _validate_operation(self):
        if self.modification_type == "create":
            if self.original_content:
                raise ValueError(
                    "Create modification must have empty original content."
                )

            if not self.new_content:
                raise ValueError(
                    "Create modification must have new content."
                )

        elif self.modification_type == "update":
            if not self.original_content:
                raise ValueError(
                    "Update modification must have original content."
                )

            if not self.new_content:
                raise ValueError(
                    "Update modification must have new content."
                )

            if self.original_content == self.new_content:
                raise ValueError(
                    "Update modification must change the file content."
                )

        elif self.modification_type == "delete":
            if not self.original_content:
                raise ValueError(
                    "Delete modification must have original content."
                )

            if self.new_content:
                raise ValueError(
                    "Delete modification must have empty new content."
                )

    @property
    def is_changed(self):
        return self.original_content != self.new_content

    @property
    def is_new_file(self):
        return self.modification_type == "create"

    @property
    def is_deleted_file(self):
        return self.modification_type == "delete"

    def __repr__(self):
        return (
            f"Modification("
            f"file_path={self.file_path!s}, "
            f"type={self.modification_type!r}, "
            f"changed={self.is_changed}"
            f")"
        )
