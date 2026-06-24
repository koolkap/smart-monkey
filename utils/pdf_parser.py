from __future__ import annotations

import io
import logging
import re
from typing import Iterable

try:
    import fitz
except Exception:
    fitz = None

try:
    import pdfplumber
except Exception:
    pdfplumber = None
from pypdf import PdfReader

from utils.models import CertificationItem, ContactInfo, EducationItem, ExperienceItem, ProjectItem, RequirementProfile, ResumeProfile

LOGGER = logging.getLogger(__name__)


def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    chunks: list[str] = []
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        chunks.extend(page.extract_text() or "" for page in reader.pages)
    except Exception:
        LOGGER.exception("pypdf extraction failed, trying fallbacks")

    if not any(chunk.strip() for chunk in chunks):
        try:
            if pdfplumber is None:
                raise RuntimeError("pdfplumber unavailable")
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                chunks = [(page.extract_text() or "") for page in pdf.pages]
        except Exception:
            LOGGER.exception("pdfplumber extraction failed, trying PyMuPDF")

    if not any(chunk.strip() for chunk in chunks):
        try:
            if fitz is None:
                raise RuntimeError("PyMuPDF unavailable")
            document = fitz.open(stream=file_bytes, filetype="pdf")
            chunks = [page.get_text("text") for page in document]
        except Exception:
            LOGGER.exception("PyMuPDF extraction failed")

    return "\n".join(chunk for chunk in chunks if chunk)


def extract_text_from_uploads(files: Iterable) -> str:
    chunks: list[str] = []
    for file in files:
        try:
            if file.type == "application/pdf":
                chunks.append(extract_text_from_pdf_bytes(file.getvalue()))
            else:
                chunks.append(file.getvalue().decode("utf-8", errors="ignore"))
        except Exception as exc:
            LOGGER.exception("Failed to parse upload %s", getattr(file, "name", "unknown"))
            chunks.append(f"[Parse error for {getattr(file, 'name', 'unknown')}: {exc}]")
    return "\n\n".join(chunks)


def _extract_email(text: str) -> str:
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else ""


def _extract_phone(text: str) -> str:
    match = re.search(r"(\+?\d[\d\s().-]{7,}\d)", text)
    return match.group(0) if match else ""


def _extract_links(text: str, keyword: str) -> str:
    for line in text.splitlines():
        if keyword.lower() in line.lower():
            return line.strip()
    return ""


def build_resume_profile(raw_text: str) -> ResumeProfile:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    name = lines[0] if lines else "Candidate"
    summary = " ".join(lines[1:4])[:500]
    skills = _extract_skill_candidates(raw_text)
    soft_skills = _extract_soft_skills(raw_text)
    experience = [
        ExperienceItem(
            title="Professional Experience",
            company="",
            achievements=[line for line in lines if len(line.split()) > 5][:6],
        )
    ]
    education = [EducationItem(institution="See source resume", degree="", field_of_study="")]
    projects = [ProjectItem(name="Highlighted Projects", description=line) for line in lines[4:7]]
    certifications = [CertificationItem(name=skill, issuer="", year="") for skill in skills[:3]]
    return ResumeProfile(
        name=name,
        summary=summary,
        contact=ContactInfo(
            email=_extract_email(raw_text),
            phone=_extract_phone(raw_text),
            linkedin=_extract_links(raw_text, "linkedin"),
            github=_extract_links(raw_text, "github"),
        ),
        skills=skills,
        soft_skills=soft_skills,
        experience=experience,
        education=education,
        projects=projects,
        certifications=certifications,
        achievements_summary=experience[0].achievements[:4],
    )


def build_requirement_profile(raw_text: str) -> RequirementProfile:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    keywords = _extract_skill_candidates(raw_text)
    soft_skills = _extract_soft_skills(raw_text)
    responsibilities = [line for line in lines if len(line.split()) > 6][:8]
    return RequirementProfile(
        title=lines[0] if lines else "Target Role",
        company=lines[1] if len(lines) > 1 else "",
        summary=" ".join(lines[:4])[:500],
        responsibilities=responsibilities,
        skills=keywords[:12],
        soft_skills=soft_skills,
        technologies=keywords[:12],
        tools=keywords[:10],
        keywords=keywords,
        certifications=[word for word in keywords if "cert" in word.lower()][:5],
        experience_level=_infer_experience_level(raw_text),
    )


def _extract_skill_candidates(text: str) -> list[str]:
    common_terms = {
        "python", "java", "javascript", "typescript", "react", "streamlit", "sql", "azure",
        "aws", "gcp", "docker", "kubernetes", "terraform", "devops", "machine learning",
        "ai", "llm", "nlp", "pytorch", "tensorflow", "pandas", "spark", "git", "linux",
        "fastapi", "django", "flask", "ollama", "gemini", "claude", "openai", "ci/cd",
    }
    lowered = text.lower()
    found = [term.title() if term.islower() else term for term in common_terms if term in lowered]
    return sorted(found)


def _infer_experience_level(text: str) -> str:
    lowered = text.lower()
    if "senior" in lowered or "lead" in lowered or "principal" in lowered:
        return "Senior"
    if "staff" in lowered or "architect" in lowered:
        return "Staff"
    if "junior" in lowered or "entry" in lowered:
        return "Junior"
    return "Mid-Level"


def _extract_soft_skills(text: str) -> list[str]:
    soft_skill_terms = [
        "leadership",
        "communication",
        "stakeholder management",
        "problem solving",
        "collaboration",
        "mentoring",
        "ownership",
        "presentation",
        "teamwork",
        "adaptability",
    ]
    lowered = text.lower()
    return [term.title() for term in soft_skill_terms if term in lowered]
