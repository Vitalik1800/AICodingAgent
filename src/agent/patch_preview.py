from dataclasses import dataclass
from pathlib import Path


@dataclass
class PatchPreview:
    file_path: Path
    patch_content: str
    modification_type: str

    def __post_init__(self):
        self.file_path = Path(self.file_path)

        if not str(self.file_path).strip():
            raise ValueError("Patch preview file path cannot be empty.")

        if not isinstance(self.patch_content, str):
            raise TypeError("Patch preview content must be a string.")

        if not isinstance(self.modification_type, str):
            raise TypeError("Patch preview modification type must be a string.")

        if self.modification_type not in {"create", "update", "delete"}:
            raise ValueError(
                f"Unsupported patch preview type: {self.modification_type}"
            )

        if not self.patch_content.strip():
            raise ValueError("Patch preview content cannot be empty.")

    @property
    def is_create(self):
        return self.modification_type == "create"

    @property
    def is_update(self):
        return self.modification_type == "update"

    @property
    def is_delete(self):
        return self.modification_type == "delete"

    def __repr__(self):
        return (
            f"PatchPreview("
            f"file_path={self.file_path!s}, "
            f"type={self.modification_type!r}"
            f")"
        )