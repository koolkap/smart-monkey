from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from utils.models import ResumeProfile

try:
    from weasyprint import HTML
except Exception:
    HTML = None


def export_html_to_pdf(html: str, output_path: Path) -> Path:
    if HTML is None:
        raise RuntimeError(
            "PDF export is unavailable because WeasyPrint native libraries are not installed on this machine."
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(str(output_path))
    return output_path


def render_downloads(english_html: str, korean_html: str, profile: ResumeProfile) -> None:
    st.subheader("Export")
    st.download_button("Download English HTML", english_html, file_name="resume_en.html")
    st.download_button("Download Korean HTML", korean_html, file_name="resume_ko.html")
    st.download_button("Download HTML", english_html, file_name="resume.html")
    st.download_button(
        "Download JSON",
        json.dumps(profile.to_dict(), indent=2),
        file_name="resume.json",
        mime="application/json",
    )

    if HTML is None:
        st.warning(
            "PDF export is disabled on this machine because WeasyPrint system libraries are missing. "
            "HTML export remains available."
        )
        return

    if st.button("Generate PDFs"):
        english_path = export_html_to_pdf(english_html, Path("data/exports/resume_en.pdf"))
        korean_path = export_html_to_pdf(korean_html, Path("data/exports/resume_ko.pdf"))
        st.success(f"PDFs generated: {english_path} and {korean_path}")
        st.download_button("Download English PDF", english_path.read_bytes(), file_name="resume_en.pdf")
        st.download_button("Download Korean PDF", korean_path.read_bytes(), file_name="resume_ko.pdf")
        st.caption("PDFs are generated from HTML, which remains the source of truth.")
