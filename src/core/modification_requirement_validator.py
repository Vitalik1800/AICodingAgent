import re
from pathlib import Path

from src.core.modification import Modification


class ModificationRequirementValidator:
    LINE_COUNT_PATTERN = re.compile(
        r"(?:довжин(?:ою|а)|на)\s+(\d+)\s+рядк",
        re.IGNORECASE
    )

    LINE_RANGE_PATTERN = re.compile(
        r"(?:довжин(?:ою|а)|на)\s+(\d+)\s*[-–—]\s*(\d+)\s+рядк",
        re.IGNORECASE
    )

    FILE_PATH_PATTERN = re.compile(
        r"(?:файл|file)\s+([^\s:]+)",
        re.IGNORECASE
    )

    def validate(self, user_message, modifications):
        if not isinstance(user_message, str):
            raise TypeError("User message must be a string.")

        if not hasattr(modifications, "get_all"):
            raise TypeError(
                "Modifications must provide get_all()."
            )

        modification_items = modifications.get_all()

        if not isinstance(modification_items, list):
            raise TypeError(
                "Modifications get_all() must return a list."
            )

        required_line_range = self._extract_required_line_range(
            user_message
        )

        required_file_path = self._extract_required_file_path(
            user_message
        )

        for modification in modification_items:
            if not isinstance(modification, Modification):
                raise TypeError(
                    "All items must be Modification objects."
                )

            if modification.modification_type != "create":
                continue

            if required_file_path is not None:
                actual_path = self._normalize_path(
                    modification.file_path
                )

                expected_path = self._normalize_path(
                    required_file_path
                )

                if actual_path != expected_path:
                    raise ValueError(
                        "Generated file path does not match the "
                        f"user request. Expected "
                        f"'{required_file_path}', got "
                        f"'{modification.file_path}'."
                    )

            if required_line_range is not None:
                minimum_lines, maximum_lines = required_line_range

                actual_lines = len(
                    modification.new_content.splitlines()
                )

                if actual_lines < minimum_lines:
                    if minimum_lines == maximum_lines:
                        raise ValueError(
                            f"Generated file contains {actual_lines} "
                            f"lines, but the user requested exactly "
                            f"{minimum_lines} lines."
                        )

                    raise ValueError(
                        f"Generated file contains {actual_lines} "
                        f"lines, but the user requested between "
                        f"{minimum_lines} and {maximum_lines} lines."
                    )

                if actual_lines > maximum_lines:
                    if minimum_lines == maximum_lines:
                        raise ValueError(
                            f"Generated file contains {actual_lines} "
                            f"lines, but the user requested exactly "
                            f"{minimum_lines} lines."
                        )

                    raise ValueError(
                        f"Generated file contains {actual_lines} "
                        f"lines, but the user requested between "
                        f"{minimum_lines} and {maximum_lines} lines."
                    )

        return True

    def get_required_line_count(self, user_message):
        if not isinstance(user_message, str):
            raise TypeError("User message must be a string.")

        line_range = self._extract_required_line_range(
            user_message
        )

        if line_range is None:
            return None

        minimum_lines, maximum_lines = line_range

        if minimum_lines == maximum_lines:
            return minimum_lines

        return line_range

    def _extract_required_line_range(self, user_message):
        message = user_message.lower().strip()

        range_match = self.LINE_RANGE_PATTERN.search(message)

        if range_match:
            return None

        exact_match = self.LINE_COUNT_PATTERN.search(message)

        if exact_match:
            line_count = int(exact_match.group(1))

            return line_count, line_count

        return None

    def _extract_required_file_path(self, user_message):
        match = self.FILE_PATH_PATTERN.search(
            user_message.strip()
        )

        if not match:
            return None

        file_path = match.group(1).strip()

        if not file_path:
            return None

        return file_path

    def _normalize_path(self, file_path):
        return Path(file_path).as_posix().lower()
