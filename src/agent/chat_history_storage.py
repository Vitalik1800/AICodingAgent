import json
import os
import tempfile

from datetime import datetime
from pathlib import Path

from .chat_history import ChatHistory
from .message import Message


class ChatHistoryStorage:
    DEFAULT_FILE = (
            Path(__file__).resolve().parents[2]
            / "data"
            / "chat_history.json"
    )

    MAX_FILE_SIZE = 10 * 1024 * 1024
    MAX_CHATS = 100
    MAX_MESSAGES_PER_CHAT = 500
    MAX_MESSAGE_LENGTH = 100_000

    def __init__(self, file_path=None):
        self.file_path = (
            Path(file_path)
            if file_path is not None
            else self.DEFAULT_FILE
        )

    def save(self, chats):
        chats = list(chats)

        self._validate_chats(chats)

        self.file_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        data = []

        for chat in chats:
            data.append(
                {
                    "id": chat.id,
                    "name": chat.name,
                    "created_at": chat.created_at.isoformat(),
                    "messages": [
                        {
                            "role": message.role,
                            "content": message.content
                        }
                        for message in chat.messages
                    ],
                    "project_path": (
                        str(chat.project_path)
                        if chat.project_path is not None
                        else None
                    )
                }
            )

        content = json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        )

        content_size = len(
            content.encode("utf-8")
        )

        if content_size > self.MAX_FILE_SIZE:
            raise ValueError(
                "Chat history file exceeds the maximum "
                "allowed size of 10 MB."
            )

        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                    mode="w",
                    encoding="utf-8",
                    dir=self.file_path.parent,
                    prefix=f"{self.file_path.stem}_",
                    suffix=".tmp",
                    delete=False
            ) as temporary_file:
                temporary_file.write(content)
                temporary_file.flush()
                os.fsync(temporary_file.fileno())

                temporary_path = Path(
                    temporary_file.name
                )

            os.replace(
                temporary_path,
                self.file_path
            )

            temporary_path = None

        finally:
            if (
                    temporary_path is not None
                    and temporary_path.exists()
            ):
                temporary_path.unlink()

    def load(self):
        if not self.file_path.exists():
            return []

        try:
            file_size = self.file_path.stat().st_size
        except OSError as error:
            raise ValueError(
                "Unable to access chat history file."
            ) from error

        if file_size > self.MAX_FILE_SIZE:
            raise ValueError(
                "Chat history file exceeds the maximum "
                "allowed size of 10 MB."
            )

        try:
            content = self.file_path.read_text(
                encoding="utf-8"
            )
        except UnicodeDecodeError as error:
            raise ValueError(
                "Chat history file is not valid UTF-8."
            ) from error
        except OSError as error:
            raise ValueError(
                "Unable to read chat history file."
            ) from error

        if not content.strip():
            return []

        try:
            data = json.loads(content)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Chat history file contains invalid JSON."
            ) from error

        if not isinstance(data, list):
            raise ValueError(
                "Chat history root must be a list."
            )

        if len(data) > self.MAX_CHATS:
            raise ValueError(
                "Chat history contains more than "
                f"{self.MAX_CHATS} chats."
            )

        chats = []
        chat_ids = set()

        for item in data:
            if not isinstance(item, dict):
                raise ValueError(
                    "Invalid chat entry in chat history."
                )

            chat_id = item.get("id")
            name = item.get("name")
            created_at = item.get("created_at")
            messages_data = item.get("messages", [])
            project_path = item.get("project_path")

            if not isinstance(chat_id, str) or not chat_id:
                raise ValueError(
                    "Chat id must be a non-empty string."
                )

            if chat_id in chat_ids:
                raise ValueError(
                    f"Duplicate chat id found: {chat_id}"
                )

            chat_ids.add(chat_id)

            if not isinstance(name, str):
                raise ValueError(
                    "Chat name must be a string."
                )

            if not isinstance(created_at, str):
                raise ValueError(
                    "Chat created_at must be a string."
                )

            try:
                created_at = datetime.fromisoformat(
                    created_at
                )
            except ValueError as error:
                raise ValueError(
                    "Chat created_at contains an invalid "
                    "datetime value."
                ) from error

            if not isinstance(messages_data, list):
                raise ValueError(
                    "Chat messages must be a list."
                )

            if len(messages_data) > self.MAX_MESSAGES_PER_CHAT:
                raise ValueError(
                    "A chat contains more than "
                    f"{self.MAX_MESSAGES_PER_CHAT} messages."
                )

            messages = []

            for message in messages_data:
                if not isinstance(message, dict):
                    raise ValueError(
                        "Invalid message entry in chat history."
                    )

                role = message.get("role")
                message_content = message.get("content")

                if not isinstance(role, str) or not role:
                    raise ValueError(
                        "Message role must be a non-empty string."
                    )

                if not isinstance(message_content, str):
                    raise ValueError(
                        "Message content must be a string."
                    )

                if len(message_content) > self.MAX_MESSAGE_LENGTH:
                    raise ValueError(
                        "A message exceeds the maximum "
                        f"length of {self.MAX_MESSAGE_LENGTH} "
                        "characters."
                    )

                messages.append(
                    Message(
                        role=role,
                        content=message_content
                    )
                )

            if project_path is not None:
                if not isinstance(project_path, str):
                    raise ValueError(
                        "Chat project_path must be a string "
                        "or null."
                    )

                project_path = Path(project_path)

            chats.append(
                ChatHistory(
                    id=chat_id,
                    name=name,
                    created_at=created_at,
                    messages=messages,
                    project_path=project_path
                )
            )

        return chats

    def _validate_chats(self, chats):
        if len(chats) > self.MAX_CHATS:
            raise ValueError(
                "Cannot save more than "
                f"{self.MAX_CHATS} chats."
            )

        for chat in chats:
            if len(chat.messages) > self.MAX_MESSAGES_PER_CHAT:
                raise ValueError(
                    f"Chat '{chat.name}' contains more than "
                    f"{self.MAX_MESSAGES_PER_CHAT} messages."
                )

            for message in chat.messages:
                if not isinstance(message.content, str):
                    raise ValueError(
                        "Message content must be a string."
                    )

                if len(message.content) > self.MAX_MESSAGE_LENGTH:
                    raise ValueError(
                        f"Message in chat '{chat.name}' exceeds "
                        f"the maximum length of "
                        f"{self.MAX_MESSAGE_LENGTH} characters."
                    )
