from pathlib import Path


class ProjectPath:
    DEFAULT_IGNORE_DIRS = {
        ".git",
        ".venv",
        ".idea",
        "__pycache__",
        "data",
        "logs",
        "node_modules"
    }

    def __init__(self, path="."):
        self.root = Path(path).expanduser().resolve()

        if not self.root.exists():
            raise FileNotFoundError(
                f"Project path does not exist: {self.root}"
            )

        if not self.root.is_dir():
            raise NotADirectoryError(
                f"Project path is not a directory: {self.root}"
            )

    def resolve(self, path):
        candidate = Path(path)

        if not candidate.is_absolute():
            candidate = self.root / candidate

        candidate = candidate.resolve()

        try:
            candidate.relative_to(self.root)
        except ValueError:
            raise PermissionError(
                f"Path is outside the project: {candidate}"
            )

        return candidate

    def is_ignored(self, path):
        path = Path(path).resolve()

        try:
            relative = path.relative_to(self.root)
        except ValueError:
            return True

        return any(
            part in self.DEFAULT_IGNORE_DIRS
            for part in relative.parts
        )
