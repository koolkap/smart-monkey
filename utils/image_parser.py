from __future__ import annotations

import base64
import io

from PIL import Image, ImageEnhance, ImageFilter


def enhance_headshot(image_bytes: bytes) -> bytes:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = image.filter(ImageFilter.SMOOTH_MORE)
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = ImageEnhance.Sharpness(image).enhance(1.15)
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def image_to_data_uri(image_bytes: bytes, mime_type: str = "image/png") -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"
