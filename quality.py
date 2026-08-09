import cv2
import numpy as np


# ============================================================
# LECTURE IMAGE
# ============================================================

def read_image(file):

    try:
        data = file.getvalue()

        image_array = np.frombuffer(
            data,
            dtype=np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        return image

    except Exception:
        return None


# ============================================================
# NETTETE
# ============================================================

def check_blur(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    variance = cv2.Laplacian(
        gray,
        cv2.CV_64F
    ).var()

    # Seuil volontairement modéré.
    return variance >= 50, variance


# ============================================================
# LUMINOSITE
# ============================================================

def check_brightness(image):

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    brightness = float(np.mean(gray))

    valid = (
        brightness >= 35
        and brightness <= 235
    )

    return valid, brightness


# ============================================================
# DIMENSIONS
# ============================================================

def check_resolution(image):

    height, width = image.shape[:2]

    valid = (
        width >= 500
        and height >= 500
    )

    return valid, width, height


# ============================================================
# CONTROLE COMPLET
# ============================================================

def quality_check(file):

    # Les PDF seront traités par Gemini après sélection.
    mime = getattr(file, "type", "")

    if mime == "application/pdf":

        return {
            "valid": True,
            "type": "pdf",
            "message": "PDF accepté."
        }

    image = read_image(file)

    if image is None:

        return {
            "valid": False,
            "type": "image",
            "message": "Impossible de lire cette image."
        }

    resolution_ok, width, height = check_resolution(image)

    if not resolution_ok:

        return {
            "valid": False,
            "type": "image",
            "message": (
                "Image trop petite. "
                "Prends une photo plus proche."
            )
        }

    blur_ok, blur_score = check_blur(image)

    if not blur_ok:

        return {
            "valid": False,
            "type": "image",
            "message": (
                "Image trop floue. "
                "Reprends la photo."
            ),
            "blur_score": blur_score,
        }

    brightness_ok, brightness = check_brightness(image)

    if not brightness_ok:

        return {
            "valid": False,
            "type": "image",
            "message": (
                "Luminosité insuffisante ou excessive."
            ),
            "brightness": brightness,
        }

    return {
        "valid": True,
        "type": "image",
        "message": "Image de qualité suffisante.",
        "width": width,
        "height": height,
        "blur_score": blur_score,
        "brightness": brightness,
    }