from pathlib import Path

from src.core.modification import Modification


class ModificationSafety:
    PROTECTED_DIRS = {
        ".git",
        ".venv",
        "__pycache__",
        "node_modules"
    }
    PROTECTED_FILES = {
        ".env",
        "chat_history.json",
        "requirements.txt",
        "pyproject.toml",
        "setup.py",
        "setup.cfg",
        "tox.ini"
    }

    def __init__(self, project_root=None):
        self.project_root = (
            Path(project_root).resolve()
            if project_root is not None
            else None
        )

    def validate(self, modification):
        if not isinstance(modification, Modification):
            raise TypeError(
                "Only Modification objects can be validated."
            )

        self._validate_path(modification)
        self._validate_operation(modification)

        return True

    def _validate_path(self, modification):
        if modification.file_path.is_absolute():
            raise ValueError(
                "Modification file path must be relative to the project."
            )

        if self.project_root is None:
            return

        resolved_path = (
            self.project_root / modification.file_path
        ).resolve()

        try:
            relative_path = resolved_path.relative_to(self.project_root)
        except ValueError as error:
            raise PermissionError(
                "Modification file path is outside the project."
            ) from error

        if any(
            part in self.PROTECTED_DIRS
            for part in relative_path.parts
        ):
            raise PermissionError(
                "Modification targets a protected project directory."
            )

        if relative_path.name in self.PROTECTED_FILES:
            raise PermissionError(
                "Modification targets a protected project file."
            )

    def _validate_operation(self, modification):
        if modification.modification_type == "create":
            if modification.original_content:
                raise ValueError(
                    "Create modification must have empty original content."
                )

        elif modification.modification_type == "update":
            if not modification.original_content:
                raise ValueError(
                    "Update modification must have original content."
                )

        elif modification.modification_type == "delete":
            if not modification.original_content:
                raise ValueError(
                    "Delete modification must have original content."
                )
