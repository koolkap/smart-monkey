from __future__ import annotations

import json

from providers.base import LLMProvider
from utils.resume_builder import normalize_resume_profile
from utils.models import ResumeProfile


def localize_resume(profile: ResumeProfile, provider: LLMProvider, target_language: str) -> ResumeProfile:
    payload = json.dumps(profile.to_dict(), ensure_ascii=False, indent=2)
    prompt = f"""
You are localizing a resume profile from English into {target_language}.

Return valid JSON only.
Preserve the exact schema and field structure from the input.
Do not add, remove, infer, or embellish facts.
Do not invent employers, dates, achievements, tools, certifications, or metrics.
If a phrase is uncertain, translate conservatively.

Style requirements:
- Write naturally for a real {target_language}-speaking recruiter.
- Avoid machine-translated phrasing.
- Avoid overly literal sentence structure.
- Avoid promotional tone and exaggerated claims.
- Avoid em dash style punctuation and GPT-like rhythm.
- Keep resume bullets concise, direct, and professional.
- Prefer standard business wording used in real resumes in {target_language}.

Input JSON:
{payload}
""".strip()
    translated = provider.generate(prompt)
    try:
        data = json.loads(translated)
        return normalize_resume_profile(data)
    except Exception:
        localized = normalize_resume_profile(profile)
        localized.summary = provider.generate(
            f"Translate this resume summary into natural {target_language}. Keep it concise, factual, and recruiter-friendly. Avoid em dash punctuation and avoid AI-sounding phrasing. Text: {profile.summary}"
        )
        localized.headline = provider.generate(
            f"Translate this resume headline into natural {target_language}. Keep it short, professional, and factual. Avoid em dash punctuation and avoid AI-sounding phrasing. Text: {profile.headline or profile.summary[:80]}"
        )
        return localized
