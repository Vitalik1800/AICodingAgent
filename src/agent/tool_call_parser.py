import json

from .tool_call import ToolCall


class ToolCallParser:
    def parse(self, response):
        if not response:
            raise ValueError("Tool call response cannot be empty.")

        response = response.strip()

        if response.startswith("```") and response.endswith("```"):
            lines = response.splitlines()

            if len(lines) >= 3:
                response = "\n".join(lines[1:-1]).strip()

        try:
            data = json.loads(response)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Invalid tool call JSON."
            ) from error

        if not isinstance(data, dict):
            raise ValueError(
                "Tool call must be a JSON object."
            )

        if data.get("type") != "tool_call":
            raise ValueError(
                "Response is not a tool call."
            )

        tool = data.get("tool")
        arguments = data.get("arguments", {})

        if not tool or not isinstance(tool, str):
            raise ValueError(
                "Tool call must contain a valid 'tool' field."
            )

        if not isinstance(arguments, dict):
            raise ValueError(
                "Tool call 'arguments' must be an object."
            )

        return ToolCall(
            tool=tool,
            arguments=arguments,
        )
