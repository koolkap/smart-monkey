from __future__ import annotations

from utils.models import ATSReport, RequirementProfile, ResumeProfile


def score_resume(profile: ResumeProfile, requirements: RequirementProfile) -> ATSReport:
    resume_skills = {skill.lower() for skill in profile.skills}
    required_skills = {skill.lower() for skill in requirements.skills + requirements.technologies + requirements.keywords}
    required_skills = {skill for skill in required_skills if skill}
    role_terms = {term.lower() for term in [requirements.title, *requirements.keywords[:6]] if term}

    matched = sorted(skill for skill in required_skills if skill in resume_skills)
    missing = sorted(skill.title() for skill in required_skills if skill not in resume_skills)
    weak_keywords = missing[:5]
    strength_areas = [skill.title() for skill in matched[:6]]
    resume_strengths = strength_areas + profile.soft_skills[:3]
    resume_weaknesses = []

    match_ratio = len(matched) / max(len(required_skills), 1)
    keyword_density = len(matched) / max(len(profile.skills), 1)
    ats_score = min(100, int(match_ratio * 70 + keyword_density * 30))
    recruiter_visibility = min(100, int(ats_score * 0.9 + len(profile.experience) * 4))
    skill_match = min(100, int((len(matched) / max(len(requirements.skills), 1)) * 100))
    experience_match = min(100, int((len(profile.experience) / max(len(requirements.responsibilities[:4]), 1)) * 100))
    role_match = min(
        100,
        int(
            sum(1 for term in role_terms if term and term in f"{profile.headline} {profile.summary}".lower())
            / max(len(role_terms), 1)
            * 100
        ),
    )
    industry_relevance = min(100, int((len(matched) + len(profile.soft_skills)) * 8))
    years_of_experience = _estimate_years_of_experience(profile)

    section_scores = {
        "Summary": min(100, 55 + len(profile.summary.split()) // 3 if profile.summary else 35),
        "Experience": min(100, 45 + len(profile.experience) * 12 + len(profile.achievements_summary) * 4),
        "Skills": min(100, 40 + len(profile.skills) * 5),
        "Projects": min(100, 35 + len(profile.projects) * 15),
        "Education": 80 if profile.education else 35,
        "Formatting": min(100, 60 + len(profile.contact.email) * 0 + (10 if profile.name and profile.summary else 0)),
        "Keyword": min(100, int(match_ratio * 100)),
    }

    suggestions = []
    if missing:
        suggestions.append(f"Address missing skills: {', '.join(missing[:5])}.")
    if not profile.summary:
        suggestions.append("Add a targeted professional summary aligned to the role.")
    if len(profile.skills) < 8:
        suggestions.append("Expand the skills section with verified tools and platforms from your experience.")
        resume_weaknesses.append("Skills section is too narrow for ATS breadth.")
    if not profile.achievements_summary:
        resume_weaknesses.append("Experience bullets need stronger quantified outcomes.")
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
    expected_screening_result = "Likely shortlist" if ats_score >= 80 else "Possible recruiter review" if ats_score >= 65 else "Needs optimization before applying"
    recruiter_decision = "PASS" if ats_score >= 75 and skill_match >= 65 else "LIKELY REJECTED"
    recruiter_decision_reason = (
        "The resume aligns with the target role, covers core skills, and presents enough evidence for recruiter review."
        if recruiter_decision == "PASS"
        else "The resume is missing too many role-specific skills or keywords and needs stronger alignment before submission."
    )
    scoring_explanations = [
        f"ATS score is driven by {len(matched)} matched requirement keywords out of {len(required_skills)}.",
        f"Recruiter visibility improves with stronger keyword coverage and clearer achievement framing.",
        f"Industry relevance reflects overlap between role-specific tools, technologies, and communication signals.",
    ]

    return ATSReport(
        ats_score=ats_score,
        match_percentage=int(match_ratio * 100),
        recruiter_visibility_score=recruiter_visibility,
        skill_match_percentage=skill_match,
        experience_match_percentage=experience_match,
        role_match_percentage=role_match,
        industry_relevance_score=industry_relevance,
        keyword_density=round(keyword_density, 2),
        missing_skills=missing,
        missing_keywords=missing,
        weak_keywords=weak_keywords,
        strength_areas=strength_areas,
        resume_weaknesses=resume_weaknesses,
        resume_strengths=resume_strengths,
        suggested_improvements=suggestions,
        gap_analysis=gap_analysis,
        role_fit_analysis=role_fit,
        career_level_estimation=career_level,
        expected_screening_result=expected_screening_result,
        scoring_explanations=scoring_explanations,
        recruiter_decision=recruiter_decision,
        recruiter_decision_reason=recruiter_decision_reason,
        years_of_experience=years_of_experience,
        section_scores=section_scores,
    )


def _estimate_years_of_experience(profile: ResumeProfile) -> str:
    if not profile.experience:
        return "0-1 years"
    if len(profile.experience) >= 5:
        return "8+ years"
    if len(profile.experience) >= 3:
        return "5-7 years"
    if len(profile.experience) >= 2:
        return "3-5 years"
    return "1-3 years"

