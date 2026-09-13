class ContextFormatter:
    def format(self, context):
        sections = []

        sections.append("PROJECT CONTEXT")
        sections.append("")
        sections.append(f"Project: {context.name}")
        sections.append(f"Root: {context.root_path}")

        sections.append("")
        sections.append("STRUCTURE:")

        if context.formatted_structure:
            sections.append(context.formatted_structure)
        else:
            sections.append("(empty)")

        sections.append("")
        sections.append("RELEVANT FILES: ")

        if context.relevant_files:
            for relevant_file in context.relevant_files:
                sections.append("")
                sections.append(
                    f"FILE: {relevant_file.path}"
                )
                sections.append(relevant_file.content)
        else:
            sections.append("(none)")

        return "\n".join(sections)
