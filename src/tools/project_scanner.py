from pathlib import Path

from .project_structure import ProjectItem


class ProjectScanner:
    DEFAULT_IGNORE_DIRS = {
        ".git",
        ".venv",
        ".idea",
        "__pycache__",
        "data",
        "logs"
    }

    def __init__(self, project_path):
        self.project_path = Path(project_path)

        if not self.project_path.exists():
            raise FileNotFoundError(
                f"Project path does not exist: {self.project_path}"
            )

        if not self.project_path.is_dir():
            raise NotADirectoryError(
                f"Project path is not a directory: {self.project_path}"
            )

    def scan(self):
        return list(self.project_path.iterdir())

    def get_files(self):
        return [
            item
            for item in self.scan()
            if item.is_file()
            and item.parent.name not in self.DEFAULT_IGNORE_DIRS
        ]

    def get_structure(self):
        structure = []

        for item in self.scan():
            if item.is_dir():
                if item.name in self.DEFAULT_IGNORE_DIRS:
                    continue

                structure.append(
                    ProjectItem(
                        path=item,
                        item_type="directory"
                    )
                )

            elif item.is_file():
                structure.append(
                    ProjectItem(
                        path=item,
                        item_type="file"
                    )
                )

        return structure

