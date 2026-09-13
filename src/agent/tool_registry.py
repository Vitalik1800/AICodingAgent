from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolDefinition:
    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)


class ToolRegistry:
    def __init__(self):
        self._tools = {}
        self._definitions = {}

    def register(self, name, tool, definition=None):
        if not name:
            raise ValueError("Tool name cannot be empty.")

        if name in self._tools:
            raise ValueError(
                f"Tool '{name}' is already registered."
            )

        self._tools[name] = tool

        if definition is not None:
            self._definitions[name] = definition

    def get(self, name):
        return self._tools.get(name)

    def has(self, name):
        return name in self._tools

    def get_all(self):
        return self._tools.copy()

    def names(self):
        return list(self._tools.keys())

    def get_definition(self, name):
        return self._definitions.get(name)

    def get_definitions(self):
        return self._definitions.copy()

    def execute(self, name, *args, **kwargs):
        tool = self.get(name)

        if tool is None:
            raise ValueError(
                f"Tool '{name}' is not registered."
            )

        return tool.execute(*args, **kwargs)

    def execute_call(self, tool_call):
        if tool_call.tool not in self._tools:
            raise ValueError(
                f"Tool '{tool_call.tool} is not registered."
            )

        tool = self._tools[tool_call.tool]

        return tool.execute(**tool_call.arguments)
