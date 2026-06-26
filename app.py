from __future__ import annotations

import logging
from pathlib import Path

import streamlit as st

from components.editor import render_profile_editor
from components.exporter import render_downloads
from providers.factory import build_provider
from templates.html_themes.theme_registry import THEMES
from utils.ats_scorer import score_resume
from utils.design_analyzer import analyze_design_reference
from utils.image_parser import enhance_headshot, image_to_data_uri
from utils.insights import build_ai_insights
from utils.models import ProviderSettings, ResumeProfile, WorkflowArtifacts
from utils.pdf_parser import build_requirement_profile, build_resume_profile, extract_text_from_uploads
from utils.resume_builder import generate_resume_html, reconstruct_profile
from utils.storage import load_settings, save_settings
from utils.template_previews import generate_preview_images, get_preview_image_path, preview_image_exists, write_preview_html
from utils.translator import localize_resume

logging.basicConfig(level=logging.INFO)

ICON_PATH = Path(__file__).parent / "assets" / "smart-monkey-icon.svg"
VARIANT_THEME_MAP = {
    "ATS Optimized": "Modern ATS",
    "Korean Resume": "Korean Corporate",
    "Executive Resume": "Executive",
    "Consulting Resume": "Consulting",
    "Startup Resume": "Startup",
}
TEMPLATE_CATALOG = {
    "Modern ATS": {
        "label": "Modern ATS",
        "tag": "Best for ATS",
        "description": "Clean single-column emphasis with strong readability and recruiter-safe spacing.",
        "layout": "Balanced two-column",
    },
    "Executive": {
        "label": "Executive",
        "tag": "Leadership",
        "description": "Premium serif-forward presentation for senior roles and strategic profiles.",
        "layout": "Wide header with structured sidebar",
    },
    "Minimalist": {
        "label": "Minimalist",
        "tag": "Simple",
        "description": "Quiet, modern layout with restrained color and compact information density.",
        "layout": "Minimal two-column",
    },
    "Consulting": {
        "label": "Consulting",
        "tag": "Structured",
        "description": "Sharp hierarchy and analytical tone for consulting, strategy, and operations roles.",
        "layout": "Structured grid",
    },
    "Startup": {
        "label": "Startup",
        "tag": "Bold",
        "description": "Warmer accent palette and energetic presentation for product and startup profiles.",
        "layout": "Creative split layout",
    },
    "Corporate Blue": {
        "label": "Corporate Blue",
        "tag": "Classic",
        "description": "Traditional professional styling for enterprise and corporate applications.",
        "layout": "Classic resume frame",
    },
    "Korean Corporate": {
        "label": "Korean Corporate",
        "tag": "Korean",
        "description": "Formal, clean presentation tuned for Korean-language resume output.",
        "layout": "Formal business layout",
    },
    "Global Tech": {
        "label": "Global Tech",
        "tag": "Tech",
        "description": "Modern technical profile layout with crisp contrast and strong skill grouping.",
        "layout": "Modern technical grid",
    },
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
        .hero-stats {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.85rem;
            margin-top: 1.2rem;
        }
        .hero-stat {
            border-radius: 18px;
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(148, 163, 184, 0.18);
            padding: 0.9rem;
        }
        .hero-stat strong {
            display: block;
            font-size: 1.2rem;
            color: #111827;
            margin-bottom: 0.2rem;
        }
        .upload-stage-grid {
            display: grid;
            grid-template-columns: minmax(0, 1.05fr) minmax(280px, 0.95fr);
            gap: 1rem;
            margin-top: 1rem;
        }
        .upload-dropzone {
            border-radius: 26px;
            border: 1.5px dashed rgba(79, 70, 229, 0.28);
            background: linear-gradient(180deg, rgba(255,255,255,0.92), rgba(244, 247, 255, 0.88));
            padding: 1.2rem;
        }
        .upload-dropzone h4 {
            margin: 0 0 0.45rem 0;
            color: #111827;
        }
        .upload-dropzone p {
            margin: 0;
            color: #6b7280;
            line-height: 1.65;
        }
        .upload-checklist {
            border-radius: 24px;
            background: rgba(248, 250, 252, 0.92);
            border: 1px solid rgba(148, 163, 184, 0.16);
            padding: 1.1rem;
        }
        .upload-checklist-item {
            display: flex;
            gap: 0.7rem;
            align-items: flex-start;
            margin-bottom: 0.85rem;
            color: #374151;
        }
        .upload-checklist-item strong {
            color: #111827;
        }
        .requirement-panel {
            border-radius: 24px;
            background: rgba(255,255,255,0.9);
            border: 1px solid rgba(148, 163, 184, 0.18);
            padding: 1.1rem;
            box-shadow: 0 14px 30px rgba(15, 23, 42, 0.04);
            margin-bottom: 0.9rem;
        }
        .requirement-panel h4 {
            margin: 0 0 0.45rem 0;
            color: #111827;
        }
        .requirement-panel p {
            margin: 0;
            color: #6b7280;
            line-height: 1.65;
        }
        .requirement-note {
            border-radius: 18px;
            background: rgba(79, 70, 229, 0.06);
            color: #4338ca;
            padding: 0.8rem 0.9rem;
            font-size: 0.9rem;
            font-weight: 600;
            margin-top: 0.8rem;
        }
        .upload-pill-row {
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem;
            margin-top: 0.9rem;
        }
        .upload-pill {
            display: inline-flex;
            align-items: center;
            padding: 0.38rem 0.7rem;
            border-radius: 999px;
            background: rgba(79, 70, 229, 0.08);
            color: #4338ca;
            font-size: 0.8rem;
            font-weight: 700;
        }
        .workflow-card {
            background: rgba(255,255,255,0.82);
            border: 1px solid rgba(148, 163, 184, 0.2);
            border-radius: 28px;
            box-shadow: 0 18px 40px rgba(15, 23, 42, 0.06);
            padding: 1.5rem;
            margin-bottom: 1.25rem;
        }
        .workflow-step {
            display: inline-flex;
            align-items: center;
            gap: 0.55rem;
            padding: 0.45rem 0.8rem;
            border-radius: 999px;
            background: rgba(79, 70, 229, 0.08);
            color: #4338ca;
            font-size: 0.82rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            margin-bottom: 0.9rem;
        }
        .score-card {
            background: linear-gradient(180deg, #ffffff, #f8fafc);
            border: 1px solid rgba(148, 163, 184, 0.18);
            border-radius: 22px;
            padding: 1rem;
            height: 100%;
        }
        .score-big {
            font-size: 2.6rem;
            font-weight: 700;
            color: #111827;
            line-height: 1;
        }
        .muted-copy {
            color: #6b7280;
        }
        .template-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 1rem;
            margin: 1rem 0 1.25rem 0;
        }
        .template-card {
            border-radius: 24px;
            border: 1px solid rgba(148, 163, 184, 0.18);
            background: rgba(255,255,255,0.9);
            padding: 1rem;
            box-shadow: 0 14px 30px rgba(15, 23, 42, 0.05);
        }
        .template-preview {
            height: 220px;
            border-radius: 18px;
            padding: 0.9rem;
            margin-bottom: 0.9rem;
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 0.75rem;
            overflow: hidden;
        }
        .template-main,
        .template-side {
            border-radius: 14px;
            background: rgba(255,255,255,0.82);
            padding: 0.7rem;
        }
        .template-line {
            height: 8px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.35);
            margin-bottom: 0.45rem;
        }
        .template-line.short {
            width: 58%;
        }
        .template-line.medium {
            width: 78%;
        }
        .template-chip {
            display: inline-flex;
            align-items: center;
            padding: 0.28rem 0.6rem;
            border-radius: 999px;
            font-size: 0.72rem;
            font-weight: 700;
            margin-bottom: 0.6rem;
        }
        .analysis-shell {
            display: grid;
            grid-template-columns: 1.1fr 0.9fr;
            gap: 1.25rem;
            align-items: center;
        }
        .analysis-visual {
            min-height: 280px;
            border-radius: 28px;
            background: linear-gradient(135deg, rgba(224, 231, 255, 0.9), rgba(236, 253, 245, 0.9));
            padding: 1.25rem;
            position: relative;
            overflow: hidden;
        }
        .analysis-orb {
            position: absolute;
            border-radius: 999px;
            filter: blur(6px);
            animation: floaty 4.8s ease-in-out infinite;
        }
        .analysis-orb.one {
            width: 120px;
            height: 120px;
            background: rgba(79, 70, 229, 0.18);
            top: 24px;
            left: 28px;
        }
        .analysis-orb.two {
            width: 160px;
            height: 160px;
            background: rgba(16, 185, 129, 0.16);
            right: 24px;
            bottom: 18px;
            animation-delay: 0.8s;
        }
        .analysis-panel {
            position: relative;
            z-index: 1;
            height: 100%;
            border-radius: 22px;
            background: rgba(255,255,255,0.78);
            border: 1px solid rgba(255,255,255,0.6);
            padding: 1rem;
            backdrop-filter: blur(10px);
        }
        .analysis-bar {
            height: 12px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.28);
            overflow: hidden;
            margin: 0.8rem 0 1rem 0;
        }
        .analysis-bar span {
            display: block;
            height: 100%;
            width: 72%;
            background: linear-gradient(90deg, #4f46e5, #10b981);
            animation: pulsebar 2.2s ease-in-out infinite;
        }
        .analysis-line {
            height: 10px;
            border-radius: 999px;
            background: rgba(148, 163, 184, 0.3);
            margin-bottom: 0.65rem;
        }
        .analysis-line.short {
            width: 62%;
        }
        .analysis-line.medium {
            width: 78%;
        }
        @keyframes floaty {
            0% { transform: translateY(0px) translateX(0px); }
            50% { transform: translateY(-10px) translateX(8px); }
            100% { transform: translateY(0px) translateX(0px); }
        }
        @keyframes pulsebar {
            0% { width: 58%; }
            50% { width: 82%; }
            100% { width: 58%; }
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
            .hero-stats,
            .upload-stage-grid,
            .analysis-shell {
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
    if "workflow_stage" not in st.session_state:
        st.session_state.workflow_stage = 1
    if "analysis_ready" not in st.session_state:
        st.session_state.analysis_ready = False
    if "analysis_started" not in st.session_state:
        st.session_state.analysis_started = False


def render_branding() -> None:
    st.markdown(
        """
        <section class='hero-shell'>
            <div class='hero-kicker'>Resume Checker</div>
            <div class='hero-grid'>
                <div class='hero-copy'>
                    <h1>Is your resume good enough?</h1>
                    <p>Upload your current resume, match it against a real job description, review the ATS gap, then edit and export polished English and Korean resume versions in one guided flow.</p>
                    <div class='hero-upload'>
                        <strong>Step 1 starts here</strong>
                        <span>Upload one resume or multiple supporting files, then continue to the requirement matching flow.</span>
                    </div>
                    <div class='hero-stats'>
                        <div class='hero-stat'>
                            <strong>1 to many</strong>
                            <span class='muted-copy'>Upload one resume or multiple PDFs in the same intake.</span>
                        </div>
                        <div class='hero-stat'>
                            <strong>ATS first</strong>
                            <span class='muted-copy'>Review the score and gaps before any generation happens.</span>
                        </div>
                        <div class='hero-stat'>
                            <strong>Editable HTML</strong>
                            <span class='muted-copy'>Refine the final resume before exporting English and Korean files.</span>
                        </div>
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


def render_sidebar_navigation() -> None:
    with st.sidebar:
        st.markdown("## Smart Monkey")
        st.caption("Workflow progress")
        stages = [
            (1, "Upload resume"),
            (2, "Add job description"),
            (3, "Analyze ATS fit"),
            (4, "Edit resume"),
            (5, "Export files"),
        ]
        current_stage = st.session_state.workflow_stage
        for stage_number, label in stages:
            marker = "●" if current_stage == stage_number else "○"
            st.markdown(f"{marker} {label}")
        st.caption("Follow the steps from top to bottom.")


def set_stage(route: str, stage: int) -> None:
    st.session_state.workflow_stage = stage


def render_stage_header(step: str, title: str, description: str) -> None:
    st.markdown("<div class='workflow-card'>", unsafe_allow_html=True)
    st.markdown(f"<div class='workflow-step'>{step}</div>", unsafe_allow_html=True)
    st.markdown(f"### {title}")
    st.caption(description)


def close_stage_header() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


def render_template_gallery(selected_theme: str) -> str:
    st.markdown("#### Template gallery")
    st.caption("Browse the available resume styles and select the one that best matches the role and tone you want.")
    theme_names = list(TEMPLATE_CATALOG.keys())
    selected = selected_theme if selected_theme in TEMPLATE_CATALOG else theme_names[0]
    columns = st.columns(2, gap="large")
    for index, theme_name in enumerate(theme_names):
        theme = THEMES[theme_name]
        meta = TEMPLATE_CATALOG[theme_name]
        with columns[index % 2]:
            st.markdown("<div class='template-card'>", unsafe_allow_html=True)
            preview_path = get_preview_image_path(theme_name)
            if preview_image_exists(theme_name):
                st.image(str(preview_path), use_container_width=True)
            else:
                st.markdown(
                    f"""
                    <div class='template-preview' style='background: linear-gradient(135deg, {theme['background']}, {theme['surface']});'>
                        <div class='template-main'>
                            <div class='template-chip' style='background:{theme['accent']}18;color:{theme['accent']};'>{meta['tag']}</div>
                            <div class='template-line medium' style='background:{theme['accent']}55; height: 10px;'></div>
                            <div class='template-line'></div>
                            <div class='template-line medium'></div>
                            <div class='template-line short'></div>
                            <div class='template-line'></div>
                            <div class='template-line short'></div>
                        </div>
                        <div class='template-side'>
                            <div class='template-line medium' style='background:{theme['accent']}40;'></div>
                            <div class='template-line short'></div>
                            <div class='template-line'></div>
                            <div class='template-line short'></div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            st.markdown(f"**{meta['label']}**")
            st.caption(meta['description'])
            st.caption(f"Layout: {meta['layout']}")
            if st.button(
                "Selected" if selected == theme_name else f"Use {meta['label']}",
                key=f"template_select_{theme_name}",
                use_container_width=True,
                disabled=selected == theme_name,
            ):
                selected = theme_name
                st.session_state.workflow.selected_theme = theme_name
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    return selected


def cache_template_preview_html(profile: ResumeProfile, photo_data_uri: str | None = None) -> None:
    for theme_name in TEMPLATE_CATALOG:
        preview_html = generate_resume_html(profile, theme_name, photo_data_uri)
        write_preview_html(theme_name, preview_html)
    generate_preview_images()


def render_home_page() -> None:
    uploads = st.session_state.uploads
    render_stage_header(
        "Step 1",
        "Upload your current resume",
        "Start with one PDF or multiple PDFs. You can combine resume, portfolio, project, and certification files in one intake step.",
    )
    st.markdown(
        """
        <div class='upload-stage-grid'>
            <div class='upload-dropzone'>
                <h4>Upload the source files for this application</h4>
                <p>Add your current resume first. You can also include portfolio, project, or certification files if they contain verified evidence you want the system to use later.</p>
                <div class='upload-pill-row'>
                    <span class='upload-pill'>PDF</span>
                    <span class='upload-pill'>DOCX</span>
                    <span class='upload-pill'>TXT</span>
                    <span class='upload-pill'>Multiple files supported</span>
                </div>
            </div>
            <div class='upload-checklist'>
                <div class='upload-checklist-item'><span>01</span><div><strong>Upload your current resume</strong><br/>Start with the exact material you already have.</div></div>
                <div class='upload-checklist-item'><span>02</span><div><strong>Add the target job description</strong><br/>Paste text or upload the requirement file in the next step.</div></div>
                <div class='upload-checklist-item'><span>03</span><div><strong>Review ATS fit before generation</strong><br/>Only then generate and edit the optimized resume.</div></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    resume_files = st.file_uploader(
        "Upload resume files",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        key="home_resume_files",
        label_visibility="collapsed",
    )
    if resume_files:
        uploads["resume_files"] = resume_files
        st.success(f"{len(resume_files)} file(s) ready for analysis.")
        file_names = ", ".join(file.name for file in resume_files[:4])
        if len(resume_files) > 4:
            file_names = f"{file_names}, +{len(resume_files) - 4} more"
        st.caption(f"Attached: {file_names}")
    else:
        st.caption("Supported formats: PDF, DOCX, TXT")
    if st.button("Continue to Job Description", type="primary", use_container_width=True):
        if not uploads["resume_files"]:
            st.error("Upload at least one resume file before continuing.")
        else:
            set_stage("/analysis", 2)
            st.rerun()
    close_stage_header()


def render_requirement_page() -> None:
    uploads = st.session_state.uploads
    render_stage_header(
        "Step 2",
        "Add the job description",
        "Paste the role description or upload one or more requirement files. This is the target the resume will be optimized against.",
    )
    left, right = st.columns(2, gap="large")
    with left:
        st.markdown(
            """
            <div class='requirement-panel'>
                <h4>Paste the full job description</h4>
                <p>Include responsibilities, required skills, preferred qualifications, tools, and any role-specific language you want the ATS analysis to match against.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        uploads["jd_text"] = st.text_area(
            "Paste job description",
            value=uploads.get("jd_text", ""),
            height=320,
            key="workflow_jd_text",
            placeholder="Paste the full job description here...",
            label_visibility="collapsed",
        )
        st.markdown(
            "<div class='requirement-note'>Best results come from the full job post, not a short summary.</div>",
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(
            """
            <div class='requirement-panel'>
                <h4>Upload requirement and optional reference files</h4>
                <p>Upload the job description if it is saved as a document. You can also add a design reference and a profile photo for the final resume layout.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        jd_files = st.file_uploader(
            "Or upload job description files",
            type=["pdf", "docx", "txt"],
            accept_multiple_files=True,
            key="workflow_jd_files",
            label_visibility="collapsed",
        )
        if jd_files:
            uploads["jd_files"] = jd_files
            st.success(f"{len(jd_files)} requirement file(s) attached.")
        uploads["design_reference"] = st.file_uploader(
            "Optional design reference",
            type=["pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=False,
            key="workflow_design_reference",
            label_visibility="collapsed",
        )
        uploads["photo"] = st.file_uploader(
            "Optional profile photo",
            type=["png", "jpg", "jpeg"],
            accept_multiple_files=False,
            key="workflow_photo",
            label_visibility="collapsed",
        )
    action_left, action_right = st.columns(2)
    with action_left:
        if st.button("Back", use_container_width=True):
            set_stage("/upload", 1)
            st.rerun()
    with action_right:
        if st.button("Analyze Requirements", type="primary", use_container_width=True):
            if not uploads.get("jd_text") and not uploads.get("jd_files"):
                st.error("Paste a job description or upload at least one requirement file.")
            else:
                st.session_state.analysis_ready = False
                st.session_state.analysis_started = False
                set_stage("/analysis", 3)
                st.rerun()
    close_stage_header()


def render_analysis_loading_page() -> None:
    if not st.session_state.analysis_started:
        st.session_state.analysis_started = True
        st.rerun()

    render_stage_header(
        "Step 3",
        "Analyzing your resume against the requirement",
        "The app is extracting the requirement, checking ATS fit, and preparing a verified optimization plan before generating the resume.",
    )
    st.markdown(
        """
        <div class='analysis-shell'>
            <div>
                <h3 style='margin-bottom:0.75rem;'>Working on the requirement match</h3>
                <p class='muted-copy'>We are checking keyword alignment, skill coverage, role fit, and verified evidence from your uploaded resume. No unsupported claims should be added.</p>
                <div class='analysis-bar'><span></span></div>
                <div class='analysis-line'></div>
                <div class='analysis-line medium'></div>
                <div class='analysis-line short'></div>
                <div class='requirement-note' style='margin-top:1rem;'>LLM is processing your request. This step may take a few seconds depending on the provider and file size.</div>
            </div>
            <div class='analysis-visual'>
                <div class='analysis-orb one'></div>
                <div class='analysis-orb two'></div>
                <div class='analysis-panel'>
                    <div style='font-size:0.8rem;font-weight:700;color:#4f46e5;margin-bottom:0.8rem;'>ATS ANALYSIS</div>
                    <div class='analysis-line medium'></div>
                    <div class='analysis-line'></div>
                    <div class='analysis-line short'></div>
                    <div class='analysis-bar'><span></span></div>
                    <div class='analysis-line'></div>
                    <div class='analysis-line medium'></div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.spinner("Analyzing resume and job description..."):
        analyze_current_resume()
    st.session_state.analysis_ready = True
    st.session_state.analysis_started = False
    st.rerun()
    close_stage_header()


def render_ats_review_page() -> None:
    workflow: WorkflowArtifacts = st.session_state.workflow
    if not workflow.ats_report:
        st.info("Complete the upload and job description steps first.")
        return
    render_stage_header(
        "Step 3",
        "Review ATS fit before generation",
        "The app checks the current resume against the requirement, highlights the gaps, and asks for confirmation before generating the optimized version.",
    )
    report = workflow.ats_report
    score_left, score_mid, score_right = st.columns(3, gap="large")
    with score_left:
        st.markdown(f"<div class='score-card'><div class='muted-copy'>Current ATS Score</div><div class='score-big'>{report.ats_score}%</div><div class='muted-copy'>Based on your uploaded resume</div></div>", unsafe_allow_html=True)
    with score_mid:
        st.markdown(f"<div class='score-card'><div class='muted-copy'>Keyword Match</div><div class='score-big'>{report.match_percentage}%</div><div class='muted-copy'>Role language alignment</div></div>", unsafe_allow_html=True)
    with score_right:
        st.markdown(f"<div class='score-card'><div class='muted-copy'>Skills Match</div><div class='score-big'>{report.skill_match_percentage}%</div><div class='muted-copy'>Verified skills only</div></div>", unsafe_allow_html=True)
    st.markdown("#### What needs attention")
    gap_left, gap_right = st.columns(2, gap="large")
    with gap_left:
        st.markdown("**Missing skills**")
        for item in report.missing_skills[:8] or ["No major missing skills detected"]:
            st.markdown(f"- {item}")
    with gap_right:
        st.markdown("**Suggested improvements**")
        for item in report.suggested_improvements[:8] or ["No immediate improvements suggested"]:
            st.markdown(f"- {item}")
    if st.button("Generate Optimized Resume", type="primary", use_container_width=True):
        generate_resume_variant("ATS Optimized")
        set_stage("/editor", 4)
        st.rerun()
    close_stage_header()


def render_resume_generation_page() -> None:
    workflow: WorkflowArtifacts = st.session_state.workflow
    if not workflow.english_html:
        st.info("Generate the optimized resume after the ATS review step.")
        return
    render_stage_header(
        "Step 4",
        "Review and edit the generated resume",
        "The optimized resume is generated in editable HTML. Only verified information should appear. If something is uncertain, you can edit or remove it before export.",
    )
    before_score = workflow.ats_report.ats_score if workflow.ats_report else 0
    live_report = score_resume(workflow.optimized_profile, workflow.requirements) if workflow.requirements else None
    after_score = live_report.ats_score if live_report else before_score
    score_left, score_right = st.columns(2, gap="large")
    with score_left:
        st.metric("Before ATS Score", f"{before_score}%")
    with score_right:
        st.metric("After ATS Score", f"{after_score}%", delta=after_score - before_score)
    workflow.selected_theme = render_template_gallery(workflow.selected_theme)
    toolbar_left, toolbar_right = st.columns([1.1, 0.9], gap="large")
    with toolbar_left:
        workflow.selected_theme = st.selectbox(
            "Selected template",
            list(TEMPLATE_CATALOG.keys()),
            index=list(TEMPLATE_CATALOG.keys()).index(workflow.selected_theme)
            if workflow.selected_theme in TEMPLATE_CATALOG
            else 0,
        )
    with toolbar_right:
        workflow.active_language = st.segmented_control(
            "Preview language",
            ["English", "Korean"],
            default=workflow.active_language,
        )
    edit_col, preview_col = st.columns([0.95, 1.25], gap="large")
    with edit_col:
        st.markdown("#### CMS-style content editor")
        active_profile = workflow.optimized_profile if workflow.active_language == "English" else workflow.localized_profile
        edited_profile = render_profile_editor(active_profile, workflow.active_language.lower())
        if workflow.active_language == "English":
            workflow.optimized_profile = edited_profile
            workflow.english_html = generate_resume_html(workflow.optimized_profile, workflow.selected_theme)
        else:
            workflow.localized_profile = edited_profile
            workflow.korean_html = generate_resume_html(workflow.localized_profile, "Korean Corporate")
    with preview_col:
        st.markdown("#### HTML preview")
        preview_html = workflow.english_html if workflow.active_language == "English" else workflow.korean_html
        st.components.v1.html(preview_html, height=980, scrolling=True)
    if live_report:
        with st.expander("Why the score changed", expanded=False):
            for item in live_report.suggested_improvements[:6] or ["No additional suggestions."]:
                st.markdown(f"- {item}")
    if st.button("Finalize Resume", type="primary", use_container_width=True):
        set_stage("/export", 5)
        st.rerun()
    close_stage_header()


def render_final_export_page() -> None:
    workflow: WorkflowArtifacts = st.session_state.workflow
    settings: ProviderSettings = st.session_state.settings
    uploads = st.session_state.uploads
    if not workflow.english_html:
        st.info("Finalize the resume before export.")
        return
    render_stage_header(
        "Step 5",
        "Export English and Korean resumes",
        "When you are satisfied with the final content, download the resume in English and Korean. Korean localization is generated at this stage for a more natural final version.",
    )
    if not workflow.korean_html:
        provider = None
        try:
            provider = build_provider(settings)
        except Exception:
            provider = None

        workflow.localized_profile = (
            localize_resume(workflow.optimized_profile, provider, "Korean") if provider else workflow.optimized_profile
        )

        photo_data_uri = None
        if uploads["photo"] is not None:
            enhanced = enhance_headshot(uploads["photo"].getvalue())
            photo_data_uri = image_to_data_uri(enhanced)

        workflow.korean_html = generate_resume_html(workflow.localized_profile, "Korean Corporate", photo_data_uri)
    render_downloads(workflow.english_html, workflow.korean_html, workflow.optimized_profile)
    st.caption("The Korean version should be reviewed for tone and natural phrasing before sending to employers.")
    close_stage_header()


def render_upload_page() -> None:
    render_home_page()


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
    if st.session_state.workflow_stage <= 2:
        render_requirement_page()
    elif not st.session_state.analysis_ready:
        render_analysis_loading_page()
    else:
        render_ats_review_page()


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
    workflow.localized_profile = ResumeProfile()
    workflow.korean_html = ""

    photo_data_uri = None
    if uploads["photo"] is not None:
        enhanced = enhance_headshot(uploads["photo"].getvalue())
        photo_data_uri = image_to_data_uri(enhanced)

    workflow.english_html = generate_resume_html(workflow.optimized_profile, workflow.selected_theme, photo_data_uri)
    cache_template_preview_html(workflow.optimized_profile, photo_data_uri)
    st.session_state.analysis_ready = True


def render_editor_page() -> None:
    render_resume_generation_page()


def render_export_page() -> None:
    render_final_export_page()


def main() -> None:
    init_state()
    inject_global_styles()
    render_settings_trigger()
    render_branding()
    render_sidebar_navigation()

    stage = st.session_state.workflow_stage
    if stage == 1:
        render_upload_page()
    elif stage in (2, 3):
        render_analysis_page()
    elif stage == 4:
        render_editor_page()
    else:
        render_export_page()


if __name__ == "__main__":
    main()