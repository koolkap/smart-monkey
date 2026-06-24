from __future__ import annotations

import anthropic

from providers.base import LLMProvider
from utils.models import ProviderSettings


class ClaudeProvider(LLMProvider):
    def __init__(self, settings: ProviderSettings) -> None:
        self.settings = settings
        self.client = anthropic.Anthropic(api_key=settings.anthropic_api_key)

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        response = self.client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=4096,
            temperature=0.2,
            system=system_prompt or "",
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if getattr(block, "text", None))

    def chat(self, messages: list[dict[str, str]]) -> str:
        system_prompt = ""
        converted_messages: list[dict[str, str]] = []
        for message in messages:
            if message["role"] == "system":
                system_prompt = message["content"]
            else:
                converted_messages.append(message)
        response = self.client.messages.create(
            model=self.settings.anthropic_model,
            max_tokens=4096,
            temperature=0.2,
            system=system_prompt,
            messages=converted_messages,
        )
        return "".join(block.text for block in response.content if getattr(block, "text", None))

    def extract(self, text: str, schema_hint: str) -> str:
        return self.generate(
            f"Schema hint:\n{schema_hint}\n\nText:\n{text}",
            "Extract structured data accurately. Never invent experience.",
        )

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        return self.generate(
            f"Localize this resume content from {source_language} to {target_language}:\n\n{text}",
            "You are a bilingual recruiter and resume writer.",
        )

    def analyze_resume(self, text: str) -> str:
        return self.generate(text, "Analyze this resume and return structured candidate intelligence.")

    def analyze_jd(self, text: str) -> str:
        return self.generate(text, "Analyze this job description and return structured requirement intelligence.")
