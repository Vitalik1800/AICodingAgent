from dataclasses import dataclass
from pathlib import Path


@dataclass
class Patch:
    file_path: Path
    content: str
    modification_type: str = "update"
    original_content: str = ""
    new_content: str = ""

    VALID_TYPES = {"create", "update", "delete"}

    def __post_init__(self):
        self.file_path = Path(self.file_path)

        if not str(self.file_path).strip():
            raise ValueError("Patch file path cannot be empty.")

        if not isinstance(self.content, str):
            raise TypeError("Patch content must be a string.")

        if not isinstance(self.original_content, str):
            raise TypeError("Patch original content must be a string.")

        if not isinstance(self.new_content, str):
            raise TypeError("Patch new content must be a string.")

        if self.modification_type not in self.VALID_TYPES:
            raise ValueError(
                f"Unsupported patch type: {self.modification_type}"
            )

    @property
    def is_empty(self):
        return not self.content.strip()

    @property
    def is_changed(self):
        return self.original_content != self.new_content
