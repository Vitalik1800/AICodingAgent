from pathlib import Path

from src.tools.project_scanner import ProjectScanner
from src.tools.read_file import ReadFileTool

from .project_context import ProjectContext
from .relevant_file_context import RelevantFileContext


class ProjectContextBuilder:
    def build(self, project_path):
        root = Path(project_path).resolve()
        scanner = ProjectScanner(root)
        structure = scanner.get_tree_structure()

        return ProjectContext(
            name=root.name,
            root_path=root,
            structure=structure
        )

    def add_relevant_file(self, context, file_path):
        reader = ReadFileTool(context.root_path)
        content = reader.execute(file_path)

        path = Path(file_path)

        if not path.is_absolute():
            path = context.root_path / path

        path = path.resolve()

        try:
            path = path.relative_to(context.root_path)
        except ValueError:
            raise PermissionError(
                f"File is outside the project: {path}"
            )

        for existing_file in context.relevant_files:
            if existing_file.path == path:
                return existing_file

        relevant_file = RelevantFileContext(
            path=Path(file_path),
            content=content
        )

        context.relevant_files.append(relevant_file)

        return relevant_file

    def refresh_relevant_file(self, context, file_path):
        path = Path(file_path)

        if not path.is_absolute():
            path = context.root_path / path

        path = path.resolve()

        try:
            path = path.relative_to(context.root_path)
        except ValueError:
            raise PermissionError(
                f"File is outside the project: {path}"
            )

        for existing_file in context.relevant_files:
            if existing_file.path == path:
                reader = ReadFileTool(context.root_path)
                existing_file.content = reader.execute(file_path)
                return existing_file

        raise ValueError(
            f"Relevant file is not loaded: {path}"
        )
