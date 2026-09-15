from pathlib import Path

from .patch import Patch
import re


class PatchValidator:
    def __init__(self, project_root=None):
        self.project_root = (
            Path(project_root).resolve()
            if project_root is not None
            else None
        )

    def validate(self, patch):
        if not isinstance(patch, Patch):
            raise TypeError("Only Patch objects can be validated.")

        self._validate_path(patch)
        self._validate_content(patch)
        self._validate_diff_format(patch)
        self._validate_operation(patch)
        self._validate_file_path_match(patch)

        return True

    def _validate_path(self, patch):
        if patch.file_path.is_absolute():
            raise ValueError(
                "Patch file path must be relative to the project."
            )

        if self.project_root is None:
            return

        resolved_path = (self.project_root / patch.file_path).resolve()

        try:
            resolved_path.relative_to(self.project_root)
        except ValueError as error:
            raise PermissionError(
                "Patch file path is outside the project."
            ) from error

    def _validate_content(self, patch):
        if patch.modification_type in {"create", "update", "delete"}:
            if not patch.content.strip():
                raise ValueError(
                    "Patch content cannot be empty."
                )

    def _validate_diff_format(self, patch):
        lines = patch.content.splitlines()

        if len(lines) < 2:
            raise ValueError("Patch must contain a valid unified diff.")

        if not lines[0].startswith("--- "):
            raise ValueError("Patch is missing the original file header.")

        if not lines[1].startswith("+++ "):
            raise ValueError("Patch is missing the new file header.")

        has_hunk = any(
            re.match(r"^@@ .* @@$", line)
            for line in lines[2:]
        )

        if not has_hunk:
            raise ValueError("Patch does not contain a valid diff hunk.")

    def _validate_operation(self, patch):
        lines = patch.content.splitlines()

        original_file = lines[0][4:].strip()
        new_file = lines[1][4:].strip()

        if patch.modification_type == "create":
            if original_file != "/dev/null":
                raise ValueError(
                    "Create patch must use /dev/null as the original file."
                )

        elif patch.modification_type == "delete":
            if new_file != "/dev/null":
                raise ValueError(
                    "Delete patch must use /dev/null as the new file."
                )

        elif patch.modification_type == "update":
            if original_file == "/dev/null" or new_file == "/dev/null":
                raise ValueError(
                    "Update patch cannot use /dev/null."
                )

    def _validate_file_path_match(self, patch):
        lines = patch.content.splitlines()

        original_file = lines[0][4:].strip()
        new_file = lines[1][4:].strip()

        excepted_path = patch.file_path.as_posix()

        if original_file != "/dev/null":
            original_file = original_file.removeprefix("a/")

            if original_file != excepted_path:
                raise ValueError(
                    "Patch original file path does not match Patch file path."
                )

        if new_file != "/dev/null":
            new_file = new_file.removeprefix("b/")

            if new_file != excepted_path:
                raise ValueError(
                    "Patch new file path does not match Patch file path."
                )
