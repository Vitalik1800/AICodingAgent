from dataclasses import dataclass
from typing import Any


@dataclass
class ToolResult:
    tool: str
    success: bool
    result: Any = None
    error: str | None = None
