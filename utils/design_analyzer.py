from __future__ import annotations

import io

try:
    import fitz
except Exception:
    fitz = None
from PIL import Image

from utils.models import DesignIntelligence


def analyze_design_reference(file_name: str, file_bytes: bytes) -> DesignIntelligence:
    lowered = file_name.lower()
    if lowered.endswith(".pdf"):
        return _analyze_pdf_design(file_bytes)
    return _analyze_image_design(file_bytes)


def _analyze_pdf_design(file_bytes: bytes) -> DesignIntelligence:
    if fitz is None:
        return DesignIntelligence(
            layout_style="single-column",
            typography="professional",
            font_hierarchy=["name", "section heading", "body"],
            margins="balanced",
            section_arrangement=["header", "summary", "experience", "skills", "education"],
            white_space="moderate",
            color_palette=["#0F4C81", "#F4F1EA", "#1F2933"],
            header_structure="hero",
            sidebar_structure="none",
        )
    document = fitz.open(stream=file_bytes, filetype="pdf")
    page = document[0]
    width = page.rect.width
    blocks = page.get_text("blocks")
    layout_style = "two-column" if any(block[0] > width * 0.55 for block in blocks) else "single-column"
    return DesignIntelligence(
        layout_style=layout_style,
        typography="clean editorial",
        font_hierarchy=["large name header", "section caps", "compact body"],
        margins="narrow" if width > 580 else "balanced",
        section_arrangement=["header", "summary", "experience", "skills", "education"],
        white_space="moderate",
        color_palette=["#0F4C81", "#F4F1EA", "#1F2933"],
        header_structure="hero",
        sidebar_structure="right sidebar" if layout_style == "two-column" else "none",
    )


def _analyze_image_design(file_bytes: bytes) -> DesignIntelligence:
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    width, height = image.size
    layout_style = "two-column" if width > height * 0.7 else "single-column"
    colors = image.resize((32, 32)).getcolors(maxcolors=1024) or []
    dominant = sorted(colors, key=lambda item: item[0], reverse=True)[:3]
    palette = ["#%02x%02x%02x" % color for _, color in dominant]
    return DesignIntelligence(
        layout_style=layout_style,
        typography="modern visual",
        font_hierarchy=["bold title", "medium section labels", "light body"],
        margins="balanced",
        section_arrangement=["header", "summary", "experience", "projects", "education"],
        white_space="airy",
        color_palette=palette,
        header_structure="banner",
        sidebar_structure="left sidebar" if layout_style == "two-column" else "none",
    )
