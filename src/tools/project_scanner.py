from pathlib import Path

from .project_path import ProjectPath
from .project_structure import ProjectItem, ProjectTreeNode


class ProjectScanner:
    DEFAULT_IGNORE_DIRS = ProjectPath.DEFAULT_IGNORE_DIRS

    def __init__(self, project_path):
        self.project_path = ProjectPath(project_path)

    def scan(self):
        return list(self.project_path.root.iterdir())

    def get_files(self):
        return [
            item
            for item in self.scan()
            if item.is_file()
            and not self.project_path.is_ignored(item)
        ]

    def get_structure(self):
        structure = []

        for item in self.scan():
            if self.project_path.is_ignored(item):
                continue

            if item.is_dir():
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

    def get_tree_structure(self):
        return self._scan_directory(self.project_path.root)

    def _scan_directory(self, directory):
        nodes = []

        for item in sorted(
            directory.iterdir(),
            key=lambda path: (
                not path.is_dir(),
                path.name.lower()
            )
        ):
            if self.project_path.is_ignored(item):
                continue

            if item.is_dir():
                node = ProjectTreeNode(
                    path=item,
                    item_type="directory",
                    children=self._scan_directory(item)
                )

                nodes.append(node)

            elif item.is_file():
                nodes.append(
                    ProjectTreeNode(
                        path=item,
                        item_type="file"
                    )
                )

        return nodes
