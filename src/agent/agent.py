from ..tools.project_scanner import ProjectScanner
from .conversation import Conversation
from .prompt_builder import PromptBuilder


class Agent:
    def __init__(self, llm_client, project_path="."):
        self.llm_client = llm_client
        self.conversation = Conversation()
        self.prompt_builder = PromptBuilder()
        self.project_scanner = ProjectScanner(project_path)

    def ask(self, message):
        self.conversation.add_message(
            "user",
            message
        )

        messages = self.conversation.get_messages()

        prompt = self.prompt_builder.build(messages)

        response = self.llm_client.generate(prompt)

        self.conversation.add_message(
            "assistant",
            response
        )

        return response

    def get_project_structure(self):
        return self.project_scanner.get_structure()

    def clear_conversation(self):
        self.conversation.clear()
