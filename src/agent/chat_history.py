from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .message import Message


@dataclass
class ChatHistory:
    id: str
    name: str
    created_at: datetime
    messages: list[Message] = field(default_factory=list)
    project_path: Path | None = None
    