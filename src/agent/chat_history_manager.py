from datetime import datetime
from pathlib import Path
from uuid import uuid4

from .chat_history import ChatHistory


class ChatHistoryManager:
    def __init__(self):
        self._chats: dict[str, ChatHistory] = {}

    def create_chat(self, name="New Chat", project_path=None):
        chat_id = str(uuid4())

        chat = ChatHistory(
            id=chat_id,
            name=name,
            created_at=datetime.now(),
            project_path=Path(project_path).resolve()
            if project_path is not None
            else None
        )

        self._chats[chat_id] = chat
        return chat

    def get_chat(self, chat_id):
        return self._chats.get(chat_id)

    def get_all_chats(self):
        return list(self._chats.values())

    def rename_chat(self, chat_id, new_name):
        chat = self.get_chat(chat_id)

        if chat is None:
            raise ValueError(
                f"Chat not found: {chat_id}"
            )

        if not new_name or not new_name.strip():
            raise ValueError(
                "Chat name cannot be empty."
            )

        chat.name = new_name.strip()

        return chat

    def delete_chat(self, chat_id):
        if chat_id not in self._chats:
            raise ValueError(f"Chat not found: {chat_id}")

        return self._chats.pop(chat_id)
