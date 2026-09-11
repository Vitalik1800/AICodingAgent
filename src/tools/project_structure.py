from dataclasses import dataclass
from pathlib import Path


@dataclass
class ProjectItem:
    path: Path
    item_type: str
