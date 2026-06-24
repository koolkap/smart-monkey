from __future__ import annotations

import streamlit as st

from utils.models import ResumeProfile


def render_profile_editor(profile: ResumeProfile, key_prefix: str = "editor") -> ResumeProfile:
    st.subheader("Live Resume Editor")
    profile.name = st.text_input("Name", value=profile.name, key=f"{key_prefix}_name")
    profile.headline = st.text_input("Headline", value=profile.headline, key=f"{key_prefix}_headline")
    profile.summary = st.text_area("Summary", value=profile.summary, height=180, key=f"{key_prefix}_summary")

    skills_text = st.text_area(
        "Skills (comma separated)",
        value=", ".join(profile.skills),
        height=100,
        key=f"{key_prefix}_skills",
    )
    profile.skills = [skill.strip() for skill in skills_text.split(",") if skill.strip()]

    soft_skills_text = st.text_input(
        "Soft Skills",
        value=", ".join(profile.soft_skills),
        key=f"{key_prefix}_soft_skills",
    )
    profile.soft_skills = [skill.strip() for skill in soft_skills_text.split(",") if skill.strip()]

    achievements_text = st.text_area(
        "Achievement Highlights",
        value="\n".join(profile.achievements_summary),
        height=120,
        key=f"{key_prefix}_achievements",
    )
    profile.achievements_summary = [line.strip() for line in achievements_text.splitlines() if line.strip()]
    return profile
