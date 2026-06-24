from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str | None = None) -> str:
        raise NotImplementedError

    @abstractmethod
    def chat(self, messages: list[dict[str, str]]) -> str:
        raise NotImplementedError

    @abstractmethod
    def extract(self, text: str, schema_hint: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def translate(self, text: str, source_language: str, target_language: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def analyze_resume(self, text: str) -> str:
        raise NotImplementedError

    @abstractmethod
    def analyze_jd(self, text: str) -> str:
        raise NotImplementedError

    def stream(self, prompt: str, system_prompt: str | None = None) -> Any:
        yield self.generate(prompt, system_prompt)
