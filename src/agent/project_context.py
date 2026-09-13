from dataclasses import dataclass, field
from pathlib import Path

from .project_structure_formatter import ProjectStructureFormatter
from .relevant_file_context import RelevantFileContext


@dataclass
class ProjectContext:
    name: str
    root_path: Path
    structure: list = field(default_factory=list)
    relevant_files: list[RelevantFileContext] = field(default_factory=list)

    @property
    def formatted_structure(self):
        return ProjectStructureFormatter().format(
            self.structure
        )
