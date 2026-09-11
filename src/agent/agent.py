from .conversation import Conversation
from .prompt_builder import PromptBuilder


class Agent:
    def __init__(self, llm_client):
        self.llm_client = llm_client
        self.conversation = Conversation()
        self.prompt_builder = PromptBuilder()

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

    def clear_conversation(self):
        self.conversation.clear()
