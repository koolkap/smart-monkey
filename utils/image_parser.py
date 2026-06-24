from __future__ import annotations

import base64
import io

try:
    import cv2
except Exception:
    cv2 = None

try:
    import numpy as np
except Exception:
    np = None
from PIL import Image, ImageEnhance, ImageFilter


def enhance_headshot(image_bytes: bytes) -> bytes:
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    image = _auto_crop_face_region(image)
    image = image.filter(ImageFilter.SMOOTH_MORE)
    image = ImageEnhance.Contrast(image).enhance(1.08)
    image = ImageEnhance.Sharpness(image).enhance(1.15)
    output = io.BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def image_to_data_uri(image_bytes: bytes, mime_type: str = "image/png") -> str:
    encoded = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime_type};base64,{encoded}"


def _auto_crop_face_region(image: Image.Image) -> Image.Image:
    if cv2 is None or np is None:
        return image.resize((512, 512))
    array = np.array(image)
    gray = cv2.cvtColor(array, cv2.COLOR_RGB2GRAY)
    cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(80, 80))
    if len(faces) == 0:
        return image.resize((512, 512))
    x, y, w, h = faces[0]
    pad = int(max(w, h) * 0.45)
    left = max(x - pad, 0)
    top = max(y - pad, 0)
    right = min(x + w + pad, image.width)
    bottom = min(y + h + pad, image.height)
    return image.crop((left, top, right, bottom)).resize((512, 512))
