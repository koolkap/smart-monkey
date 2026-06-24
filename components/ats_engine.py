from __future__ import annotations

import streamlit as st

from utils.models import ATSReport


def render_ats_report(report: ATSReport) -> None:
    st.subheader("ATS Optimization Report")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ATS Score", f"{report.ats_score}%")
    col2.metric("Match", f"{report.match_percentage}%")
    col3.metric("Recruiter Visibility", f"{report.recruiter_visibility_score}%")
    col4.metric("Keyword Density", f"{report.keyword_density:.2f}")

    st.write("**Missing Skills**")
    st.write(report.missing_skills or ["No major gaps detected"])
    st.write("**Strength Areas**")
    st.write(report.strength_areas or ["Add more role-specific evidence"])
    st.write("**Suggested Improvements**")
    st.write(report.suggested_improvements)
    st.write("**Gap Analysis**")
    st.write(report.gap_analysis)
    st.write("**Role Fit Analysis**")
    st.info(report.role_fit_analysis)
