class ProjectStructureFormatter:
    def format(self, structure):
        lines = []

        for node in structure:
            self._format_node(node, lines, level=0)

        return "\n".join(lines)

    def _format_node(self, node, lines, level):
        indent = "  " * level

        if node.item_type == "directory":
            lines.append(f"{indent}[DIR] {node.path.name}/")

            for child in node.children:
                self._format_node(
                    child,
                    lines,
                    level + 1
                )

        else:
            lines.append(
                f"{indent}[FILE] {node.path.name}"
            )
