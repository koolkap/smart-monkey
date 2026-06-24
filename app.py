from __future__ import annotations

import json
import logging
from pathlib import Path

import streamlit as st

from components.ats_engine import render_ats_report
from components.editor import render_profile_editor
from components.exporter import render_downloads
from components.insights_panel import render_ai_insights, render_design_intelligence
from components.uploader import render_uploaders
from providers.factory import build_provider
from templates.html_themes.theme_registry import THEMES
from utils.ats_scorer import score_resume
from utils.design_analyzer import analyze_design_reference
from utils.image_parser import enhance_headshot, image_to_data_uri
from utils.insights import build_ai_insights
from utils.models import AIInsights, DesignIntelligence, ProviderSettings, ResumeProfile
from utils.pdf_parser import build_requirement_profile, build_resume_profile, extract_text_from_uploads
from utils.resume_builder import generate_resume_html, reconstruct_profile
from utils.storage import load_settings, save_settings
from utils.translator import localize_resume

logging.basicConfig(level=logging.INFO)

ICON_PATH = Path(__file__).parent / "assets" / "smart-monkey-icon.svg"

st.set_page_config(page_title="Smart Monkey", page_icon=str(ICON_PATH), layout="wide")


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
    if "design_intelligence" not in st.session_state:
        st.session_state.design_intelligence = None
    if "ai_insights" not in st.session_state:
        st.session_state.ai_insights = None


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
        .step-grid {
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 0.75rem;
            margin-top: 1rem;
        }
        .step-card {
            background: rgba(255,255,255,0.72);
            border: 1px solid rgba(15,76,129,0.1);
            border-radius: 18px;
            padding: 0.85rem 1rem;
        }
        .step-card strong {
            display: block;
            color: #102a43;
            margin-bottom: 0.2rem;
        }
        </style>
        <section class='hero-shell'>
            <h1>Smart Monkey</h1>
            <p>ATS-optimized multilingual resume generation with provider-agnostic LLM orchestration, live editing, theme switching, and PDF export.</p>
            <div class='step-grid'>
                <div class='step-card'><strong>1. Configure</strong><span>Choose provider and credentials</span></div>
                <div class='step-card'><strong>2. Ingest</strong><span>Upload resume, JD, design, and photo</span></div>
                <div class='step-card'><strong>3. Optimize</strong><span>Generate ATS and AI insights</span></div>
                <div class='step-card'><strong>4. Export</strong><span>Edit, localize, and download</span></div>
            </div>
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
            settings.azure_api_version = st.text_input("API Version", value=settings.azure_api_version)
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
        st.caption("If a .env file is present, those values override the saved settings file.")
    return settings


def render_sidebar_navigation() -> None:
    with st.sidebar:
        st.divider()
        st.markdown("### Workflow")
        for item in [
            "Settings",
            "Resume Upload",
            "Job Description",
            "Design Reference",
            "ATS Report",
            "Resume Editor",
            "Export",
        ]:
            st.caption(f"- {item}")


def render_generation_status() -> tuple[st.delta_generator.DeltaGenerator, st.delta_generator.DeltaGenerator]:
    status = st.status("Ready to generate", expanded=True)
    progress = st.progress(0, text="Waiting for inputs")
    return status, progress


def main() -> None:
    init_state()
    render_branding()
    settings = render_settings()
    render_sidebar_navigation()
    status, progress = render_generation_status()

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        uploads = render_uploaders()
        theme_name = st.selectbox(
            "Theme",
            [
                "Modern ATS",
                "Executive",
                "Minimalist",
                "Consulting",
                "Startup",
                "Corporate Blue",
                "Korean Corporate",
                "Global Tech",
            ],
            index=0,
        )
        color_mode = st.segmented_control("Mode", ["Light", "Dark"], default="Light")
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
        render_design_intelligence(st.session_state.design_intelligence)

    if generate_clicked:
        status.update(label="Initializing provider and parsing inputs", state="running")
        progress.progress(10, text="Initializing provider")
        provider = None
        try:
            provider = build_provider(settings)
        except Exception as exc:
            st.warning(f"Provider initialization failed. Falling back to heuristic mode: {exc}")

        resume_text = extract_text_from_uploads(uploads["resume_files"] or [])
        jd_text = uploads["jd_text"] or ""
        if uploads["jd_files"]:
            jd_text = f"{jd_text}\n\n{extract_text_from_uploads(uploads['jd_files'])}".strip()
        progress.progress(30, text="Documents parsed")

        if not resume_text:
            st.error("Upload at least one resume or supporting PDF.")
            st.stop()
        if not jd_text:
            st.error("Provide a job description as text or PDF.")
            st.stop()

        design_intelligence: DesignIntelligence | None = None
        if uploads["design_reference"] is not None:
            design_intelligence = analyze_design_reference(
                uploads["design_reference"].name,
                uploads["design_reference"].getvalue(),
            )
        st.session_state.design_intelligence = design_intelligence

        status.update(label="Reconstructing candidate profile", state="running")
        progress.progress(50, text="Building candidate and requirement intelligence")
        base_profile = build_resume_profile(resume_text)
        requirements = build_requirement_profile(jd_text)
        profile = reconstruct_profile(base_profile, requirements, provider)
        ats_report = score_resume(profile, requirements)
        ai_insights: AIInsights = build_ai_insights(profile, requirements, ats_report)

        photo_data_uri = None
        if uploads["photo"] is not None:
            enhanced = enhance_headshot(uploads["photo"].getvalue())
            photo_data_uri = image_to_data_uri(enhanced)

        status.update(label="Generating multilingual resumes", state="running")
        progress.progress(75, text="Rendering HTML resumes")
        selected_theme = theme_name if color_mode == "Light" else "Global Tech"
        english_html = generate_resume_html(profile, selected_theme, photo_data_uri)
        localized_profile = localize_resume(profile, provider, "Korean") if provider else profile
        korean_html = generate_resume_html(localized_profile, "Korean Corporate", photo_data_uri)

        st.session_state.profile = profile
        st.session_state.localized_profile = localized_profile
        st.session_state.ats_report = ats_report
        st.session_state.ai_insights = ai_insights
        st.session_state.english_html = english_html
        st.session_state.korean_html = korean_html
        progress.progress(100, text="Resume package ready")
        status.update(label="Generation complete", state="complete")

    if st.session_state.ats_report:
        tabs = st.tabs([
            "ATS Report",
            "AI Insights",
            "Design Reference",
            "English Resume",
            "Korean Resume",
            "JSON Model",
            "Product Spec",
        ])
        with tabs[0]:
            render_ats_report(st.session_state.ats_report)
        with tabs[1]:
            render_ai_insights(st.session_state.ai_insights)
        with tabs[2]:
            render_design_intelligence(st.session_state.design_intelligence)
        with tabs[3]:
            st.session_state.profile = render_profile_editor(st.session_state.profile, "english")
            st.session_state.english_html = generate_resume_html(st.session_state.profile, theme_name)
            st.components.v1.html(st.session_state.english_html, height=900, scrolling=True)
        with tabs[4]:
            st.session_state.localized_profile = render_profile_editor(st.session_state.localized_profile, "korean")
            st.session_state.korean_html = generate_resume_html(st.session_state.localized_profile, "Korean Corporate")
            st.components.v1.html(st.session_state.korean_html, height=900, scrolling=True)
        with tabs[5]:
            payload = {
                "profile": st.session_state.profile.to_dict(),
                "localized_profile": st.session_state.localized_profile.to_dict(),
                "ats_report": st.session_state.ats_report.to_dict(),
                "design_intelligence": st.session_state.design_intelligence.to_dict() if st.session_state.design_intelligence else None,
                "ai_insights": st.session_state.ai_insights.to_dict() if st.session_state.ai_insights else None,
            }
            st.code(json.dumps(payload, ensure_ascii=False, indent=2), language="json")
        with tabs[6]:
            st.markdown(
                """
### UI Screens

1. Settings sidebar for provider selection and credentials.
2. Intake workspace for resume, JD, design reference, and photo uploads.
3. ATS dashboard with scorecards and gap analysis.
4. AI insights workspace for recruiter simulation and interview readiness.
5. Dual-language live editor with HTML preview.
6. Export center for HTML and PDF artifacts.

### Deployment

1. Install Python 3.11+ and system dependencies required by WeasyPrint.
2. Create a virtual environment and install dependencies from requirements.txt.
3. Run `streamlit run app.py` locally or deploy to Streamlit Community Cloud, Azure App Service, or a container platform.
4. Persist provider settings locally or inject them through environment variables for managed hosting.

### Additional AI Features

- Resume rewrite and achievement enhancement.
- Role match analysis and recruiter simulation.
- Interview readiness and promotion readiness analysis.
- Skill recommendation engine and application success prediction.
                """
            )
        render_downloads(st.session_state.english_html, st.session_state.korean_html)


if __name__ == "__main__":
    main()