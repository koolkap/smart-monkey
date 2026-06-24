from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ContactInfo:
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""


@dataclass
class ExperienceItem:
    title: str = ""
    company: str = ""
    location: str = ""
    start_date: str = ""
    end_date: str = ""
    achievements: list[str] = field(default_factory=list)


@dataclass
class EducationItem:
    institution: str = ""
    degree: str = ""
    field_of_study: str = ""
    start_date: str = ""
    end_date: str = ""


@dataclass
class ProjectItem:
    name: str = ""
    description: str = ""
    technologies: list[str] = field(default_factory=list)
    link: str = ""


@dataclass
class CertificationItem:
    name: str = ""
    issuer: str = ""
    year: str = ""


@dataclass
class ResumeProfile:
    name: str = ""
    headline: str = ""
    summary: str = ""
    contact: ContactInfo = field(default_factory=ContactInfo)
    skills: list[str] = field(default_factory=list)
    experience: list[ExperienceItem] = field(default_factory=list)
    education: list[EducationItem] = field(default_factory=list)
    projects: list[ProjectItem] = field(default_factory=list)
    certifications: list[CertificationItem] = field(default_factory=list)
    publications: list[str] = field(default_factory=list)
    awards: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RequirementProfile:
    title: str = ""
    company: str = ""
    summary: str = ""
    responsibilities: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    experience_level: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ATSReport:
    ats_score: int
    match_percentage: int
    recruiter_visibility_score: int
    keyword_density: float
    missing_skills: list[str]
    weak_keywords: list[str]
    strength_areas: list[str]
    suggested_improvements: list[str]
    gap_analysis: list[str]
    role_fit_analysis: str
    career_level_estimation: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ProviderSettings:
    provider: str = "ollama"
    azure_endpoint: str = ""
    azure_api_key: str = ""
    azure_deployment: str = ""
    openai_endpoint: str = ""
    openai_api_key: str = ""
    openai_model: str = ""
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-5-sonnet-20240620"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-pro"
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
