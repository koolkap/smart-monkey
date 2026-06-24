from __future__ import annotations

import streamlit as st

from utils.models import ATSReport


def render_ats_report(report: ATSReport) -> None:
    st.subheader("Current Resume Analysis")

    score_cols = st.columns(6)
    score_cols[0].metric("ATS Score", f"{report.ats_score}%")
    score_cols[1].metric("Keyword Match", f"{report.match_percentage}%")
    score_cols[2].metric("Skills Match", f"{report.skill_match_percentage}%")
    score_cols[3].metric("Experience Match", f"{report.experience_match_percentage}%")
    score_cols[4].metric("Role Match", f"{report.role_match_percentage}%")
    score_cols[5].metric("Recruiter Visibility", f"{report.recruiter_visibility_score}%")

    st.progress(report.ats_score / 100, text=f"Visual ATS Gauge: {report.expected_screening_result}")

    left, right = st.columns([1.2, 0.8], gap="large")
    with left:
        st.markdown("### Missing Skills")
        _render_tag_list(report.missing_skills, "No major missing skills detected")

        st.markdown("### Missing Keywords")
        _render_tag_list(report.missing_keywords, "No major missing keywords detected")

        st.markdown("### Strengths")
        _render_bullets(report.strength_areas or report.resume_strengths, "Add more role-specific evidence")

        st.markdown("### Weaknesses")
        _render_bullets(report.resume_weaknesses, "No major weaknesses detected")

    with right:
        st.markdown("### Recruiter Simulation")
        if report.recruiter_decision == "PASS":
            st.success(f"{report.recruiter_decision}: {report.recruiter_decision_reason}")
        else:
            st.error(f"{report.recruiter_decision}: {report.recruiter_decision_reason}")

        st.markdown("### Section-by-Section Score")
        for section, score in report.section_scores.items():
            st.caption(f"{section} Score")
            st.progress(score / 100, text=f"{score}%")

        st.markdown("### Improvement Suggestions")
        _render_bullets(report.suggested_improvements, "No immediate suggestions")

    with st.expander("Scoring Notes", expanded=False):
        _render_bullets(report.scoring_explanations, "No scoring notes available")
        st.caption(f"Industry Alignment Score: {report.industry_relevance_score}%")
        st.caption(f"Keyword density: {report.keyword_density:.2f}")


def _render_tag_list(items: list[str], empty_message: str) -> None:
    if not items:
        st.info(empty_message)
        return
    cols = st.columns(2)
    for index, item in enumerate(items):
        cols[index % 2].markdown(f"- {item}")


def _render_bullets(items: list[str], empty_message: str) -> None:
    if not items:
        st.info(empty_message)
        return
    for item in items:
        st.markdown(f"- {item}")
