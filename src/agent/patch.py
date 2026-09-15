from dataclasses import dataclass
from pathlib import Path


@dataclass
class Patch:
    file_path: Path
    content: str
    modification_type: str = "update"

    def __post_init__(self):
        self.file_path = Path(self.file_path)

        if not str(self.file_path).strip():
            raise ValueError("Patch file path cannot be empty.")

        if not isinstance(self.content, str):
            raise TypeError("Patch content must be a string.")

        if self.modification_type not in {"create", "update", "delete"}:
            raise ValueError(
                f"Unsupported patch type: {self.modification_type}"
            )

    @property
    def is_empty(self):
        return not self.content.strip()
