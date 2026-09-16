from dataclasses import dataclass
from pathlib import Path


@dataclass
class PatchPreview:
    file_path: Path
    patch_content: str
    modification_type: str
    original_content: str = ""
    new_content: str = ""

    VALID_TYPES = {"create", "update", "delete"}

    def __post_init__(self):
        self.file_path = Path(self.file_path)

        if not str(self.file_path).strip():
            raise ValueError("Patch preview file path cannot be empty.")

        if not isinstance(self.patch_content, str):
            raise TypeError("Patch preview content must be a string.")

        if not isinstance(self.original_content, str):
            raise TypeError(
                "Patch preview original content must be a string."
            )

        if not isinstance(self.new_content, str):
            raise TypeError(
                "Patch preview new content must be a string."
            )

        if self.modification_type not in self.VALID_TYPES:
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

    @property
    def has_changes(self):
        return self.original_content != self.new_content

    def __repr__(self):
        return (
            f"PatchPreview("
            f"file_path={self.file_path!s}, "
            f"type={self.modification_type!r}"
            f")"
        )