from __future__ import annotations

import json
import logging

import streamlit as st

from components.ats_engine import render_ats_report
from components.editor import render_profile_editor
from components.exporter import render_downloads
from components.uploader import render_uploaders
from providers.factory import build_provider
from templates.html_themes.theme_registry import THEMES
from utils.ats_scorer import score_resume
from utils.image_parser import enhance_headshot, image_to_data_uri
from utils.models import ProviderSettings, ResumeProfile
from utils.pdf_parser import build_requirement_profile, build_resume_profile, extract_text_from_uploads
from utils.resume_builder import generate_resume_html, reconstruct_profile
from utils.storage import load_settings, save_settings
from utils.translator import localize_resume

logging.basicConfig(level=logging.INFO)

st.set_page_config(page_title="ResumeForge AI", page_icon="RF", layout="wide")


def init_state() -> None:
    if "settings" not in st.session_state:
        st.session_state.settings = load_settings()
    if "profile" not in st.session_state:
        st.session_state.profile = ResumeProfile()
    if "localized_profile" not in st.session_state:
        st.session_state.localized_profile = ResumeProfile()
    if "ats_report" not in st.session_state:
        st.session_state.ats_report = None
    if "english_html" not in st.session_state:
        st.session_state.english_html = ""
    if "korean_html" not in st.session_state:
        st.session_state.korean_html = ""


def render_branding() -> None:
    st.markdown(
        """
        <style>
        .hero-shell {
            padding: 1.5rem 1.75rem;
            border-radius: 24px;
            background: radial-gradient(circle at top left, rgba(15,76,129,0.18), transparent 35%),
                        linear-gradient(135deg, #f4f1ea 0%, #ffffff 55%, #e7e0d3 100%);
            border: 1px solid rgba(15,76,129,0.12);
            margin-bottom: 1rem;
        }
        .hero-shell h1 {
            font-family: Georgia, serif;
            font-size: 2.4rem;
            margin-bottom: 0.25rem;
            color: #102a43;
        }
        .hero-shell p {
            color: #486581;
            max-width: 60rem;
            margin: 0;
        }
        </style>
        <section class='hero-shell'>
            <h1>ResumeForge AI</h1>
            <p>ATS-optimized multilingual resume generation with provider-agnostic LLM orchestration, live editing, theme switching, and PDF export.</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_settings() -> ProviderSettings:
    settings: ProviderSettings = st.session_state.settings
    with st.sidebar:
        st.header("Settings")
        settings.provider = st.selectbox(
            "LLM Provider",
            ["Azure Foundry", "OpenAI Compatible", "Claude", "Gemini", "Ollama"],
            index=["Azure Foundry", "OpenAI Compatible", "Claude", "Gemini", "Ollama"].index(settings.provider.title())
            if settings.provider.title() in ["Azure Foundry", "OpenAI Compatible", "Claude", "Gemini", "Ollama"]
            else 4,
        )
        if settings.provider == "Azure Foundry":
            settings.azure_endpoint = st.text_input("Endpoint", value=settings.azure_endpoint)
            settings.azure_api_key = st.text_input("API Key", value=settings.azure_api_key, type="password")
            settings.azure_deployment = st.text_input("Deployment Name", value=settings.azure_deployment)
        elif settings.provider == "OpenAI Compatible":
            settings.openai_endpoint = st.text_input("Endpoint", value=settings.openai_endpoint)
            settings.openai_api_key = st.text_input("API Key", value=settings.openai_api_key, type="password")
            settings.openai_model = st.text_input("Model Name", value=settings.openai_model)
        elif settings.provider == "Claude":
            settings.anthropic_api_key = st.text_input("API Key", value=settings.anthropic_api_key, type="password")
            settings.anthropic_model = st.text_input("Model Name", value=settings.anthropic_model)
        elif settings.provider == "Gemini":
            settings.gemini_api_key = st.text_input("API Key", value=settings.gemini_api_key, type="password")
            settings.gemini_model = st.text_input("Model Name", value=settings.gemini_model)
        else:
            settings.ollama_url = st.text_input("Ollama URL", value=settings.ollama_url)
            settings.ollama_model = st.text_input("Model Name", value=settings.ollama_model)

        if st.button("Save Settings"):
            save_settings(settings)
            st.success("Settings saved locally.")
    return settings


def main() -> None:
    init_state()
    render_branding()
    settings = render_settings()

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        uploads = render_uploaders()
        theme_name = st.selectbox("Theme", list(THEMES.keys()), index=0)
        generate_clicked = st.button("Generate Resume Package", type="primary", use_container_width=True)

    with right:
        st.subheader("Architecture")
        st.markdown(
            """
```mermaid
flowchart TD
    A[Streamlit UI] --> B[Provider Factory]
    A --> C[PDF and Image Parsers]
    C --> D[Profile Reconstruction]
    B --> D
    D --> E[ATS Scoring Engine]
    D --> F[HTML Theme Renderer]
    D --> G[Localization Engine]
    F --> H[PDF Export]
```
            """
        )
        st.caption("Stateless orchestration with local settings persistence and session-scoped editing.")

    if generate_clicked:
        provider = None
        try:
            provider = build_provider(settings)
        except Exception as exc:
            st.warning(f"Provider initialization failed. Falling back to heuristic mode: {exc}")

        resume_text = extract_text_from_uploads(uploads["resume_files"] or [])
        jd_text = uploads["jd_text"] or ""
        if uploads["jd_files"]:
            jd_text = f"{jd_text}\n\n{extract_text_from_uploads(uploads['jd_files'])}".strip()

        if not resume_text:
            st.error("Upload at least one resume or supporting PDF.")
            st.stop()
        if not jd_text:
            st.error("Provide a job description as text or PDF.")
            st.stop()

        base_profile = build_resume_profile(resume_text)
        requirements = build_requirement_profile(jd_text)
        profile = reconstruct_profile(base_profile, requirements, provider)
        ats_report = score_resume(profile, requirements)

        photo_data_uri = None
        if uploads["photo"] is not None:
            enhanced = enhance_headshot(uploads["photo"].getvalue())
            photo_data_uri = image_to_data_uri(enhanced)

        english_html = generate_resume_html(profile, theme_name, photo_data_uri)
        localized_profile = localize_resume(profile, provider, "Korean") if provider else profile
        korean_html = generate_resume_html(localized_profile, "Korean Corporate", photo_data_uri)

        st.session_state.profile = profile
        st.session_state.localized_profile = localized_profile
        st.session_state.ats_report = ats_report
        st.session_state.english_html = english_html
        st.session_state.korean_html = korean_html

    if st.session_state.ats_report:
        tabs = st.tabs([
            "ATS Report",
            "English Resume",
            "Korean Resume",
            "JSON Model",
            "Product Spec",
        ])
        with tabs[0]:
            render_ats_report(st.session_state.ats_report)
        with tabs[1]:
            st.session_state.profile = render_profile_editor(st.session_state.profile, "english")
            st.session_state.english_html = generate_resume_html(st.session_state.profile, theme_name)
            st.components.v1.html(st.session_state.english_html, height=900, scrolling=True)
        with tabs[2]:
            st.session_state.localized_profile = render_profile_editor(st.session_state.localized_profile, "korean")
            st.session_state.korean_html = generate_resume_html(st.session_state.localized_profile, "Korean Corporate")
            st.components.v1.html(st.session_state.korean_html, height=900, scrolling=True)
        with tabs[3]:
            st.code(json.dumps(st.session_state.profile.to_dict(), ensure_ascii=False, indent=2), language="json")
        with tabs[4]:
            st.markdown(
                """
### UI Screens

1. Settings sidebar for provider selection and credentials.
2. Intake workspace for resume, JD, design reference, and photo uploads.
3. ATS dashboard with scorecards and gap analysis.
4. Dual-language live editor with HTML preview.
5. Export center for HTML and PDF artifacts.

### Deployment

1. Install Python 3.11+ and system dependencies required by WeasyPrint.
2. Create a virtual environment and install dependencies from requirements.txt.
3. Run `streamlit run app.py` locally or deploy to Streamlit Community Cloud, Azure App Service, or a container platform.
4. Persist provider settings locally or inject them through environment variables for managed hosting.
                """
            )
        render_downloads(st.session_state.english_html, st.session_state.korean_html)


if __name__ == "__main__":
    main()