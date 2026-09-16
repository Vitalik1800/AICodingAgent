import json

from src.core.modification_parser import ModificationParser


class ModificationResponseParser:
    def __init__(self, project_root=None):
        self.project_root = project_root
        self.modification_parser = ModificationParser(project_root)

    def _prepare_original_content(
        self,
        file_path,
        original_content,
        modification_type
    ):
        """
        Always load the actual file content for update and delete operations.
        """

        if modification_type not in {"update", "delete"}:
            return original_content

        normalized_path = (
            self.modification_parser._normalize_file_path(
                file_path
            )
        )

        target_path = (
                self.modification_parser.project_root
                / normalized_path
        )

        if not target_path.exists():
            raise FileNotFoundError(
                f"File does not exist: {file_path}"
            )

        if not target_path.is_file():
            raise IsADirectoryError(
                f"Path is not a file: {file_path}"
            )

        current_content = target_path.read_text(
            encoding="utf-8"
        )

        if (
                original_content
                and original_content != current_content
        ):
            raise ValueError(
                "Provided original_content does not match "
                "current file content."
            )

        return current_content

    def _normalize_content(self, content, field_name):
        if isinstance(content, str):
            return content

        if isinstance(content, list):
            if not all(isinstance(line, str) for line in content):
                raise TypeError(
                    f"Modification {field_name} list must contain "
                    "only strings."
                )

            return "\n".join(content)

        raise TypeError(
            f"Modification {field_name} must be a string "
            "or a list of strings."
        )

    def _detect_modification_type(self, file_path):
        if self.project_root is None:
            return "create"

        normalized_path = self.modification_parser._normalize_file_path(
            file_path
        )

        target_path = self.modification_parser.project_root / normalized_path

        if target_path.exists():
            if not target_path.is_file():
                raise IsADirectoryError(
                    f"Path is not a file: {target_path}"
                )

            return "update"

        return "create"

    def parse(self, content):
        if not isinstance(content, str):
            raise TypeError(
                "Modification response must be a string."
            )

        text = content.strip()

        if not text:
            raise ValueError(
                "Modification response cannot be empty."
            )

        if text.startswith("```") and text.endswith("```"):
            lines = text.splitlines()

            if len(lines) < 3:
                raise ValueError(
                    "Modification code block cannot be empty."
                )

            first_line = lines[0].strip().lower()

            if first_line in {"```json", "```"}:
                text = "\n".join(lines[1:-1]).strip()

        try:
            data = json.loads(text)

        except json.JSONDecodeError:
            try:
                return self.modification_parser.parse(text)

            except (ValueError, TypeError) as error:
                raise ValueError(
                    "Invalid modification JSON."
                ) from error

        if not isinstance(data, dict):
            raise ValueError(
                "Modification response must be a JSON object."
            )

        # =========================================================
        # NORMALIZE FLAT RESPONSE
        # =========================================================

        modification_type = data.get("modification_type")
        file_path = data.get("file_path")

        if (
                modification_type is None
                and file_path is not None
                and "type" not in data
                and "modifications" not in data
                and (
                "new_content" in data
                or "content" in data
                or "file_content" in data
        )
        ):
            modification_type = self._detect_modification_type(
                file_path
            )

        # =========================================================
        # NORMALIZE FULL RESPONSE
        # =========================================================

        if data.get("type") == "modification":
            modifications_data = data.get("modifications")

            if not isinstance(modifications_data, list):
                raise ValueError(
                    "'modifications' must be a list."
                )

            if not modifications_data:
                raise ValueError(
                    "Modification list cannot be empty."
                )

            normalized_modifications = []

            for modification in modifications_data:
                if not isinstance(modification, dict):
                    raise ValueError(
                        "Each modification must be a JSON object."
                    )

                normalized_modification = dict(modification)

                current_file_path = (
                    normalized_modification.get("file_path")
                )

                current_type = (
                    normalized_modification.get(
                        "modification_type"
                    )
                )

                if not isinstance(current_file_path, str):
                    raise TypeError(
                        "Modification file_path must be a string."
                    )

                if not current_file_path.strip():
                    raise ValueError(
                        "Modification file_path cannot be empty."
                    )

                if current_type not in {
                    "create",
                    "update",
                    "delete"
                }:
                    raise ValueError(
                        "Modification type must be create, "
                        "update, or delete."
                    )

                original_content = (
                    normalized_modification.get(
                        "original_content",
                        ""
                    )
                )

                new_content = (
                    normalized_modification.get(
                        "new_content",
                        ""
                    )
                )

                original_content = self._normalize_content(
                    original_content,
                    "original_content"
                )

                new_content = self._normalize_content(
                    new_content,
                    "new_content"
                )

                original_content = (
                    self._prepare_original_content(
                        file_path=current_file_path,
                        original_content=original_content,
                        modification_type=current_type
                    )
                )

                normalized_modification["original_content"] = (
                    original_content
                )

                normalized_modification["new_content"] = (
                    new_content
                )

                normalized_modifications.append(
                    normalized_modification
                )

            normalized_data = {
                "type": "modification",
                "modifications": normalized_modifications
            }

            return self.modification_parser.parse(
                json.dumps(normalized_data)
            )

        # =========================================================
        # FLAT RESPONSE VALIDATION
        # =========================================================

        if file_path is None:
            raise ValueError(
                "Modification response must contain file_path."
            )

        if not isinstance(file_path, str):
            raise TypeError(
                "Modification file_path must be a string."
            )

        if not file_path.strip():
            raise ValueError(
                "Modification file_path cannot be empty."
            )

        if modification_type is None:
            raise ValueError(
                "Modification type could not be determined."
            )

        if modification_type not in {
            "create",
            "update",
            "delete"
        }:
            raise ValueError(
                "Modification type must be create, update, or delete."
            )

        # =========================================================
        # FLAT CONTENT EXTRACTION
        # =========================================================

        original_content = data.get("original_content")

        if original_content is None:
            original_content = data.get("old_content")

        new_content = data.get("new_content")

        if new_content is None:
            new_content = data.get("content")

        if new_content is None:
            new_content = data.get("file_content")

        if original_content is None:
            original_content = ""

        if new_content is None:
            new_content = ""

        original_content = self._normalize_content(
            original_content,
            "original_content"
        )

        new_content = self._normalize_content(
            new_content,
            "new_content"
        )

        # =========================================================
        # LOAD ACTUAL ORIGINAL FILE CONTENT
        # =========================================================

        original_content = self._prepare_original_content(
            file_path=file_path,
            original_content=original_content,
            modification_type=modification_type
        )

        normalized_data = {
            "type": "modification",
            "modifications": [
                {
                    "file_path": file_path,
                    "original_content": original_content,
                    "new_content": new_content,
                    "description": data.get(
                        "description",
                        f"Modify file '{file_path}'"
                    ),
                    "modification_type": modification_type
                }
            ]
        }

        return self.modification_parser.parse(
            json.dumps(normalized_data)
        )
