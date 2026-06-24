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
from utils.ats_scorer import score_resume
from utils.design_analyzer import analyze_design_reference
from utils.image_parser import enhance_headshot, image_to_data_uri
from utils.insights import build_ai_insights
from utils.models import ProviderSettings, ResumeProfile, WorkflowArtifacts
from utils.pdf_parser import build_requirement_profile, build_resume_profile, extract_text_from_uploads
from utils.resume_builder import generate_resume_html, reconstruct_profile
from utils.storage import load_settings, save_settings
from utils.translator import localize_resume

logging.basicConfig(level=logging.INFO)

ICON_PATH = Path(__file__).parent / "assets" / "smart-monkey-icon.svg"
ROUTES = ["/upload", "/analysis", "/editor", "/export"]
VARIANT_THEME_MAP = {
    "ATS Optimized": "Modern ATS",
    "Korean Resume": "Korean Corporate",
    "Executive Resume": "Executive",
    "Consulting Resume": "Consulting",
    "Startup Resume": "Startup",
}

st.set_page_config(page_title="Smart Monkey", page_icon=str(ICON_PATH), layout="wide")


def inject_global_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at 18% 18%, rgba(170, 232, 214, 0.55), transparent 28%),
                radial-gradient(circle at 62% 34%, rgba(198, 232, 255, 0.45), transparent 24%),
                radial-gradient(circle at 78% 52%, rgba(214, 198, 255, 0.32), transparent 22%),
                linear-gradient(180deg, #f7f8fb 0%, #eef3f2 100%);
        }
        [data-testid="stSidebar"] {
            background: rgba(255, 255, 255, 0.72);
            border-right: 1px solid rgba(31, 41, 55, 0.08);
            backdrop-filter: blur(18px);
        }
        [data-testid="stSidebar"] .stRadio > div {
            gap: 0.35rem;
        }
        .topbar {
            display: flex;
            justify-content: flex-end;
            align-items: center;
            margin-bottom: 0.75rem;
        }
        .hero-shell {
            padding: 2.25rem 2.4rem;
            border-radius: 32px;
            background: linear-gradient(135deg, rgba(255,255,255,0.88) 0%, rgba(247,250,252,0.92) 100%);
            border: 1px solid rgba(148, 163, 184, 0.22);
            box-shadow: 0 24px 60px rgba(15, 23, 42, 0.08);
            margin-bottom: 1.5rem;
        }
        .hero-kicker {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #4f46e5;
            margin-bottom: 0.9rem;
        }
        .hero-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.1fr) minmax(320px, 0.9fr);
            gap: 1.5rem;
            align-items: center;
        }
        .hero-copy h1 {
            font-family: Georgia, serif;
            font-size: 4rem;
            line-height: 1.02;
            letter-spacing: -0.04em;
            margin: 0 0 1rem 0;
            color: #1f2937;
            max-width: 10ch;
        }
        .hero-copy p {
            color: #4b5563;
            font-size: 1.08rem;
            line-height: 1.75;
            max-width: 42rem;
            margin: 0 0 1.4rem 0;
        }
        .hero-upload {
            display: inline-flex;
            align-items: center;
            gap: 0.75rem;
            padding: 0.95rem 1.15rem;
            border: 1px dashed rgba(16, 185, 129, 0.45);
            border-radius: 20px;
            background: rgba(255,255,255,0.72);
            color: #374151;
            font-size: 0.95rem;
        }
        .hero-preview {
            min-height: 320px;
            border-radius: 28px;
            padding: 1rem;
            background: linear-gradient(180deg, rgba(244, 241, 255, 0.95), rgba(232, 240, 255, 0.88));
            box-shadow: inset 0 1px 0 rgba(255,255,255,0.7);
        }
        .preview-window {
            height: 100%;
            min-height: 288px;
            border-radius: 22px;
            background: rgba(255,255,255,0.92);
            padding: 1rem;
            display: grid;
            grid-template-columns: 120px 1fr;
            gap: 1rem;
        }
        .preview-score {
            border-radius: 18px;
            background: #f8fafc;
            padding: 0.9rem;
        }
        .preview-score .ring {
            width: 72px;
            height: 72px;
            border-radius: 50%;
            margin: 0.5rem auto;
            border: 8px solid #d1fae5;
            border-top-color: #10b981;
        }
        .preview-panel {
            border-radius: 18px;
            background: #eef2ff;
            padding: 1rem;
        }
        .preview-line {
            height: 10px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.35);
            margin-bottom: 0.65rem;
        }
        .preview-line.short {
            width: 58%;
        }
        .preview-line.medium {
            width: 76%;
        }
        .preview-meter {
            height: 12px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.35);
            overflow: hidden;
            margin: 1rem 0;
        }
        .preview-meter span {
            display: block;
            width: 78%;
            height: 100%;
            background: linear-gradient(90deg, #34d399, #10b981);
        }
        @media (max-width: 980px) {
            .hero-grid {
                grid-template-columns: 1fr;
            }
            .hero-copy h1 {
                font-size: 2.8rem;
                max-width: none;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def init_state() -> None:
    if "settings" not in st.session_state:
        st.session_state.settings = load_settings()
    if "workflow" not in st.session_state:
        st.session_state.workflow = WorkflowArtifacts()
    if "uploads" not in st.session_state:
        st.session_state.uploads = {
            "resume_files": [],
            "jd_text": "",
            "jd_files": [],
            "design_reference": None,
            "photo": None,
        }


def render_branding() -> None:
    st.markdown(
        """
        <section class='hero-shell'>
            <div class='hero-kicker'>Resume Checker</div>
            <div class='hero-grid'>
                <div class='hero-copy'>
                    <h1>Is your resume good enough?</h1>
                    <p>Smart Monkey checks ATS compatibility, rebuilds your profile, and turns raw resume inputs into polished, editable resume variants with a cleaner workflow for analysis, editing, and export.</p>
                    <div class='hero-upload'>
                        <strong>Upload your resume</strong>
                        <span>PDF and DOCX only. Add job requirements, design references, and profile assets in one flow.</span>
                    </div>
                </div>
                <div class='hero-preview'>
                    <div class='preview-window'>
                        <div class='preview-score'>
                            <div style='font-size:0.8rem;color:#6b7280;'>Resume Score</div>
                            <div class='ring'></div>
                            <div style='text-align:center;font-weight:700;color:#10b981;'>92/100</div>
                        </div>
                        <div class='preview-panel'>
                            <div style='font-size:0.85rem;font-weight:700;color:#4f46e5;margin-bottom:0.8rem;'>CONTENT</div>
                            <div class='preview-line'></div>
                            <div class='preview-line medium'></div>
                            <div class='preview-line short'></div>
                            <div class='preview-meter'><span></span></div>
                            <div class='preview-line'></div>
                            <div class='preview-line medium'></div>
                            <div class='preview-line short'></div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_settings_form(settings: ProviderSettings) -> None:
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


@st.dialog("Settings", width="large")
def open_settings_dialog() -> None:
    settings: ProviderSettings = st.session_state.settings
    st.caption("Provider credentials are stored locally. If a .env file is present, those values override the saved settings file.")
    render_settings_form(settings)
    action_left, action_right = st.columns([0.7, 0.3])
    with action_left:
        if st.button("Save Settings", type="primary", use_container_width=True):
            save_settings(settings)
            st.session_state.settings = settings
            st.rerun()
    with action_right:
        st.button("Close", use_container_width=True)


def render_settings_trigger() -> ProviderSettings:
    settings: ProviderSettings = st.session_state.settings
    topbar_left, topbar_right = st.columns([0.88, 0.12])
    with topbar_right:
        if st.button("⚙ Settings", use_container_width=True):
            open_settings_dialog()
    return settings


def render_sidebar_navigation() -> str:
    workflow: WorkflowArtifacts = st.session_state.workflow
    with st.sidebar:
        st.markdown("## Smart Monkey")
        st.caption("Workflow navigation")
        selected_route = st.radio(
            "Navigate",
            ROUTES,
            index=ROUTES.index(workflow.selected_route) if workflow.selected_route in ROUTES else 0,
            label_visibility="collapsed",
        )
        workflow.selected_route = selected_route
        st.caption("Independent pages: upload, analysis, editor, export")
    return selected_route


def render_upload_page() -> None:
    workflow: WorkflowArtifacts = st.session_state.workflow
    st.title("Stage 1 and 2: Resume and Job Requirement Input")
    st.caption("Upload resumes, portfolios, projects, certifications, and job requirements before analysis.")

    uploads = render_uploaders()
    st.session_state.uploads = uploads

    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        st.markdown("### Candidate Profile Sources")
        st.markdown("- Resume PDF or DOCX")
        st.markdown("- Multiple resume PDFs")
        st.markdown("- Portfolio PDFs")
        st.markdown("- Project PDFs")
        st.markdown("- Certification PDFs")
    with right:
        st.markdown("### Requirement Profile Sources")
        st.markdown("- Paste job description")
        st.markdown("- Upload JD PDF")
        st.markdown("- Upload multiple requirement PDFs")

    if st.button("Analyze My Resume", type="primary", use_container_width=True):
        analyze_current_resume()
        workflow.selected_route = "/analysis"
        st.rerun()


def analyze_current_resume() -> None:
    workflow: WorkflowArtifacts = st.session_state.workflow
    settings: ProviderSettings = st.session_state.settings
    uploads = st.session_state.uploads

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
        st.error("Upload at least one resume, portfolio, project, or certification file.")
        return
    if not jd_text:
        st.error("Provide a job description as text or upload requirement files.")
        return

    workflow.base_profile = build_resume_profile(resume_text)
    workflow.requirements = build_requirement_profile(jd_text)
    workflow.ats_report = score_resume(workflow.base_profile, workflow.requirements)
    workflow.ai_insights = build_ai_insights(workflow.base_profile, workflow.requirements, workflow.ats_report)

    if uploads["design_reference"] is not None:
        workflow.design_intelligence = analyze_design_reference(
            uploads["design_reference"].name,
            uploads["design_reference"].getvalue(),
        )

    workflow.optimized_profile = ResumeProfile()
    workflow.localized_profile = ResumeProfile()
    workflow.english_html = ""
    workflow.korean_html = ""


def render_analysis_page() -> None:
    workflow: WorkflowArtifacts = st.session_state.workflow
    st.title("Current Resume Analysis")
    if not workflow.ats_report:
        st.info("Run analysis from /upload first.")
        return

    profile = workflow.base_profile
    requirements = workflow.requirements

    overview_left, overview_right = st.columns([1.1, 0.9], gap="large")
    with overview_left:
        st.markdown("### Profile Overview")
        st.markdown(f"**Name:** {profile.name or 'Unknown'}")
        st.markdown(f"**Contact:** {profile.contact.email or 'N/A'} | {profile.contact.phone or 'N/A'}")
        st.markdown(f"**LinkedIn:** {profile.contact.linkedin or 'N/A'}")
        st.markdown(f"**GitHub:** {profile.contact.github or 'N/A'}")
        st.markdown(f"**Years of Experience:** {workflow.ats_report.years_of_experience}")
        st.markdown(f"**Target Role:** {requirements.title or 'Not detected'}")
        st.markdown(f"**Current Skills:** {', '.join(profile.skills[:12]) or 'N/A'}")
    with overview_right:
        st.markdown("### Education, Certifications, Projects")
        st.markdown(f"**Education:** {', '.join(item.institution or item.degree for item in profile.education) or 'N/A'}")
        st.markdown(f"**Certifications:** {', '.join(item.name for item in profile.certifications) or 'N/A'}")
        st.markdown(f"**Projects:** {', '.join(item.name for item in profile.projects) or 'N/A'}")
        render_design_intelligence(workflow.design_intelligence)

    render_ats_report(workflow.ats_report)
    render_ai_insights(workflow.ai_insights)

    st.markdown("### Generate Optimized Resume Variants")
    action_cols = st.columns(5)
    actions = [
        ("Generate ATS Optimized Resume", "ATS Optimized"),
        ("Generate Korean Resume", "Korean Resume"),
        ("Generate Executive Resume", "Executive Resume"),
        ("Generate Consulting Resume", "Consulting Resume"),
        ("Generate Startup Resume", "Startup Resume"),
    ]
    for index, (label, variant) in enumerate(actions):
        if action_cols[index].button(label, use_container_width=True):
            generate_resume_variant(variant)
            workflow.selected_route = "/editor"
            st.rerun()


def generate_resume_variant(variant: str) -> None:
    workflow: WorkflowArtifacts = st.session_state.workflow
    settings: ProviderSettings = st.session_state.settings
    uploads = st.session_state.uploads

    provider = None
    try:
        provider = build_provider(settings)
    except Exception as exc:
        st.warning(f"Provider initialization failed. Falling back to heuristic mode: {exc}")

    workflow.selected_variant = variant
    workflow.selected_theme = VARIANT_THEME_MAP.get(variant, "Modern ATS")
    workflow.optimized_profile = reconstruct_profile(workflow.base_profile, workflow.requirements, provider)

    photo_data_uri = None
    if uploads["photo"] is not None:
        enhanced = enhance_headshot(uploads["photo"].getvalue())
        photo_data_uri = image_to_data_uri(enhanced)

    workflow.english_html = generate_resume_html(workflow.optimized_profile, workflow.selected_theme, photo_data_uri)
    workflow.localized_profile = localize_resume(workflow.optimized_profile, provider, "Korean") if provider else workflow.optimized_profile
    workflow.korean_html = generate_resume_html(workflow.localized_profile, "Korean Corporate", photo_data_uri)


def render_editor_page() -> None:
    workflow: WorkflowArtifacts = st.session_state.workflow
    st.title("Stage 5: Canva-Style Resume Editor")
    if not workflow.english_html:
        st.info("Generate a resume variant from /analysis first.")
        return

    toolbar_left, toolbar_right = st.columns([1.2, 0.8], gap="large")
    with toolbar_left:
        workflow.active_language = st.segmented_control(
            "Language",
            ["English", "Korean"],
            default=workflow.active_language,
        )
    with toolbar_right:
        workflow.selected_theme = st.selectbox(
            "Theme",
            ["Modern ATS", "Executive", "Minimalist", "Consulting", "Startup", "Corporate Blue", "Korean Corporate", "Global Tech"],
            index=["Modern ATS", "Executive", "Minimalist", "Consulting", "Startup", "Corporate Blue", "Korean Corporate", "Global Tech"].index(workflow.selected_theme)
            if workflow.selected_theme in ["Modern ATS", "Executive", "Minimalist", "Consulting", "Startup", "Corporate Blue", "Korean Corporate", "Global Tech"]
            else 0,
        )

    left, center, right = st.columns([0.9, 1.4, 0.9], gap="large")
    with left:
        st.markdown("### Left Panel")
        for section in [
            "Summary",
            "Experience",
            "Skills",
            "Projects",
            "Education",
            "Certifications",
            "Awards",
            "Languages",
            "Custom Sections",
        ]:
            st.markdown(f"- {section}")
        st.markdown("### AI Action Panel")
        for action in [
            "Improve Summary",
            "Improve Experience",
            "Improve Skills",
            "Make More Executive",
            "Make More Technical",
            "Make More ATS Friendly",
            "Make More Korean Corporate Style",
            "Make More Global Style",
            "Shorten Content",
            "Expand Content",
            "Rewrite Section",
        ]:
            st.button(action, key=f"ai_action_{action}", use_container_width=True)

    with center:
        st.markdown("### Center Panel")
        st.caption("Live resume canvas, A4 preview, zoom controls, and page navigation")
        zoom = st.slider("Zoom", min_value=60, max_value=140, value=100, step=10)
        active_profile = workflow.optimized_profile if workflow.active_language == "English" else workflow.localized_profile
        edited_profile = render_profile_editor(active_profile, workflow.active_language.lower())
        if workflow.active_language == "English":
            workflow.optimized_profile = edited_profile
            workflow.english_html = generate_resume_html(workflow.optimized_profile, workflow.selected_theme)
            st.components.v1.html(workflow.english_html, height=int(900 * zoom / 100), scrolling=True)
        else:
            workflow.localized_profile = edited_profile
            workflow.korean_html = generate_resume_html(workflow.localized_profile, "Korean Corporate")
            st.components.v1.html(workflow.korean_html, height=int(900 * zoom / 100), scrolling=True)

    with right:
        st.markdown("### Right Panel")
        st.markdown("- Fonts")
        st.markdown("- Colors")
        st.markdown("- Spacing")
        st.markdown("- Margins")
        st.markdown("- Theme")
        st.markdown("- Layout")
        st.markdown("- Photo Controls")
        st.markdown("- Section Visibility")
        if workflow.ats_report:
            live_report = score_resume(workflow.optimized_profile, workflow.requirements)
            st.markdown("### ATS Live Score")
            st.metric("Current ATS Score", f"{live_report.ats_score}%")
            st.metric("Keyword Match", f"{live_report.match_percentage}%")
            st.markdown("**Missing Skills**")
            for item in live_report.missing_skills[:6] or ["No major gaps"]:
                st.markdown(f"- {item}")
            st.markdown("**Improvement Suggestions**")
            for item in live_report.suggested_improvements[:5]:
                st.markdown(f"- {item}")

    if st.button("Continue to Export", type="primary", use_container_width=True):
        workflow.selected_route = "/export"
        st.rerun()


def render_export_page() -> None:
    workflow: WorkflowArtifacts = st.session_state.workflow
    st.title("Stage 6: Export")
    if not workflow.english_html:
        st.info("Generate and review a resume in /editor before exporting.")
        return

    render_downloads(workflow.english_html, workflow.korean_html, workflow.generated_profile)
    st.markdown("### JSON Export")
    st.code(json.dumps(workflow.to_dict(), ensure_ascii=False, indent=2), language="json")


def main() -> None:
    init_state()
    inject_global_styles()
    render_settings_trigger()
    render_branding()
    route = render_sidebar_navigation()

    if route == "/upload":
        render_upload_page()
    elif route == "/analysis":
        render_analysis_page()
    elif route == "/editor":
        render_editor_page()
    else:
        render_export_page()


if __name__ == "__main__":
    main()