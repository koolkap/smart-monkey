from __future__ import annotations

from pathlib import Path

import streamlit as st
from weasyprint import HTML


def export_html_to_pdf(html: str, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    HTML(string=html).write_pdf(str(output_path))
    return output_path


def render_downloads(english_html: str, korean_html: str) -> None:
    st.subheader("Export")
    st.download_button("Download English HTML", english_html, file_name="resume_en.html")
    st.download_button("Download Korean HTML", korean_html, file_name="resume_ko.html")

    if st.button("Generate PDFs"):
        english_path = export_html_to_pdf(english_html, Path("data/exports/resume_en.pdf"))
        korean_path = export_html_to_pdf(korean_html, Path("data/exports/resume_ko.pdf"))
        st.success(f"PDFs generated: {english_path} and {korean_path}")
        st.download_button("Download English PDF", english_path.read_bytes(), file_name="resume_en.pdf")
        st.download_button("Download Korean PDF", korean_path.read_bytes(), file_name="resume_ko.pdf")
