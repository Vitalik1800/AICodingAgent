from .message import Message


class PromptBuilder:
    def __init__(self, context_formatter=None):
        self.context_formatter = context_formatter

    def build(self, messages, project_context=None):
        prompt_parts = []

        if project_context is not None:
            if self.context_formatter is None:
                raise ValueError(
                    "Context formatter is required for project context."
                )

            project_context_text = self.context_formatter.format(
                project_context
            )

            prompt_parts.append(project_context_text)

        for message in messages:
            if isinstance(message, Message):
                role = message.role
                content = message.content
            else:
                role = message["role"]
                content = message["content"]

            if role == "tool":
                prompt_parts.append(content)
            else:
                prompt_parts.append(
                    f"{role.upper()}: {content}"
                )

        prompt_parts.append("ASSISTANT: ")

        return "\n\n".join(prompt_parts)
