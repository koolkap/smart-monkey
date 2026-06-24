from __future__ import annotations

import json
import os
from pathlib import Path

from dotenv import load_dotenv

from utils.models import ProviderSettings


SETTINGS_PATH = Path("data") / "settings.json"
ENV_PATH = Path(".env")


def _env_overrides() -> dict[str, str]:
    load_dotenv(dotenv_path=ENV_PATH, override=True)
    mapping = {
        "provider": "RESUMEFORGE_PROVIDER",
        "azure_endpoint": "AZURE_FOUNDRY_ENDPOINT",
        "azure_api_key": "AZURE_FOUNDRY_API_KEY",
        "azure_deployment": "AZURE_FOUNDRY_DEPLOYMENT",
        "azure_api_version": "AZURE_FOUNDRY_API_VERSION",
        "openai_endpoint": "OPENAI_COMPATIBLE_ENDPOINT",
        "openai_api_key": "OPENAI_COMPATIBLE_API_KEY",
        "openai_model": "OPENAI_COMPATIBLE_MODEL",
        "anthropic_api_key": "ANTHROPIC_API_KEY",
        "anthropic_model": "ANTHROPIC_MODEL",
        "gemini_api_key": "GEMINI_API_KEY",
        "gemini_model": "GEMINI_MODEL",
        "ollama_url": "OLLAMA_URL",
        "ollama_model": "OLLAMA_MODEL",
    }
    overrides: dict[str, str] = {}
    for field_name, env_name in mapping.items():
        value = os.getenv(env_name)
        if value is not None and value != "":
            overrides[field_name] = value
    return overrides


def load_settings() -> ProviderSettings:
    data: dict[str, str] = {}
    if not SETTINGS_PATH.exists():
        data = {}
    else:
        data = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    data.update(_env_overrides())
    return ProviderSettings(**data)


def save_settings(settings: ProviderSettings) -> None:
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SETTINGS_PATH.write_text(json.dumps(settings.to_dict(), indent=2), encoding="utf-8")
