from .message import Message


class PromptBuilder:
    def build(self, messages):
        prompt_parts = []

        for message in messages:
            if isinstance(message, Message):
                role = message.role
                content = message.content
            else:
                role = message["role"]
                content = message["content"]

            prompt_parts.append(
                f"{role.upper()}: {content}"
            )

        prompt_parts.append("ASSISTANT: ")

        return "\n\n".join(prompt_parts)
