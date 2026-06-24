from __future__ import annotations

from utils.models import AIInsights, ATSReport, InterviewReadinessReport, RecruiterSimulation, RequirementProfile, ResumeProfile


def build_ai_insights(profile: ResumeProfile, requirements: RequirementProfile, ats: ATSReport) -> AIInsights:
    likely_questions = [
        f"How have you applied {skill} in production?" for skill in (requirements.skills[:3] or profile.skills[:3])
    ]
    talking_points = profile.achievements_summary[:4] or [profile.summary]
    risk_areas = ats.missing_skills[:4] or ["Need stronger quantified outcomes in recent experience."]
    recruiter_feedback = [
        "Resume is readable and role-aligned.",
        "Add more measurable business impact in the top two experience entries.",
        "Ensure the summary mirrors the target role language more directly.",
    ]
    return AIInsights(
        role_match_analysis=ats.role_fit_analysis,
        interview_readiness=InterviewReadinessReport(
            readiness_score=min(100, ats.ats_score + 5),
            likely_questions=likely_questions,
            talking_points=talking_points,
            risk_areas=risk_areas,
        ),
        recruiter_simulation=RecruiterSimulation(
            first_impression="Strong professional profile with clear ATS alignment." if ats.ats_score >= 75 else "Promising profile but needs tighter role targeting.",
            recruiter_feedback=recruiter_feedback,
            shortlist_probability=min(100, ats.ats_score),
        ),
        career_gap_analysis=ats.gap_analysis,
        promotion_readiness_analysis=(
            "Profile shows senior-level ownership signals and promotion readiness."
            if "Senior" in ats.career_level_estimation or ats.ats_score >= 80
            else "Profile is progressing well but needs stronger leadership and impact evidence for promotion readiness."
        ),
        skill_recommendations=ats.missing_skills[:6],
        resume_quality_score=min(100, int((ats.ats_score + ats.recruiter_visibility_score) / 2)),
        application_success_prediction=min(100, int((ats.ats_score + ats.skill_match_percentage + ats.industry_relevance_score) / 3)),
    )