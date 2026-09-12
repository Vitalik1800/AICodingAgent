from pathlib import Path


class SearchCodeTool:
    DEFAULT_IGNORE_DIRS = {
        ".git",
        ".venv",
        ".idea",
        "__pycache__",
        "data",
        "logs",
        "node_modules"
    }

    def __init__(self, project_path="."):
        self.project_path = Path(project_path).resolve()

        if not self.project_path.exists():
            raise FileNotFoundError(
                f"Project path does not exist: {self.project_path}"
            )

        if not self.project_path.is_dir():
            raise NotADirectoryError(
                f"Project path is not a directory: {self.project_path}"
            )

    def execute(self, query):
        if not query:
            raise ValueError("Search query cannot be empty.")

        results = []

        for path in self.project_path.rglob("*"):
            if not path.is_file():
                continue

            if any(
                part in self.DEFAULT_IGNORE_DIRS
                for part in path.parts
            ):
                continue

            try:
                path.relative_to(self.project_path)
            except ValueError:
                continue

            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            for line_number, line in enumerate(
                content.splitlines(),
                start=1
            ):
                if query.lower() in line.lower():
                    results.append(
                        {
                            "file": str(path.relative_to(self.project_path)),
                            "line": line_number,
                            "content": line.strip()
                        }
                    )

        return results
    