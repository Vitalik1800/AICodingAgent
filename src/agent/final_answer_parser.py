import json


class FinalAnswerParser:
    def parse(self, response):
        if not response:
            raise ValueError(
                "Final answer response cannot be empty."
            )

        response = response.strip()

        if response.startswith("```") and response.endswith("```"):
            lines = response.splitlines()

            if len(lines) >= 3:
                response = "\n".join(lines[1:-1]).strip()

        try:
            data = json.loads(response)
        except json.JSONDecodeError as error:
            raise ValueError(
                "Invalid final answer JSON."
            ) from error

        if not isinstance(data, dict):
            raise ValueError(
                "Final answer must be a JSON object."
            )

        if data.get("type") != "final_answer":
            raise ValueError(
                "Response is not a final answer."
            )

        content = data.get("content")

        if not isinstance(content, str):
            raise ValueError(
                "Final answer 'content' must be a string."
            )

        if not content.strip():
            raise ValueError(
                "Final answer content cannot be empty."
            )

        return content.strip()
