from __future__ import annotations

import streamlit as st


def render_uploaders() -> dict[str, object]:
    st.subheader("Source Inputs")
    resume_files = st.file_uploader(
        "Upload current resume, portfolio, projects, or certificates",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key="resume_files",
    )
    jd_text = st.text_area("Paste job description", height=220, key="jd_text")
    jd_files = st.file_uploader(
        "Or upload job description PDFs",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key="jd_files",
    )
    design_reference = st.file_uploader(
        "Upload design reference (PDF, PNG, JPG)",
        type=["pdf", "png", "jpg", "jpeg"],
        accept_multiple_files=False,
        key="design_reference",
    )
    photo = st.file_uploader(
        "Upload optional profile photo",
        type=["png", "jpg", "jpeg"],
        accept_multiple_files=False,
        key="photo",
    )
    return {
        "resume_files": resume_files,
        "jd_text": jd_text,
        "jd_files": jd_files,
        "design_reference": design_reference,
        "photo": photo,
    }
