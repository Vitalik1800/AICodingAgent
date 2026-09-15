import json

from .modification_collection import ModificationCollection
from .modification_parser import ModificationParser


class ModificationResponseParser:
    def __init__(self, project_root=None):
        self.project_root = project_root
        self.modification_parser = ModificationParser(project_root)

    def parse(self, content):
        if not isinstance(content, str):
            raise TypeError("Modification response must be a string.")

        text = content.strip()

        if not text:
            raise ValueError("Modification response cannot be empty.")

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

            except (ValueError, TypeError):
                raise ValueError(
                    "Invalid modification JSON."
                )

        if not isinstance(data, dict):
            raise ValueError(
                "Modification response must be a JSON object."
            )

        if (
                data.get("modification_type") == "delete"
                and "file_path" in data
                and "type" not in data
                and "modifications" not in data
        ):
            file_path = data["file_path"]

            if not isinstance(file_path, str):
                raise TypeError(
                    "Modification file_path must be a string."
                )

            if not file_path.strip():
                raise ValueError(
                    "Modification file_path cannot be empty."
                )

            normalized_data = {
                "type": "modification",
                "modifications": [
                    {
                        "file_path": file_path,
                        "original_content": "",
                        "new_content": "",
                        "description": (
                            f"Delete file '{file_path}'"
                        ),
                        "modification_type": "delete"
                    }
                ]
            }

            return self.modification_parser.parse(
                json.dumps(normalized_data)
            )

        if data.get("type") != "modification":
            raise ValueError(
                "Modification response type must be 'modification'."
            )

        modifications_data = data.get("modifications")

        if not isinstance(modifications_data, list):
            raise ValueError(
                "'modifications' must be a list."
            )

        if not modifications_data:
            raise ValueError(
                "Modification list cannot be empty."
            )

        normalized_data = {
            "type": "modification",
            "modifications": modifications_data
        }

        return self.modification_parser.parse(
            json.dumps(normalized_data)
        )
