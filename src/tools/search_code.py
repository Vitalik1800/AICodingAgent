from .project_path import ProjectPath


class SearchCodeTool:
    SOURCE_DIRS = {
        "src",
        "app",
        "lib",
        "tests",
        "test",
    }

    DOCUMENTATION_EXTENSIONS = {
        ".md",
        ".txt",
        ".rst",
    }

    def __init__(self, project_path="."):
        self.project_path = ProjectPath(project_path)

    def execute(self, query):
        if not query:
            raise ValueError("Search query cannot be empty.")

        results = []
        query_lower = query.lower()

        for path in self.project_path.root.rglob("*"):
            if not path.is_file():
                continue

            if self.project_path.is_ignored(path):
                continue

            try:
                content = path.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue

            relative_path = path.relative_to(self.project_path.root)
            relative_parts = relative_path.parts

            if any(part.lower() in self.SOURCE_DIRS for part in relative_parts):
                priority = 0
            elif path.suffix.lower() in self.DOCUMENTATION_EXTENSIONS:
                priority = 2
            elif path.name.lower() == "package-lock.json":
                priority = 3
            else:
                priority = 1

            for line_number, line in enumerate(
                content.splitlines(),
                start=1
            ):
                if query_lower in line.lower():
                    results.append(
                        {
                            "file": str(relative_path),
                            "line": line_number,
                            "content": line.strip(),
                            "_priority": priority,
                        }
                    )

        results.sort(
            key=lambda result: (
                result["_priority"],
                result["file"].lower(),
                result["line"],
            )
        )

        for result in results:
            result.pop("_priority")

        return results
