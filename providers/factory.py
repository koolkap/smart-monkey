from __future__ import annotations

from providers.azure_foundry import AzureFoundryProvider
from providers.base import LLMProvider
from providers.claude import ClaudeProvider
from providers.gemini import GeminiProvider
from providers.ollama import OllamaProvider
from utils.models import ProviderSettings


def build_provider(settings: ProviderSettings) -> LLMProvider:
    provider = settings.provider.lower()
    if provider == "azure foundry":
        return AzureFoundryProvider(settings)
    if provider == "claude":
        return ClaudeProvider(settings)
    if provider == "gemini":
        return GeminiProvider(settings)
    if provider == "openai compatible":
        return AzureFoundryProvider(
            ProviderSettings(
                provider="azure foundry",
                azure_endpoint=settings.openai_endpoint,
                azure_api_key=settings.openai_api_key,
                azure_deployment=settings.openai_model,
                azure_api_version="",
            )
        )
    return OllamaProvider(settings)
