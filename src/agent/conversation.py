from .message import Message


class Conversation:
    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        message = Message(
            role=role,
            content=content
        )

        self.messages.append(message)

    def get_messages(self):
        return self.messages.copy()

    def clear(self):
        self.messages.clear()
