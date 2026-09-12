from pathlib import Path


class ListFilesTool:
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
        self.project_path = Path(project_path)

        if not self.project_path.exists():
            raise FileNotFoundError(
                f"Project path does not exist: {self.project_path}"
            )

        if not self.project_path.is_dir():
            raise NotADirectoryError(
                f"Project path is not a directory: {self.project_path}"
            )

    def execute(self):
        items = []

        for item in sorted(self.project_path.iterdir()):
            if item.is_dir() and item.name in self.DEFAULT_IGNORE_DIRS:
                continue

            items.append(item)

        return items
