from __future__ import annotations

from openai import OpenAI

from providers.base import LLMProvider
from utils.models import ProviderSettings


class AzureFoundryProvider(LLMProvider):
    def __init__(self, settings: ProviderSettings) -> None:
        self.settings = settings
        base_url = settings.azure_endpoint.rstrip("/")
        if settings.azure_api_version:
            base_url = f"{base_url}/openai/v1/?api-version={settings.azure_api_version}"
        else:
            base_url = f"{base_url}/openai/v1/"
        self.client = OpenAI(
            api_key=settings.azure_api_key,
            base_url=base_url,
        )

    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        response = self.client.chat.completions.create(
            model=self.settings.azure_deployment,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    def chat(self, messages: list[dict[str, str]]) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.azure_deployment,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    def extract(self, text: str, schema_hint: str) -> str:
        prompt = f"Extract structured data using this schema hint:\n{schema_hint}\n\nText:\n{text}"
        return self.generate(prompt, "You extract structured resume and job requirement data.")

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        prompt = (
            f"Translate and localize the following text from {source_language} to {target_language}. "
            "Preserve professional resume tone and avoid literal translation.\n\n"
            f"{text}"
        )
        return self.generate(prompt, "You are an expert resume localization specialist.")

    def analyze_resume(self, text: str) -> str:
        return self.generate(text, "Analyze this resume and extract structured candidate intelligence.")

    def analyze_jd(self, text: str) -> str:
        return self.generate(text, "Analyze this job description and extract structured requirement intelligence.")
