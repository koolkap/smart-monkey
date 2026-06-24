from __future__ import annotations

import requests

from providers.base import LLMProvider
from utils.models import ProviderSettings


class OllamaProvider(LLMProvider):
    def __init__(self, settings: ProviderSettings) -> None:
        self.settings = settings

    def _post(self, prompt: str, system_prompt: str | None = None) -> str:
        response = requests.post(
            f"{self.settings.ollama_url.rstrip('/')}/api/generate",
            json={
                "model": self.settings.ollama_model,
                "prompt": prompt,
                "system": system_prompt or "",
                "stream": False,
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "")

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        return self._post(prompt, system_prompt)

    def chat(self, messages: list[dict[str, str]]) -> str:
        prompt = "\n".join(f"{message['role']}: {message['content']}" for message in messages)
        return self._post(prompt)

    def extract(self, text: str, schema_hint: str) -> str:
        return self._post(f"Extract structured data using schema hint:\n{schema_hint}\n\n{text}")

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        return self._post(
            f"Translate and localize from {source_language} to {target_language}:\n\n{text}",
            "You are a professional resume localization expert.",
        )
