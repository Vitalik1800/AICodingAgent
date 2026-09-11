import requests


class OllamaClient:
    DEFAULT_MODEL = "qwen2.5-coder:7b"

    def __init__(
        self,
        base_url="http://localhost:11434",
        model=DEFAULT_MODEL
    ):
        self.base_url = base_url.rstrip("/")
        self.model = model

    def is_available(self):
        try:
            response = requests.get(
                f"{self.base_url}/api/tags",
                timeout=5
            )

            return response.ok

        except requests.RequestException:
            return False

    def generate(
        self,
        prompt
    ):
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        if "response" not in data:
            raise ValueError(
                "Ollama response does not contain 'response' field."
            )

        return data["response"]
