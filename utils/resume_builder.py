from __future__ import annotations

import html
import json

from providers.base import LLMProvider
from templates.html_themes.theme_registry import THEMES
from utils.models import (
  CertificationItem,
  ContactInfo,
  EducationItem,
  ExperienceItem,
  ProjectItem,
  RequirementProfile,
  ResumeProfile,
)


def reconstruct_profile(
    base_profile: ResumeProfile,
    requirements: RequirementProfile,
    provider: LLMProvider | None,
) -> ResumeProfile:
    if provider is None:
        return _heuristic_rewrite(base_profile, requirements)

    prompt = (
      "Create a professional ATS-optimized resume JSON object using the candidate profile and job requirements. "
      "Never invent employers, dates, degrees, certifications, tools, or experience that are not supported by the candidate profile. "
      "You may rewrite summaries and achievements for clarity, stronger keyword alignment, and recruiter readability.\n\n"
      "Optimization rules:\n"
      "1. Prioritize exact job-description terminology when it truthfully matches the candidate profile.\n"
      "2. Reflect the target role title in the headline or summary when justified.\n"
      "3. Emphasize verified skills, technologies, tools, and responsibilities from the job requirements.\n"
      "4. Strengthen achievement bullets with business impact language, but do not fabricate metrics.\n"
      "5. Ensure the skills list includes relevant verified keywords from the job description.\n"
      "6. Keep output concise, professional, and valid for ATS parsing.\n\n"
        f"Candidate profile:\n{json.dumps(base_profile.to_dict(), ensure_ascii=False, indent=2)}\n\n"
      f"Job requirements:\n{json.dumps(requirements.to_dict(), ensure_ascii=False, indent=2)}\n\n"
      "Return a complete ResumeProfile-compatible JSON object only."
    )
    response = provider.generate(
      prompt,
      "Return valid JSON only. Optimize for ATS keyword alignment using only verified candidate evidence.",
    )
    try:
        data = json.loads(response)
      return _coerce_resume_profile(data)
    except Exception:
        return _heuristic_rewrite(base_profile, requirements)


  def _coerce_resume_profile(data: dict) -> ResumeProfile:
    contact = data.get("contact") or {}
    return ResumeProfile(
      name=data.get("name", ""),
      headline=data.get("headline", ""),
      summary=data.get("summary", ""),
      contact=ContactInfo(**contact) if isinstance(contact, dict) else ContactInfo(),
      skills=list(data.get("skills") or []),
      experience=[
        ExperienceItem(**item) if isinstance(item, dict) else ExperienceItem()
        for item in (data.get("experience") or [])
      ],
      education=[
        EducationItem(**item) if isinstance(item, dict) else EducationItem()
        for item in (data.get("education") or [])
      ],
      projects=[
        ProjectItem(**item) if isinstance(item, dict) else ProjectItem()
        for item in (data.get("projects") or [])
      ],
      certifications=[
        CertificationItem(**item) if isinstance(item, dict) else CertificationItem()
        for item in (data.get("certifications") or [])
      ],
      publications=list(data.get("publications") or []),
      awards=list(data.get("awards") or []),
      languages=list(data.get("languages") or []),
      soft_skills=list(data.get("soft_skills") or []),
      target_roles=list(data.get("target_roles") or []),
      achievements_summary=list(data.get("achievements_summary") or []),
    )


def _heuristic_rewrite(base_profile: ResumeProfile, requirements: RequirementProfile) -> ResumeProfile:
    profile = ResumeProfile(**base_profile.to_dict())
    prioritized_keywords = []
    for item in requirements.skills + requirements.technologies + requirements.tools + requirements.keywords:
        if item and item not in prioritized_keywords:
            prioritized_keywords.append(item)
    top_skills = ", ".join(prioritized_keywords[:6])
    profile.headline = requirements.title or profile.headline or "Targeted Professional Resume"
    if profile.summary:
        profile.summary = (
            f"{profile.summary} Focused on {top_skills}."
            if top_skills and top_skills.lower() not in profile.summary.lower()
            else profile.summary
        )
    else:
        profile.summary = f"Results-oriented professional aligned to {requirements.title} with strengths in {top_skills}."
    existing_skills = {skill.lower() for skill in profile.skills}
    base_skills = {skill.lower() for skill in base_profile.skills}
    for keyword in prioritized_keywords:
        if keyword.lower() in existing_skills:
            continue
        if keyword.lower() in base_skills:
            profile.skills.append(keyword)
            existing_skills.add(keyword.lower())
    for item in profile.experience:
        if item.achievements:
            item.achievements = [enhance_achievement(line, requirements) for line in item.achievements]
    return profile


def enhance_achievement(text: str, requirements: RequirementProfile) -> str:
    if any(char.isdigit() for char in text):
        return text
    focus = requirements.skills[:2] or requirements.keywords[:2]
    suffix = f" using {', '.join(focus)}" if focus else ""
    return text.rstrip(".") + suffix + "."


def generate_resume_html(profile: ResumeProfile, theme_name: str, photo_data_uri: str | None = None) -> str:
    theme = THEMES[theme_name]
    experience_html = "".join(
        f"<article class='item'><h4>{html.escape(item.title)} | {html.escape(item.company)}</h4>"
        f"<p class='meta'>{html.escape(item.start_date)} - {html.escape(item.end_date)}</p>"
        f"<ul>{''.join(f'<li>{html.escape(point)}</li>' for point in item.achievements)}</ul></article>"
        for item in profile.experience
    )
    education_html = "".join(
        f"<article class='item'><h4>{html.escape(item.degree)} {html.escape(item.field_of_study)}</h4>"
        f"<p>{html.escape(item.institution)}</p></article>"
        for item in profile.education
    )
    projects_html = "".join(
        f"<article class='item'><h4>{html.escape(item.name)}</h4><p>{html.escape(item.description)}</p></article>"
        for item in profile.projects
    )
    photo_html = f"<img class='headshot' src='{photo_data_uri}' alt='Profile photo' />" if photo_data_uri else ""
    return f"""
<!DOCTYPE html>
<html lang='en'>
<head>
  <meta charset='UTF-8' />
  <meta name='viewport' content='width=device-width, initial-scale=1.0' />
  <style>
    :root {{
      --accent: {theme['accent']};
      --background: {theme['background']};
      --surface: {theme['surface']};
      --text: {theme['text']};
      --muted: {theme['muted']};
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; background: linear-gradient(135deg, var(--background), #ffffff); color: var(--text); font-family: {theme['font_body']}; }}
    .page {{ width: 210mm; min-height: 297mm; margin: 0 auto; padding: 18mm; background: var(--surface); display: grid; grid-template-columns: 2fr 1fr; gap: 18px; }}
    .hero {{ grid-column: 1 / -1; display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid var(--accent); padding-bottom: 12px; }}
    h1, h2, h3, h4 {{ font-family: {theme['font_heading']}; margin: 0; }}
    h1 {{ font-size: 30px; letter-spacing: 0.02em; }}
    h2 {{ font-size: 14px; text-transform: uppercase; color: var(--accent); margin-bottom: 8px; }}
    .headline {{ color: var(--muted); margin-top: 6px; }}
    .headshot {{ width: 110px; height: 110px; object-fit: cover; border-radius: 18px; border: 3px solid var(--accent); }}
    .section {{ margin-bottom: 18px; }}
    .item {{ margin-bottom: 12px; }}
    .meta {{ color: var(--muted); font-size: 12px; }}
    ul {{ margin: 8px 0 0 18px; padding: 0; }}
    .skills {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .chip {{ background: rgba(15, 76, 129, 0.08); color: var(--accent); padding: 6px 10px; border-radius: 999px; font-size: 12px; }}
    .sidebar {{ background: rgba(0, 0, 0, 0.02); padding: 14px; border-radius: 16px; }}
    @media (max-width: 900px) {{
      .page {{ width: 100%; min-height: auto; padding: 20px; grid-template-columns: 1fr; }}
      .hero {{ align-items: flex-start; gap: 12px; }}
    }}
  </style>
</head>
<body>
  <main class='page'>
    <section class='hero'>
      <div>
        <h1 contenteditable='true'>{html.escape(profile.name)}</h1>
        <p class='headline' contenteditable='true'>{html.escape(profile.headline)}</p>
        <p contenteditable='true'>{html.escape(profile.summary)}</p>
      </div>
      {photo_html}
    </section>
    <section>
      <div class='section'>
        <h2>Experience</h2>
        {experience_html}
      </div>
      <div class='section'>
        <h2>Projects</h2>
        {projects_html}
      </div>
    </section>
    <aside class='sidebar'>
      <div class='section'>
        <h2>Contact</h2>
        <p>{html.escape(profile.contact.email)}</p>
        <p>{html.escape(profile.contact.phone)}</p>
        <p>{html.escape(profile.contact.linkedin)}</p>
        <p>{html.escape(profile.contact.github)}</p>
      </div>
      <div class='section'>
        <h2>Skills</h2>
        <div class='skills'>{''.join(f"<span class='chip'>{html.escape(skill)}</span>" for skill in profile.skills)}</div>
      </div>
      <div class='section'>
        <h2>Education</h2>
        {education_html}
      </div>
      <div class='section'>
        <h2>Certifications</h2>
        <ul>{''.join(f"<li>{html.escape(item.name)}</li>" for item in profile.certifications)}</ul>
      </div>
    </aside>
  </main>
</body>
</html>
"""
