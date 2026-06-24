from __future__ import annotations

import json

from providers.base import LLMProvider
from utils.resume_builder import normalize_resume_profile
from utils.models import ResumeProfile


def localize_resume(profile: ResumeProfile, provider: LLMProvider, target_language: str) -> ResumeProfile:
    payload = json.dumps(profile.to_dict(), ensure_ascii=False, indent=2)
    translated = provider.translate(payload, "English", target_language)
    try:
        data = json.loads(translated)
        return normalize_resume_profile(data)
    except Exception:
        localized = normalize_resume_profile(profile)
        localized.summary = provider.translate(profile.summary, "English", target_language)
        localized.headline = provider.translate(profile.headline or profile.summary[:80], "English", target_language)
        return localized
