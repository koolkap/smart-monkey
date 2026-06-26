from __future__ import annotations

import streamlit as st

from utils.models import CertificationItem, EducationItem, ExperienceItem, ProjectItem, ResumeProfile


def _split_lines(value: str) -> list[str]:
    return [line.strip() for line in value.splitlines() if line.strip()]


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _render_contact_editor(profile: ResumeProfile, key_prefix: str) -> None:
    st.markdown("#### Contact")
    col_left, col_right = st.columns(2)
    with col_left:
        profile.contact.email = st.text_input("Email", value=profile.contact.email, key=f"{key_prefix}_contact_email")
        profile.contact.phone = st.text_input("Phone", value=profile.contact.phone, key=f"{key_prefix}_contact_phone")
        profile.contact.location = st.text_input(
            "Location", value=profile.contact.location, key=f"{key_prefix}_contact_location"
        )
    with col_right:
        profile.contact.linkedin = st.text_input(
            "LinkedIn", value=profile.contact.linkedin, key=f"{key_prefix}_contact_linkedin"
        )
        profile.contact.github = st.text_input("GitHub", value=profile.contact.github, key=f"{key_prefix}_contact_github")
        profile.contact.website = st.text_input(
            "Website", value=profile.contact.website, key=f"{key_prefix}_contact_website"
        )


def _render_experience_editor(profile: ResumeProfile, key_prefix: str) -> None:
    st.markdown("#### Experience")
    remove_index = None
    add_item = False
    for index, item in enumerate(profile.experience):
        with st.expander(f"Experience {index + 1}: {item.title or 'Untitled role'}", expanded=index == 0):
            top_left, top_right = st.columns([0.82, 0.18])
            with top_left:
                item.title = st.text_input("Title", value=item.title, key=f"{key_prefix}_exp_title_{index}")
            with top_right:
                if st.button("Delete", key=f"{key_prefix}_exp_delete_{index}", use_container_width=True):
                    remove_index = index
            item.company = st.text_input("Company", value=item.company, key=f"{key_prefix}_exp_company_{index}")
            item.location = st.text_input("Location", value=item.location, key=f"{key_prefix}_exp_location_{index}")
            date_left, date_right = st.columns(2)
            with date_left:
                item.start_date = st.text_input(
                    "Start date", value=item.start_date, key=f"{key_prefix}_exp_start_{index}"
                )
            with date_right:
                item.end_date = st.text_input("End date", value=item.end_date, key=f"{key_prefix}_exp_end_{index}")
            achievements = st.text_area(
                "Achievements, one per line",
                value="\n".join(item.achievements),
                height=140,
                key=f"{key_prefix}_exp_achievements_{index}",
            )
            item.achievements = _split_lines(achievements)
    if st.button("Add experience", key=f"{key_prefix}_exp_add", use_container_width=True):
        add_item = True
    if remove_index is not None:
        profile.experience.pop(remove_index)
    elif add_item:
        profile.experience.append(ExperienceItem())


def _render_education_editor(profile: ResumeProfile, key_prefix: str) -> None:
    st.markdown("#### Education")
    remove_index = None
    add_item = False
    for index, item in enumerate(profile.education):
        with st.expander(f"Education {index + 1}: {item.institution or 'Untitled education'}", expanded=False):
            top_left, top_right = st.columns([0.82, 0.18])
            with top_left:
                item.institution = st.text_input(
                    "Institution", value=item.institution, key=f"{key_prefix}_edu_institution_{index}"
                )
            with top_right:
                if st.button("Delete", key=f"{key_prefix}_edu_delete_{index}", use_container_width=True):
                    remove_index = index
            item.degree = st.text_input("Degree", value=item.degree, key=f"{key_prefix}_edu_degree_{index}")
            item.field_of_study = st.text_input(
                "Field of study", value=item.field_of_study, key=f"{key_prefix}_edu_field_{index}"
            )
            date_left, date_right = st.columns(2)
            with date_left:
                item.start_date = st.text_input(
                    "Start date", value=item.start_date, key=f"{key_prefix}_edu_start_{index}"
                )
            with date_right:
                item.end_date = st.text_input("End date", value=item.end_date, key=f"{key_prefix}_edu_end_{index}")
    if st.button("Add education", key=f"{key_prefix}_edu_add", use_container_width=True):
        add_item = True
    if remove_index is not None:
        profile.education.pop(remove_index)
    elif add_item:
        profile.education.append(EducationItem())


def _render_projects_editor(profile: ResumeProfile, key_prefix: str) -> None:
    st.markdown("#### Projects")
    remove_index = None
    add_item = False
    for index, item in enumerate(profile.projects):
        with st.expander(f"Project {index + 1}: {item.name or 'Untitled project'}", expanded=False):
            top_left, top_right = st.columns([0.82, 0.18])
            with top_left:
                item.name = st.text_input("Project name", value=item.name, key=f"{key_prefix}_project_name_{index}")
            with top_right:
                if st.button("Delete", key=f"{key_prefix}_project_delete_{index}", use_container_width=True):
                    remove_index = index
            item.description = st.text_area(
                "Description", value=item.description, height=120, key=f"{key_prefix}_project_description_{index}"
            )
            technologies = st.text_input(
                "Technologies",
                value=", ".join(item.technologies),
                key=f"{key_prefix}_project_tech_{index}",
            )
            item.technologies = _split_csv(technologies)
            item.link = st.text_input("Link", value=item.link, key=f"{key_prefix}_project_link_{index}")
    if st.button("Add project", key=f"{key_prefix}_project_add", use_container_width=True):
        add_item = True
    if remove_index is not None:
        profile.projects.pop(remove_index)
    elif add_item:
        profile.projects.append(ProjectItem())


def _render_certifications_editor(profile: ResumeProfile, key_prefix: str) -> None:
    st.markdown("#### Certifications")
    remove_index = None
    add_item = False
    for index, item in enumerate(profile.certifications):
        with st.expander(f"Certification {index + 1}: {item.name or 'Untitled certification'}", expanded=False):
            top_left, top_right = st.columns([0.82, 0.18])
            with top_left:
                item.name = st.text_input("Name", value=item.name, key=f"{key_prefix}_cert_name_{index}")
            with top_right:
                if st.button("Delete", key=f"{key_prefix}_cert_delete_{index}", use_container_width=True):
                    remove_index = index
            item.issuer = st.text_input("Issuer", value=item.issuer, key=f"{key_prefix}_cert_issuer_{index}")
            item.year = st.text_input("Year", value=item.year, key=f"{key_prefix}_cert_year_{index}")
    if st.button("Add certification", key=f"{key_prefix}_cert_add", use_container_width=True):
        add_item = True
    if remove_index is not None:
        profile.certifications.pop(remove_index)
    elif add_item:
        profile.certifications.append(CertificationItem())


def render_profile_editor(profile: ResumeProfile, key_prefix: str = "editor") -> ResumeProfile:
    st.subheader("Live Resume Editor")
    st.caption("Edit verified content section by section. Add or remove entries before final export.")

    profile.name = st.text_input("Name", value=profile.name, key=f"{key_prefix}_name")
    profile.headline = st.text_input("Headline", value=profile.headline, key=f"{key_prefix}_headline")
    profile.summary = st.text_area("Summary", value=profile.summary, height=180, key=f"{key_prefix}_summary")

    _render_contact_editor(profile, key_prefix)

    skills_text = st.text_area(
        "Skills (comma separated)",
        value=", ".join(profile.skills),
        height=100,
        key=f"{key_prefix}_skills",
    )
    profile.skills = _split_csv(skills_text)

    soft_skills_text = st.text_input(
        "Soft Skills",
        value=", ".join(profile.soft_skills),
        key=f"{key_prefix}_soft_skills",
    )
    profile.soft_skills = _split_csv(soft_skills_text)

    achievements_text = st.text_area(
        "Achievement Highlights",
        value="\n".join(profile.achievements_summary),
        height=120,
        key=f"{key_prefix}_achievements",
    )
    profile.achievements_summary = _split_lines(achievements_text)

    _render_experience_editor(profile, key_prefix)
    _render_education_editor(profile, key_prefix)
    _render_projects_editor(profile, key_prefix)
    _render_certifications_editor(profile, key_prefix)
    return profile
