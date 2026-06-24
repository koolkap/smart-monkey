from __future__ import annotations

import streamlit as st

from utils.models import AIInsights, DesignIntelligence


def render_design_intelligence(design: DesignIntelligence | None) -> None:
    st.subheader("Design Intelligence")
    if design is None:
        st.info("Upload a reference design to analyze layout, typography, and color direction.")
        return
    col1, col2, col3 = st.columns(3)
    col1.metric("Layout", design.layout_style)
    col2.metric("Typography", design.typography)
    col3.metric("Sidebar", design.sidebar_structure)
    st.write("**Font Hierarchy**")
    st.write(design.font_hierarchy)
    st.write("**Section Arrangement**")
    st.write(design.section_arrangement)
    st.write("**Color Palette**")
    st.write(design.color_palette)


def render_ai_insights(insights: AIInsights | None) -> None:
    st.subheader("AI Insights")
    if insights is None:
        st.info("Generate a resume package to unlock role match, recruiter simulation, and interview readiness insights.")
        return
    col1, col2, col3 = st.columns(3)
    col1.metric("Resume Quality", f"{insights.resume_quality_score}%")
    col2.metric("Application Success", f"{insights.application_success_prediction}%")
    col3.metric("Interview Readiness", f"{insights.interview_readiness.readiness_score}%")
    st.write("**Role Match Analysis**")
    st.write(insights.role_match_analysis)
    st.write("**Skill Recommendations**")
    st.write(insights.skill_recommendations)
    st.write("**Recruiter Simulation**")
    st.write(insights.recruiter_simulation.first_impression)
    st.write(insights.recruiter_simulation.recruiter_feedback)
    st.write("**Likely Interview Questions**")
    st.write(insights.interview_readiness.likely_questions)
    st.write("**Talking Points**")
    st.write(insights.interview_readiness.talking_points)
    st.write("**Risk Areas**")
    st.write(insights.interview_readiness.risk_areas)
    st.write("**Promotion Readiness**")
    st.write(insights.promotion_readiness_analysis)