from dataclasses import dataclass
from pathlib import Path


@dataclass
class RelevantFileContext:
    path: Path
    content: str
