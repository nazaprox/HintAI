"""
HintAI camera utilities
"""

from PIL import Image
from io import BytesIO


def validate_image(data: bytes):
    try:
        image = Image.open(BytesIO(data))
        return {
            "valid": True,
            "format": image.format,
            "width": image.width,
            "height": image.height,
        }
    except Exception:
        return {
            "valid": False,
            "message": "Image invalide"
        }
