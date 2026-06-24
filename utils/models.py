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
    soft_skills: list[str] = field(default_factory=list)
    target_roles: list[str] = field(default_factory=list)
    achievements_summary: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RequirementProfile:
    title: str = ""
    company: str = ""
    summary: str = ""
    responsibilities: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    soft_skills: list[str] = field(default_factory=list)
    technologies: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)
    certifications: list[str] = field(default_factory=list)
    experience_level: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ATSReport:
    ats_score: int
    match_percentage: int
    recruiter_visibility_score: int
    skill_match_percentage: int
    industry_relevance_score: int
    keyword_density: float
    missing_skills: list[str]
    missing_keywords: list[str]
    weak_keywords: list[str]
    strength_areas: list[str]
    resume_weaknesses: list[str]
    resume_strengths: list[str]
    suggested_improvements: list[str]
    gap_analysis: list[str]
    role_fit_analysis: str
    career_level_estimation: str
    expected_screening_result: str
    scoring_explanations: list[str]
    experience_match_percentage: int = 0
    role_match_percentage: int = 0
    recruiter_decision: str = "LIKELY REJECTED"
    recruiter_decision_reason: str = ""
    years_of_experience: str = ""
    section_scores: dict[str, int] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DesignIntelligence:
    layout_style: str = "single-column"
    typography: str = "professional serif"
    font_hierarchy: list[str] = field(default_factory=list)
    margins: str = "balanced"
    section_arrangement: list[str] = field(default_factory=list)
    white_space: str = "moderate"
    color_palette: list[str] = field(default_factory=list)
    header_structure: str = "hero"
    sidebar_structure: str = "none"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InterviewReadinessReport:
    readiness_score: int
    likely_questions: list[str] = field(default_factory=list)
    talking_points: list[str] = field(default_factory=list)
    risk_areas: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RecruiterSimulation:
    first_impression: str
    recruiter_feedback: list[str] = field(default_factory=list)
    shortlist_probability: int = 0

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class AIInsights:
    role_match_analysis: str = ""
    interview_readiness: InterviewReadinessReport = field(
        default_factory=lambda: InterviewReadinessReport(readiness_score=0)
    )
    recruiter_simulation: RecruiterSimulation = field(
        default_factory=lambda: RecruiterSimulation(first_impression="", shortlist_probability=0)
    )
    career_gap_analysis: list[str] = field(default_factory=list)
    promotion_readiness_analysis: str = ""
    skill_recommendations: list[str] = field(default_factory=list)
    resume_quality_score: int = 0
    application_success_prediction: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "role_match_analysis": self.role_match_analysis,
            "interview_readiness": self.interview_readiness.to_dict(),
            "recruiter_simulation": self.recruiter_simulation.to_dict(),
            "career_gap_analysis": self.career_gap_analysis,
            "promotion_readiness_analysis": self.promotion_readiness_analysis,
            "skill_recommendations": self.skill_recommendations,
            "resume_quality_score": self.resume_quality_score,
            "application_success_prediction": self.application_success_prediction,
        }


@dataclass
class ProviderSettings:
    provider: str = "ollama"
    azure_endpoint: str = ""
    azure_api_key: str = ""
    azure_deployment: str = ""
    azure_api_version: str = "2025-01-01-preview"
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


@dataclass
class WorkflowArtifacts:
    base_profile: ResumeProfile = field(default_factory=ResumeProfile)
    optimized_profile: ResumeProfile = field(default_factory=ResumeProfile)
    localized_profile: ResumeProfile = field(default_factory=ResumeProfile)
    requirements: RequirementProfile = field(default_factory=RequirementProfile)
    ats_report: ATSReport | None = None
    design_intelligence: DesignIntelligence | None = None
    ai_insights: AIInsights | None = None
    english_html: str = ""
    korean_html: str = ""
    active_language: str = "English"
    selected_theme: str = "Modern ATS"
    selected_route: str = "/upload"
    selected_variant: str = "ATS Optimized"

    def to_dict(self) -> dict[str, Any]:
        return {
            "base_profile": self.base_profile.to_dict(),
            "optimized_profile": self.optimized_profile.to_dict(),
            "localized_profile": self.localized_profile.to_dict(),
            "requirements": self.requirements.to_dict(),
            "ats_report": self.ats_report.to_dict() if self.ats_report else None,
            "design_intelligence": self.design_intelligence.to_dict() if self.design_intelligence else None,
            "ai_insights": self.ai_insights.to_dict() if self.ai_insights else None,
            "english_html": self.english_html,
            "korean_html": self.korean_html,
            "active_language": self.active_language,
            "selected_theme": self.selected_theme,
            "selected_route": self.selected_route,
            "selected_variant": self.selected_variant,
        }
