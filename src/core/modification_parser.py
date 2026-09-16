import json
from pathlib import Path

from src.core.modification import Modification
from src.core.modification_collection import ModificationCollection


class ModificationParser:
    MAX_MODIFICATIONS = 50

    def __init__(self, project_root=None):
        self.project_root = (
            Path(project_root).resolve()
            if project_root is not None
            else None
        )

    def parse(self, content):
        if not isinstance(content, str):
            raise TypeError("Modification content must be a string.")

        content = content.strip()

        if not content:
            raise ValueError("Modification content cannot be empty.")

        content = self._extract_json(content)

        try:
            data = json.loads(content)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid modification JSON: {error}"
            ) from error

        if not isinstance(data, dict):
            raise ValueError(
                "Modification response must be a JSON object."
            )

        if data.get("type") != "modification":
            raise ValueError(
                "Modification response must have type 'modification'."
            )

        modifications = data.get("modifications")

        if not isinstance(modifications, list):
            raise ValueError(
                "Modification response must contain a 'modifications' list."
            )

        if len(modifications) > self.MAX_MODIFICATIONS:
            raise ValueError(
                f"Modification response contains too many modifications. "
                f"Maximum allowed: {self.MAX_MODIFICATIONS}."
            )

        collection = ModificationCollection()
        seen_paths = set()

        for item in modifications:
            modification = self._parse_modification(item)

            normalized_key = str(modification.file_path).replace("\\", "/")

            if normalized_key in seen_paths:
                raise ValueError(
                    f"Duplicate modification path: "
                    f"{modification.file_path}"
                )

            seen_paths.add(normalized_key)
            collection.add(modification)

        return collection

    def _extract_json(self, content):
        if content.startswith("```") and content.endswith("```"):
            lines = content.splitlines()

            if len(lines) < 3:
                raise ValueError(
                    "Fenced modification JSON is empty."
                )

            first_line = lines[0].strip().lower()

            if first_line not in {"```", "```json"}:
                raise ValueError(
                    "Unsupported fenced modification format."
                )

            content = "\n".join(lines[1:-1]).strip()

        if not content:
            raise ValueError(
                "Modification JSON cannot be empty."
            )

        try:
            json.loads(content)
            return content
        except json.JSONDecodeError:
            pass

        start = content.find("{")
        end = content.rfind("}")

        if start == -1 or end == -1 or start >= end:
            raise ValueError(
                "Modification JSON object was not found."
            )

        extracted = content[start:end + 1].strip()

        try:
            json.loads(extracted)
        except json.JSONDecodeError as error:
            raise ValueError(
                f"Invalid modification JSON: {error}"
            ) from error

        return extracted

    def _normalize_file_path(self, file_path):
        path = Path(file_path)

        if path.is_absolute():
            raise ValueError(
                "Modification file_path must be relative to the project."
            )

        if self.project_root is None:
            return path

        resolved_path = (self.project_root / path).resolve()

        try:
            resolved_path.relative_to(self.project_root)
        except ValueError as error:
            raise PermissionError(
                "Modification file_path is outside the project."
            ) from error

        return resolved_path.relative_to(self.project_root)

    def _load_current_content(self, normalized_path):
        if self.project_root is None:
            raise ValueError(
                "Project root is required to load current file content."
            )

        file_path = (self.project_root / normalized_path).resolve()

        try:
            file_path.relative_to(self.project_root)
        except ValueError as error:
            raise PermissionError(
                "Modification file_path is outside the project."
            ) from error

        if not file_path.exists():
            raise FileNotFoundError(
                f"File does not exist: {file_path}"
            )

        if not file_path.is_file():
            raise IsADirectoryError(
                f"Path is not a file: {file_path}"
            )

        return file_path.read_text(encoding="utf-8")

    def _prepare_original_content(
        self,
        normalized_path,
        original_content,
        modification_type
    ):
        if modification_type not in {"update", "delete"}:
            return original_content

        current_content = self._load_current_content(normalized_path)

        if original_content and original_content != current_content:
            raise ValueError(
                "Provided original_content does not match "
                "current file content."
            )

        return current_content

    def _parse_modification(self, data):
        if not isinstance(data, dict):
            raise ValueError(
                "Each modification must be a JSON object."
            )

        required_fields = {
            "file_path",
            "original_content",
            "new_content",
            "modification_type"
        }

        missing_fields = required_fields - data.keys()

        if missing_fields:
            raise ValueError(
                "Modification is missing required fields: "
                + ", ".join(sorted(missing_fields))
            )

        file_path = data["file_path"]
        original_content = data["original_content"]
        new_content = data["new_content"]
        description = data.get("description", "")
        modification_type = data["modification_type"]

        if not isinstance(file_path, str):
            raise TypeError(
                "Modification file_path must be a string."
            )

        if not file_path.strip():
            raise ValueError(
                "Modification file_path cannot be empty."
            )

        if not isinstance(original_content, str):
            raise TypeError(
                "Modification original_content must be a string."
            )

        if not isinstance(new_content, str):
            raise TypeError(
                "Modification new_content must be a string."
            )

        if not isinstance(description, str):
            raise TypeError(
                "Modification description must be a string."
            )

        if not isinstance(modification_type, str):
            raise TypeError(
                "Modification modification_type must be a string."
            )

        modification_type = modification_type.strip().lower()

        if modification_type == "insertion":
            modification_type = "update"

        if modification_type not in Modification.VALID_TYPES:
            raise ValueError(
                f"Unsupported modification type: {modification_type}"
            )

        normalized_path = self._normalize_file_path(file_path)

        original_content = self._prepare_original_content(
            normalized_path,
            original_content,
            modification_type
        )

        return Modification(
            file_path=normalized_path,
            original_content=original_content,
            new_content=new_content,
            description=description,
            modification_type=modification_type
        )
