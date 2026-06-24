from __future__ import annotations

import google.generativeai as genai

from providers.base import LLMProvider
from utils.models import ProviderSettings


class GeminiProvider(LLMProvider):
    def __init__(self, settings: ProviderSettings) -> None:
        self.settings = settings
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        full_prompt = f"{system_prompt or ''}\n\n{prompt}".strip()
        response = self.model.generate_content(full_prompt)
        return getattr(response, "text", "") or ""

    def chat(self, messages: list[dict[str, str]]) -> str:
        prompt = "\n".join(f"{message['role']}: {message['content']}" for message in messages)
        return self.generate(prompt)

    def extract(self, text: str, schema_hint: str) -> str:
        return self.generate(f"Extract using schema hint:\n{schema_hint}\n\n{text}")

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        return self.generate(
            f"Translate and localize from {source_language} to {target_language}:\n\n{text}",
            "Use professional hiring terminology and natural phrasing.",
        )
