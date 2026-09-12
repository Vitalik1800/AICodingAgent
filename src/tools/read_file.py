from pathlib import Path


class ReadFileTool:
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

    def execute(self, file_path):
        path = Path(file_path)

        if not path.is_absolute():
            path = self.project_path / path

        path = path.resolve()

        try:
            path.relative_to(self.project_path)
        except ValueError:
            raise PermissionError(
                f"File is outside the project: {path}"
            )

        if not path.exists():
            raise FileNotFoundError(
                f"File does not exist: {path}"
            )

        if not path.is_file():
            raise IsADirectoryError(
                f"Path is not a file: {path}"
            )

        return path.read_text(encoding="utf-8")
