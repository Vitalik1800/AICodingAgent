from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ProjectItem:
    path: Path
    item_type: str


@dataclass
class ProjectTreeNode:
    path: Path
    item_type: str
    children: list["ProjectTreeNode"] = field(default_factory=list)
