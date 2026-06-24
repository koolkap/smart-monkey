from __future__ import annotations

from utils.models import ATSReport, RequirementProfile, ResumeProfile


def score_resume(profile: ResumeProfile, requirements: RequirementProfile) -> ATSReport:
    resume_skills = {skill.lower() for skill in profile.skills}
    required_skills = {skill.lower() for skill in requirements.skills + requirements.technologies + requirements.keywords}
    required_skills = {skill for skill in required_skills if skill}

    matched = sorted(skill for skill in required_skills if skill in resume_skills)
    missing = sorted(skill.title() for skill in required_skills if skill not in resume_skills)
    weak_keywords = missing[:5]
    strength_areas = [skill.title() for skill in matched[:6]]

    match_ratio = len(matched) / max(len(required_skills), 1)
    keyword_density = len(matched) / max(len(profile.skills), 1)
    ats_score = min(100, int(match_ratio * 70 + keyword_density * 30))
    recruiter_visibility = min(100, int(ats_score * 0.9 + len(profile.experience) * 4))

    suggestions = []
    if missing:
        suggestions.append(f"Address missing skills: {', '.join(missing[:5])}.")
    if not profile.summary:
        suggestions.append("Add a targeted professional summary aligned to the role.")
    if len(profile.skills) < 8:
        suggestions.append("Expand the skills section with verified tools and platforms from your experience.")
    if not suggestions:
        suggestions.append("Resume is well aligned. Focus on quantifying achievements for stronger recruiter impact.")

    gap_analysis = [
        f"Experience level target appears to be {requirements.experience_level}.",
        f"Missing capability coverage: {', '.join(missing[:4]) or 'No major gaps detected'}.",
    ]

    role_fit = (
        "Strong fit for the target role based on overlapping skills and relevant experience."
        if ats_score >= 75
        else "Partial fit. Resume should be tailored further to emphasize role-specific outcomes and keywords."
    )
    career_level = requirements.experience_level or "Mid-Level"

    return ATSReport(
        ats_score=ats_score,
        match_percentage=int(match_ratio * 100),
        recruiter_visibility_score=recruiter_visibility,
        keyword_density=round(keyword_density, 2),
        missing_skills=missing,
        weak_keywords=weak_keywords,
        strength_areas=strength_areas,
        suggested_improvements=suggestions,
        gap_analysis=gap_analysis,
        role_fit_analysis=role_fit,
        career_level_estimation=career_level,
    )
