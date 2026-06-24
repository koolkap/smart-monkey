from __future__ import annotations

import streamlit as st

from utils.models import ATSReport


def render_ats_report(report: ATSReport) -> None:
    st.subheader("ATS Optimization Report")
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("ATS Score", f"{report.ats_score}%")
    col2.metric("Match", f"{report.match_percentage}%")
    col3.metric("Recruiter Visibility", f"{report.recruiter_visibility_score}%")
    col4.metric("Skill Match", f"{report.skill_match_percentage}%")
    col5.metric("Industry Relevance", f"{report.industry_relevance_score}%")

    st.progress(report.ats_score / 100, text=f"Expected screening result: {report.expected_screening_result}")

    st.write("**Missing Skills**")
    st.write(report.missing_skills or ["No major gaps detected"])
    st.write("**Missing Keywords**")
    st.write(report.missing_keywords or ["No major keyword gaps detected"])
    st.write("**Strength Areas**")
    st.write(report.strength_areas or ["Add more role-specific evidence"])
    st.write("**Resume Strengths**")
    st.write(report.resume_strengths or ["Add stronger quantified achievements"])
    st.write("**Resume Weaknesses**")
    st.write(report.resume_weaknesses or ["No major weaknesses detected"])
    st.write("**Suggested Improvements**")
    st.write(report.suggested_improvements)
    st.write("**Gap Analysis**")
    st.write(report.gap_analysis)
    st.write("**Role Fit Analysis**")
    st.info(report.role_fit_analysis)
    st.write("**Scoring Explanations**")
    st.write(report.scoring_explanations)
    st.caption(f"Keyword density: {report.keyword_density:.2f}")
