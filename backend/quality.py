```python
"""
HintAI — Quality Control
========================

Contrôle qualité des exercices avant traitement IA.

Responsabilités :
- validation des fichiers
- validation des images
- correction d'orientation
- recadrage
- amélioration de contraste
- amélioration de netteté
- détection de flou
- détection de luminosité insuffisante
- estimation de qualité OCR
- validation PDF
- génération d'empreintes pour détection de doublons
- préparation des médias destinés à Gemini

Architecture :

    Caméra / Galerie / PDF
              |
              v
       Traitement local
              |
              v
       Contrôle qualité
              |
       +------+------+
       |             |
    REFUSÉ        VALIDÉ
                     |
                     v
                   IA

IMPORTANT :

Le frontend Expo/React Native doit effectuer le premier
traitement de l'image localement lorsque cela est possible.

Ce module constitue la seconde couche de contrôle côté serveur.

Il ne doit jamais considérer une image comme "bonne"
uniquement parce que le frontend l'a déclarée valide.
"""

from __future__ import annotations

import hashlib
import io
import math
import os
import re
import tempfile
from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple


# ============================================================
# IMPORTS OPTIONNELS
# ============================================================

try:
    import cv2
except ImportError:
    cv2 = None


try:
    import numpy as np
except ImportError:
    np = None


try:
    from PIL import Image, ImageEnhance, ImageFilter, ImageOps
except ImportError:
    Image = None
    ImageEnhance = None
    ImageFilter = None
    ImageOps = None


try:
    import fitz
except ImportError:
    fitz = None


# ============================================================
# CONFIGURATION
# ============================================================

MAX_IMAGE_SIZE_MB = float(
    os.getenv(
        "HINTAI_MAX_IMAGE_SIZE_MB",
        "12",
    )
)

MAX_PDF_SIZE_MB = float(
    os.getenv(
        "HINTAI_MAX_PDF_SIZE_MB",
        "20",
    )
)

MIN_IMAGE_WIDTH = int(
    os.getenv(
        "HINTAI_MIN_IMAGE_WIDTH",
        "500",
    )
)

MIN_IMAGE_HEIGHT = int(
    os.getenv(
        "HINTAI_MIN_IMAGE_HEIGHT",
        "500",
    )
)

MAX_IMAGE_WIDTH = int(
    os.getenv(
        "HINTAI_MAX_IMAGE_WIDTH",
        "8000",
    )
)

MAX_IMAGE_HEIGHT = int(
    os.getenv(
        "HINTAI_MAX_IMAGE_HEIGHT",
        "8000",
    )
)

BLUR_THRESHOLD = float(
    os.getenv(
        "HINTAI_BLUR_THRESHOLD",
        "70",
    )
)

DARK_THRESHOLD = float(
    os.getenv(
        "HINTAI_DARK_THRESHOLD",
        "45",
    )
)

BRIGHT_THRESHOLD = float(
    os.getenv(
        "HINTAI_BRIGHT_THRESHOLD",
        "235",
    )
)

MIN_TEXT_RATIO = float(
    os.getenv(
        "HINTAI_MIN_TEXT_RATIO",
        "0.002",
    )
)


# ============================================================
# TYPES
# ============================================================

@dataclass
class QualityResult:
    """
    Résultat du contrôle qualité.
    """

    valid: bool

    score: float

    reasons: list[str]

    warnings: list[str]

    width: int = 0

    height: int = 0

    blur_score: float = 0.0

    brightness: float = 0.0

    sharpness: float = 0.0

    perceptual_hash: Optional[str] = None

    processed_bytes: Optional[bytes] = None

    mime_type: Optional[str] = None

    metadata: Optional[Dict[str, Any]] = None

    def to_dict(
        self,
    ) -> Dict[str, Any]:
        """
        Conversion en dictionnaire JSON.
        """

        return {
            "valid": self.valid,

            "score": round(
                self.score,
                3,
            ),

            "reasons":
                self.reasons,

            "warnings":
                self.warnings,

            "width":
                self.width,

            "height":
                self.height,

            "blurScore":
                round(
                    self.blur_score,
                    3,
                ),

            "brightness":
                round(
                    self.brightness,
                    3,
                ),

            "sharpness":
                round(
                    self.sharpness,
                    3,
                ),

            "perceptualHash":
                self.perceptual_hash,

            "mimeType":
                self.mime_type,

            "metadata":
                self.metadata or {},
        }


# ============================================================
# UTILITAIRES
# ============================================================

def bytes_to_mb(
    data: bytes,
) -> float:
    """
    Convertit une taille en MB.
    """

    return len(data) / (
        1024 * 1024
    )


def sha256_bytes(
    data: bytes,
) -> str:
    """
    Hash cryptographique exact du fichier.
    """

    return hashlib.sha256(
        data
    ).hexdigest()


def detect_mime_type(
    data: bytes,
) -> Optional[str]:
    """
    Détection basique du type via signature binaire.

    Ne fait pas confiance au Content-Type envoyé
    par le frontend.
    """

    if data.startswith(
        b"\xFF\xD8\xFF"
    ):
        return "image/jpeg"

    if data.startswith(
        b"\x89PNG\r\n\x1a\n"
    ):
        return "image/png"

    if data.startswith(
        b"GIF87a"
    ) or data.startswith(
        b"GIF89a"
    ):
        return "image/gif"

    if data.startswith(
        b"%PDF"
    ):
        return "application/pdf"

    if data.startswith(
        b"RIFF"
    ) and data[8:12] == b"WEBP":
        return "image/webp"

    return None


def is_image_mime(
    mime_type: Optional[str],
) -> bool:
    """
    Vérifie si le MIME est une image supportée.
    """

    return mime_type in {
        "image/jpeg",
        "image/png",
        "image/webp",
    }


# ============================================================
# VALIDATION FICHIER
# ============================================================

def validate_file(
    data: bytes,
    *,
    filename: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Validation générale d'un fichier.

    Retourne uniquement les informations de validation.
    """

    if not data:
        return {
            "valid": False,
            "reason": "Fichier vide.",
        }

    size_mb = bytes_to_mb(
        data
    )

    mime_type = detect_mime_type(
        data
    )

    if mime_type is None:
        return {
            "valid": False,
            "reason":
                "Type de fichier non supporté.",
        }

    if is_image_mime(
        mime_type
    ):

        if size_mb > MAX_IMAGE_SIZE_MB:
            return {
                "valid": False,
                "reason":
                    "Image trop volumineuse.",
                "mimeType":
                    mime_type,
                "sizeMB":
                    size_mb,
            }

    elif mime_type == "application/pdf":

        if size_mb > MAX_PDF_SIZE_MB:
            return {
                "valid": False,
                "reason":
                    "PDF trop volumineux.",
                "mimeType":
                    mime_type,
                "sizeMB":
                    size_mb,
            }

    else:
        return {
            "valid": False,
            "reason":
                "Type non autorisé.",
        }

    return {
        "valid": True,

        "mimeType":
            mime_type,

        "sizeMB":
            round(
                size_mb,
                3,
            ),

        "sha256":
            sha256_bytes(
                data
            ),

        "filename":
            filename,
    }


# ============================================================
# IMAGE
# ============================================================

def load_image(
    data: bytes,
):
    """
    Charge une image depuis des bytes.
    """

    if Image is None:
        raise RuntimeError(
            "Pillow n'est pas installé."
        )

    image = Image.open(
        io.BytesIO(
            data
        )
    )

    # Chargement complet pour détecter les fichiers
    # corrompus avant de poursuivre.
    image.load()

    return image


def normalize_image(
    image,
):
    """
    Normalise le format couleur.
    """

    if image.mode in {
        "RGBA",
        "LA",
    }:
        background = Image.new(
            "RGB",
            image.size,
            "white",
        )

        if image.mode == "RGBA":
            background.paste(
                image,
                mask=image.getchannel(
                    "A"
                ),
            )

        else:
            background.paste(
                image
            )

        return background

    if image.mode != "RGB":
        return image.convert(
            "RGB"
        )

    return image


def auto_orient(
    image,
):
    """
    Corrige l'orientation EXIF.
    """

    if ImageOps is None:
        return image

    return ImageOps.exif_transpose(
        image
    )


# ============================================================
# STATISTIQUES IMAGE
# ============================================================

def calculate_brightness(
    image,
) -> float:
    """
    Luminosité moyenne approximative.
    """

    if np is None:
        grayscale = image.convert(
            "L"
        )

        values = list(
            grayscale.getdata()
        )

        if not values:
            return 0.0

        return sum(
            values
        ) / len(values)

    array = np.asarray(
        image.convert(
            "L"
        ),
        dtype=np.float32,
    )

    if array.size == 0:
        return 0.0

    return float(
        array.mean()
    )


def calculate_blur_score(
    image,
) -> float:
    """
    Mesure le niveau de netteté avec la variance
    du Laplacien.

    Plus le score est élevé, plus l'image est nette.
    """

    if cv2 is None or np is None:
        return 0.0

    array = np.asarray(
        image.convert(
            "L"
        )
    )

    laplacian = cv2.Laplacian(
        array,
        cv2.CV_64F,
    )

    return float(
        laplacian.var()
    )


def calculate_sharpness(
    image,
) -> float:
    """
    Score normalisé de netteté.
    """

    blur_score = (
        calculate_blur_score(
            image
        )
    )

    if blur_score <= 0:
        return 0.0

    # Compression logarithmique pour éviter
    # des valeurs gigantesques.
    return min(
        100.0,
        math.log10(
            blur_score + 1
        )
        * 20,
    )


# ============================================================
# CONTRASTE
# ============================================================

def calculate_contrast(
    image,
) -> float:
    """
    Mesure approximative du contraste.
    """

    if np is None:
        grayscale = image.convert(
            "L"
        )

        values = list(
            grayscale.getdata()
        )

        if not values:
            return 0.0

        mean = sum(
            values
        ) / len(values)

        variance = sum(
            (
                value - mean
            ) ** 2
            for value in values
        ) / len(values)

        return math.sqrt(
            variance
        )

    array = np.asarray(
        image.convert(
            "L"
        ),
        dtype=np.float32,
    )

    if array.size == 0:
        return 0.0

    return float(
        array.std()
    )


# ============================================================
# DÉTECTION DE TEXTE
# ============================================================

def estimate_text_density(
    image,
) -> float:
    """
    Estimation très simple de la densité de contenu.

    Ce n'est PAS un OCR.

    Le but est seulement de détecter une photo totalement
    vide ou extrêmement uniforme avant d'envoyer l'image
    à l'étape OCR/IA.
    """

    if cv2 is None or np is None:
        return 0.0

    array = np.asarray(
        image.convert(
            "L"
        )
    )

    if array.size == 0:
        return 0.0

    thresholded = cv2.adaptiveThreshold(
        array,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        10,
    )

    non_zero = np.count_nonzero(
        thresholded
    )

    return (
        non_zero
        / thresholded.size
    )


# ============================================================
# DÉTECTION BORDS
# ============================================================

def detect_edges(
    image,
) -> float:
    """
    Détermine approximativement la présence de contours.

    Utile pour repérer une image complètement vide.
    """

    if cv2 is None or np is None:
        return 0.0

    array = np.asarray(
        image.convert(
            "L"
        )
    )

    edges = cv2.Canny(
        array,
        50,
        150,
    )

    return float(
        np.count_nonzero(
            edges
        )
        / edges.size
    )


# ============================================================
# RECADRAGE
# ============================================================

def crop_to_content(
    image,
    padding: int = 20,
):
    """
    Essaie de supprimer les grandes marges inutiles.

    Le recadrage reste volontairement conservateur :
    on préfère conserver une marge plutôt que couper
    une partie de l'énoncé.
    """

    if cv2 is None or np is None:
        return image

    grayscale = np.asarray(
        image.convert(
            "L"
        )
    )

    # Détection des zones non blanches.
    threshold = cv2.threshold(
        grayscale,
        245,
        255,
        cv2.THRESH_BINARY_INV,
    )[1]

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    if not contours:
        return image

    x_min = image.width
    y_min = image.height
    x_max = 0
    y_max = 0

    found = False

    for contour in contours:

        x, y, w, h = cv2.boundingRect(
            contour
        )

        # Ignore les petits artefacts.
        if w * h < 100:
            continue

        found = True

        x_min = min(
            x_min,
            x,
        )

        y_min = min(
            y_min,
            y,
        )

        x_max = max(
            x_max,
            x + w,
        )

        y_max = max(
            y_max,
            y + h,
        )

    if not found:
        return image

    x_min = max(
        0,
        x_min - padding,
    )

    y_min = max(
        0,
        y_min - padding,
    )

    x_max = min(
        image.width,
        x_max + padding,
    )

    y_max = min(
        image.height,
        y_max + padding,
    )

    if (
        x_max <= x_min
        or y_max <= y_min
    ):
        return image

    return image.crop(
        (
            x_min,
            y_min,
            x_max,
            y_max,
        )
    )


# ============================================================
# AMÉLIORATION
# ============================================================

def enhance_image(
    image,
):
    """
    Amélioration légère de l'image.

    L'objectif n'est pas de rendre l'image artificielle,
    mais d'améliorer sa lisibilité pour OCR/Gemini.
    """

    image = normalize_image(
        image
    )

    if ImageEnhance is not None:

        contrast = ImageEnhance.Contrast(
            image
        )

        image = contrast.enhance(
            1.15
        )

        sharpness = ImageEnhance.Sharpness(
            image
        )

        image = sharpness.enhance(
            1.20
        )

    return image


def resize_if_needed(
    image,
):
    """
    Réduit les images gigantesques sans les agrandir.
    """

    width, height = image.size

    if (
        width <= MAX_IMAGE_WIDTH
        and height <= MAX_IMAGE_HEIGHT
    ):
        return image

    ratio = min(
        MAX_IMAGE_WIDTH
        / width,

        MAX_IMAGE_HEIGHT
        / height,
    )

    new_size = (
        max(
            1,
            int(
                width * ratio
            ),
        ),

        max(
            1,
            int(
                height * ratio
            ),
        ),
    )

    return image.resize(
        new_size
    )


# ============================================================
# ENCODAGE
# ============================================================

def encode_image(
    image,
    quality: int = 92,
) -> bytes:
    """
    Encode une image en JPEG.
    """

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="JPEG",
        quality=quality,
        optimize=True,
    )

    return buffer.getvalue()


# ============================================================
# HASH PERCEPTUEL
# ============================================================

def perceptual_hash(
    image,
) -> str:
    """
    Génère un hash perceptuel simple.

    Il sert à détecter des images similaires.

    Ce hash n'est PAS un hash de sécurité.
    """

    if Image is None:
        raise RuntimeError(
            "Pillow est requis."
        )

    grayscale = image.convert(
        "L"
    )

    resized = grayscale.resize(
        (
            32,
            32,
        )
    )

    if np is None:

        values = list(
            resized.getdata()
        )

        average = (
            sum(values)
            / len(values)
        )

        bits = "".join(
            "1"
            if value >= average
            else "0"
            for value in values
        )

    else:

        array = np.asarray(
            resized,
            dtype=np.float32,
        )

        average = float(
            array.mean()
        )

        bits = "".join(
            "1"
            if value >= average
            else "0"
            for value in array.flatten()
        )

    # Conversion binaire -> hex.
    hexadecimal = ""

    for index in range(
        0,
        len(bits),
        4,
    ):

        hexadecimal += format(
            int(
                bits[
                    index:index + 4
                ],
                2,
            ),
            "x",
        )

    return hexadecimal


def hamming_distance(
    first: str,
    second: str,
) -> int:
    """
    Distance entre deux hashes perceptuels.
    """

    if len(first) != len(
        second
    ):
        return 10**9

    try:

        first_int = int(
            first,
            16,
        )

        second_int = int(
            second,
            16,
        )

    except ValueError:
        return 10**9

    return (
        first_int
        ^ second_int
    ).bit_count()


def are_images_similar(
    first_hash: str,
    second_hash: str,
    threshold: int = 12,
) -> bool:
    """
    Détermine si deux images sont probablement similaires.
    """

    return (
        hamming_distance(
            first_hash,
            second_hash,
        )
        <= threshold
    )


# ============================================================
# CONTRÔLE IMAGE
# ============================================================

def analyze_image(
    data: bytes,
) -> QualityResult:
    """
    Analyse complète d'une image.
    """

    file_validation = validate_file(
        data
    )

    if not file_validation[
        "valid"
    ]:

        return QualityResult(
            valid=False,
            score=0.0,
            reasons=[
                file_validation[
                    "reason"
                ]
            ],
            warnings=[],
        )

    mime_type = file_validation[
        "mimeType"
    ]

    if not is_image_mime(
        mime_type
    ):

        return QualityResult(
            valid=False,
            score=0.0,
            reasons=[
                "Le fichier n'est pas une image."
            ],
            warnings=[],
        )

    try:
        image = load_image(
            data
        )

        image = auto_orient(
            image
        )

        image = normalize_image(
            image
        )

    except Exception as exc:

        return QualityResult(
            valid=False,
            score=0.0,
            reasons=[
                "Image illisible ou corrompue."
            ],
            warnings=[
                str(exc)
            ],
        )

    width, height = (
        image.size
    )

    reasons = []

    warnings = []

    # --------------------------------------------------------
    # Dimensions
    # --------------------------------------------------------

    if (
        width < MIN_IMAGE_WIDTH
        or height < MIN_IMAGE_HEIGHT
    ):

        reasons.append(
            "Résolution trop faible."
        )

    if (
        width > MAX_IMAGE_WIDTH
        or height > MAX_IMAGE_HEIGHT
    ):

        warnings.append(
            "Image très grande."
        )

    # --------------------------------------------------------
    # Statistiques
    # --------------------------------------------------------

    brightness = calculate_brightness(
        image
    )

    blur_score = calculate_blur_score(
        image
    )

    sharpness = calculate_sharpness(
        image
    )

    contrast = calculate_contrast(
        image
    )

    text_density = estimate_text_density(
        image
    )

    edge_density = detect_edges(
        image
    )

    # --------------------------------------------------------
    # Luminosité
    # --------------------------------------------------------

    if brightness < DARK_THRESHOLD:

        reasons.append(
            "Image trop sombre."
        )

    elif brightness > BRIGHT_THRESHOLD:

        warnings.append(
            "Image très claire."
        )

    # --------------------------------------------------------
    # Flou
    # --------------------------------------------------------

    if (
        cv2 is not None
        and blur_score < BLUR_THRESHOLD
    ):

        reasons.append(
            "Image trop floue."
        )

    # --------------------------------------------------------
    # Contraste
    # --------------------------------------------------------

    if contrast < 15:

        reasons.append(
            "Contraste insuffisant."
        )

    elif contrast < 30:

        warnings.append(
            "Contraste faible."
        )

    # --------------------------------------------------------
    # Contenu
    # --------------------------------------------------------

    if (
        cv2 is not None
        and text_density < MIN_TEXT_RATIO
        and edge_density < 0.005
    ):

        reasons.append(
            "Aucun contenu exploitable détecté."
        )

    # --------------------------------------------------------
    # Score
    # --------------------------------------------------------

    score = 100.0

    if width < MIN_IMAGE_WIDTH:
        score -= 25

    if height < MIN_IMAGE_HEIGHT:
        score -= 25

    if brightness < DARK_THRESHOLD:
        score -= 25

    if (
        cv2 is not None
        and blur_score < BLUR_THRESHOLD
    ):
        score -= 30

    if contrast < 15:
        score -= 20

    if (
        cv2 is not None
        and text_density < MIN_TEXT_RATIO
        and edge_density < 0.005
    ):
        score -= 30

    score = max(
        0.0,
        min(
            100.0,
            score,
        ),
    )

    valid = (
        len(reasons) == 0
        and score >= 55
    )

    image_hash = None

    try:
        image_hash = perceptual_hash(
            image
        )
    except Exception:
        warnings.append(
            "Hash perceptuel indisponible."
        )

    return QualityResult(
        valid=valid,

        score=score,

        reasons=reasons,

        warnings=warnings,

        width=width,

        height=height,

        blur_score=blur_score,

        brightness=brightness,

        sharpness=sharpness,

        perceptual_hash=image_hash,

        mime_type=mime_type,

        metadata={
            "contrast":
                contrast,

            "textDensity":
                text_density,

            "edgeDensity":
                edge_density,

            "sha256":
                file_validation[
                    "sha256"
                ],
        },
    )


# ============================================================
# PIPELINE DE TRAITEMENT
# ============================================================

def process_image(
    data: bytes,
) -> QualityResult:
    """
    Pipeline complet :

        validation
            ↓
        orientation
            ↓
        recadrage
            ↓
        amélioration
            ↓
        resize
            ↓
        contrôle final
            ↓
        JPEG optimisé
    """

    initial = analyze_image(
        data
    )

    if not initial.valid:

        return initial

    try:

        image = load_image(
            data
        )

        image = auto_orient(
            image
        )

        image = normalize_image(
            image
        )

        # ----------------------------------------------------
        # Recadrage prudent
        # ----------------------------------------------------

        image = crop_to_content(
            image
        )

        # ----------------------------------------------------
        # Amélioration
        # ----------------------------------------------------

        image = enhance_image(
            image
        )

        # ----------------------------------------------------
        # Resize
        # ----------------------------------------------------

        image = resize_if_needed(
            image
        )

        # ----------------------------------------------------
        # Encodage
        # ----------------------------------------------------

        processed = encode_image(
            image
        )

        # ----------------------------------------------------
        # Analyse finale
        # ----------------------------------------------------

        final_result = analyze_image(
            processed
        )

        if not final_result.valid:

            # On conserve l'information du premier contrôle
            # plutôt que de considérer automatiquement le
            # traitement comme une réussite.
            final_result.warnings.insert(
                0,
                "Le traitement automatique n'a pas amélioré "
                "suffisamment la qualité."
            )

            return final_result

        final_result.processed_bytes = (
            processed
        )

        final_result.mime_type = (
            "image/jpeg"
        )

        return final_result

    except Exception as exc:

        return QualityResult(
            valid=False,

            score=0.0,

            reasons=[
                "Impossible de traiter l'image."
            ],

            warnings=[
                str(exc)
            ],
        )


# ============================================================
# PDF
# ============================================================

def validate_pdf(
    data: bytes,
) -> Dict[str, Any]:
    """
    Vérifie un PDF avant traitement.
    """

    validation = validate_file(
        data
    )

    if not validation[
        "valid"
    ]:

        return validation

    if validation[
        "mimeType"
    ] != "application/pdf":

        return {
            "valid": False,
            "reason":
                "Le fichier n'est pas un PDF.",
        }

    if fitz is None:

        return {
            "valid": False,
            "reason":
                "PyMuPDF n'est pas installé.",
        }

    try:

        document = fitz.open(
            stream=data,
            filetype="pdf",
        )

        pages = document.page_count

        if pages <= 0:

            document.close()

            return {
                "valid": False,
                "reason":
                    "Le PDF ne contient aucune page.",
            }

        if pages > 100:

            document.close()

            return {
                "valid": False,
                "reason":
                    "Le PDF contient trop de pages.",
            }

        # Vérification basique de lisibilité.
        text_length = 0

        for index in range(
            min(
                pages,
                5,
            )
        ):

            page = document.load_page(
                index
            )

            text = page.get_text(
                "text"
            )

            text_length += len(
                text.strip()
            )

        document.close()

        return {
            "valid": True,

            "mimeType":
                "application/pdf",

            "pages":
                pages,

            "textPreviewLength":
                text_length,

            "sha256":
                validation[
                    "sha256"
                ],

            "sizeMB":
                validation[
                    "sizeMB"
                ],
        }

    except Exception as exc:

        return {
            "valid": False,

            "reason":
                "PDF corrompu ou illisible.",

            "details":
                str(exc),
        }


# ============================================================
# EXTRACTION PDF
# ============================================================

def extract_pdf_text(
    data: bytes,
    max_pages: int = 20,
) -> str:
    """
    Extrait le texte d'un PDF lorsque du texte est présent.

    Les PDF purement scannés seront traités par une étape
    image/OCR ultérieure.
    """

    if fitz is None:
        raise RuntimeError(
            "PyMuPDF n'est pas installé."
        )

    document = fitz.open(
        stream=data,
        filetype="pdf",
    )

    parts = []

    try:

        for index in range(
            min(
                document.page_count,
                max_pages,
            )
        ):

            page = document.load_page(
                index
            )

            text = page.get_text(
                "text"
            ).strip()

            if text:
                parts.append(
                    text
                )

    finally:

        document.close()

    return "\n\n".join(
        parts
    )


# ============================================================
# NETTOYAGE OCR
# ============================================================

def clean_ocr_text(
    text: str,
) -> str:
    """
    Nettoyage léger du texte OCR.
    """

    if not text:
        return ""

    text = text.replace(
        "\x00",
        " ",
    )

    # Normalisation des espaces.
    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    # Limitation des lignes vides.
    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def looks_like_useful_text(
    text: str,
) -> bool:
    """
    Vérifie si l'OCR a probablement trouvé quelque chose
    d'exploitable.
    """

    cleaned = clean_ocr_text(
        text
    )

    if len(cleaned) < 5:
        return False

    alphanumeric = sum(
        1
        for char in cleaned
        if char.isalnum()
    )

    return (
        alphanumeric >= 5
    )


# ============================================================
# DÉTECTION DE DOUBLON
# ============================================================

def build_duplicate_signature(
    data: bytes,
    image: Optional[Any] = None,
) -> Dict[str, str]:
    """
    Génère les signatures utiles à la détection
    des documents/images déjà présents.

    storage.py comparera ces signatures avec les documents
    existants.
    """

    exact_hash = sha256_bytes(
        data
    )

    perceptual = ""

    if image is not None:

        try:
            perceptual = perceptual_hash(
                image
            )
        except Exception:
            perceptual = ""

    return {
        "sha256":
            exact_hash,

        "perceptualHash":
            perceptual,
    }


def duplicate_similarity(
    first_signature: Dict[str, str],
    second_signature: Dict[str, str],
) -> Dict[str, Any]:
    """
    Compare deux signatures.
    """

    first_sha = (
        first_signature.get(
            "sha256",
            "",
        )
    )

    second_sha = (
        second_signature.get(
            "sha256",
            "",
        )
    )

    if (
        first_sha
        and second_sha
        and first_sha == second_sha
    ):

        return {
            "duplicate": True,
            "type": "exact",
            "distance": 0,
        }

    first_phash = (
        first_signature.get(
            "perceptualHash",
            "",
        )
    )

    second_phash = (
        second_signature.get(
            "perceptualHash",
            "",
        )
    )

    if (
        first_phash
        and second_phash
    ):

        distance = hamming_distance(
            first_phash,
            second_phash,
        )

        return {
            "duplicate":
                distance <= 12,

            "type":
                "perceptual",

            "distance":
                distance,
        }

    return {
        "duplicate": False,
        "type": "unknown",
        "distance": None,
    }


# ============================================================
# ANALYSE DOCUMENT
# ============================================================

def analyze_document(
    data: bytes,
    filename: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyse un document entrant dans la bibliothèque
    d'épreuves.

    Support :
        image
        PDF
    """

    validation = validate_file(
        data,
        filename=filename,
    )

    if not validation[
        "valid"
    ]:
        return {
            "valid": False,
            "type": "unknown",
            "quality": None,
            "file": validation,
        }

    mime_type = validation[
        "mimeType"
    ]

    if is_image_mime(
        mime_type
    ):

        quality = analyze_image(
            data
        )

        return {
            "valid":
                quality.valid,

            "type":
                "image",

            "file":
                validation,

            "quality":
                quality.to_dict(),
        }

    if mime_type == "application/pdf":

        pdf = validate_pdf(
            data
        )

        return {
            "valid":
                pdf.get(
                    "valid",
                    False,
                ),

            "type":
                "pdf",

            "file":
                validation,

            "quality":
                pdf,
        }

    return {
        "valid": False,
        "type": "unknown",
        "quality": None,
        "file": validation,
    }


# ============================================================
# DÉCISION D'ENVOI À L'IA
# ============================================================

def should_send_to_ai(
    quality: QualityResult,
) -> bool:
    """
    Décision finale concernant l'envoi d'une image
    vers le moteur IA.
    """

    if not quality.valid:
        return False

    if quality.score < 60:
        return False

    if (
        quality.width < MIN_IMAGE_WIDTH
        or quality.height < MIN_IMAGE_HEIGHT
    ):
        return False

    return True


def build_ai_media_metadata(
    quality: QualityResult,
) -> Dict[str, Any]:
    """
    Métadonnées envoyées avec le média à ai.py.
    """

    return {
        "mimeType":
            quality.mime_type,

        "width":
            quality.width,

        "height":
            quality.height,

        "qualityScore":
            round(
                quality.score,
                3,
            ),

        "blurScore":
            round(
                quality.blur_score,
                3,
            ),

        "brightness":
            round(
                quality.brightness,
                3,
            ),

        "sharpness":
            round(
                quality.sharpness,
                3,
            ),

        "perceptualHash":
            quality.perceptual_hash,
    }
```
