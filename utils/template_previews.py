from __future__ import annotations

from pathlib import Path
import subprocess
import sys


PREVIEW_DIR = Path("data") / "template_previews"


def ensure_preview_dir() -> Path:
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    return PREVIEW_DIR


def get_preview_html_path(theme_name: str) -> Path:
    safe_name = theme_name.lower().replace(" ", "_")
    return ensure_preview_dir() / f"{safe_name}.html"


def get_preview_image_path(theme_name: str) -> Path:
    safe_name = theme_name.lower().replace(" ", "_")
    return ensure_preview_dir() / f"{safe_name}.png"


def write_preview_html(theme_name: str, html: str) -> Path:
    path = get_preview_html_path(theme_name)
    path.write_text(html, encoding="utf-8")
    return path


def preview_image_exists(theme_name: str) -> bool:
    return get_preview_image_path(theme_name).exists()


def generate_preview_images() -> bool:
    script_path = Path(__file__).resolve().parent.parent / "scripts" / "generate_template_previews.py"
    if not script_path.exists():
        return False
    try:
        subprocess.run([sys.executable, str(script_path)], check=True, cwd=Path(__file__).resolve().parent.parent)
        return True
    except Exception:
        return False