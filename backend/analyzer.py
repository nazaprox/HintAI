"""
HintAI image quality analyzer
"""

from PIL import Image, ImageStat
from io import BytesIO


def analyze_quality(data: bytes):
    try:
        image = Image.open(BytesIO(data)).convert("L")
        stat = ImageStat.Stat(image)
        brightness = stat.mean[0]

        return {
            "quality": "good" if brightness > 40 else "low_light",
            "brightness": brightness
        }
    except Exception:
        return {
            "quality": "invalid"
        }
