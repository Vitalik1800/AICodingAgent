from pathlib import Path

from .apply_result import ApplyResult


class PatchApplier:
    def __init__(self, project_root="."):
        self.project_root = Path(project_root).expanduser().resolve()

        if not self.project_root.exists():
            raise FileNotFoundError(
                f"Project root does not exist: {self.project_root}"
            )

        if not self.project_root.is_dir():
            raise NotADirectoryError(
                f"Project root is not a directory: {self.project_root}"
            )

    def _resolve_safe_path(self, file_path):
        if not isinstance(file_path, (str, Path)):
            raise TypeError(
                "File path must be a string or Path."
            )

        file_path = Path(file_path)

        if not str(file_path).strip():
            raise ValueError("File path cannot be empty.")

        if not file_path.is_absolute():
            file_path = self.project_root / file_path

        resolved_path = file_path.resolve()

        try:
            resolved_path.relative_to(self.project_root)
        except ValueError as error:
            raise PermissionError(
                f"Path is outside the project: {resolved_path}"
            ) from error

        return resolved_path

    def create_file(self, file_path, content):
        file_path = self._resolve_safe_path(file_path)

        if not isinstance(content, str):
            raise TypeError(
                "File content must be a string."
            )

        if file_path.exists():
            raise FileExistsError(
                f"File already exists: {file_path}"
            )

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        print("[PATCH APPLIER] content repr:", repr(content))

        file_path.write_text(
            content,
            encoding="utf-8"
        )

        return ApplyResult(
            file_path=file_path,
            modification_type="create",
            success=True,
            message=f"File created: {file_path}"
        )

    def update_file(
        self,
        file_path,
        original_content,
        new_content
    ):
        file_path = self._resolve_safe_path(file_path)

        if not isinstance(original_content, str):
            raise TypeError(
                "Original content must be a string."
            )

        if not isinstance(new_content, str):
            raise TypeError(
                "New content must be a string."
            )

        if not file_path.exists():
            raise FileNotFoundError(
                f"File does not exist: {file_path}"
            )

        if not file_path.is_file():
            raise IsADirectoryError(
                f"Path is not a file: {file_path}"
            )

        current_content = file_path.read_text(
            encoding="utf-8"
        )

        if current_content != original_content:
            raise ValueError(
                f"File content has changed since the patch "
                f"was generated: {file_path}"
            )

        if current_content == new_content:
            raise ValueError(
                f"New content is identical to current content: "
                f"{file_path}"
            )

        file_path.write_text(
            new_content,
            encoding="utf-8"
        )

        return ApplyResult(
            file_path=file_path,
            modification_type="update",
            success=True,
            message=f"File updated: {file_path}"
        )

    def delete_file(
        self,
        file_path,
        original_content
    ):
        file_path = self._resolve_safe_path(file_path)

        if not isinstance(original_content, str):
            raise TypeError(
                "Original content must be a string."
            )

        if not file_path.exists():
            raise FileNotFoundError(
                f"File does not exist: {file_path}"
            )

        if not file_path.is_file():
            raise IsADirectoryError(
                f"Path is not a file: {file_path}"
            )

        current_content = file_path.read_text(
            encoding="utf-8"
        )

        if current_content != original_content:
            raise ValueError(
                f"File content has changed since the patch "
                f"was generated: {file_path}"
            )

        file_path.unlink()

        return ApplyResult(
            file_path=file_path,
            modification_type="delete",
            success=True,
            message=f"File deleted: {file_path}"
        )

    def _atomic_write(
        self,
        file_path,
        content
    ):
        file_path = self._resolve_safe_path(file_path)

        if not str(file_path).strip():
            raise ValueError(
                "File path cannot be empty."
            )

        if not isinstance(content, str):
            raise TypeError(
                "File content must be a string."
            )

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        temporary_path = file_path.with_name(
            f".{file_path.name}.tmp"
        )

        try:
            temporary_path.write_text(
                content,
                encoding="utf-8"
            )

            temporary_path.replace(
                file_path
            )

        finally:
            if temporary_path.exists():
                temporary_path.unlink()

    def _validate_original_content(
        self,
        file_path,
        original_content
    ):
        file_path = self._resolve_safe_path(file_path)

        if not str(file_path).strip():
            raise ValueError(
                "File path cannot be empty."
            )

        if not isinstance(original_content, str):
            raise TypeError(
                "Original content must be a string."
            )

        if not file_path.exists():
            raise FileNotFoundError(
                f"File does not exist: {file_path}"
            )

        if not file_path.is_file():
            raise IsADirectoryError(
                f"Path is not a file: {file_path}"
            )

        current_content = file_path.read_text(
            encoding="utf-8"
        )

        if current_content != original_content:
            raise ValueError(
                f"File content has changed since the patch "
                f"was generated: {file_path}"
            )

        return True
