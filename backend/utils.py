```python
"""
HintAI — Utils
==============

Utilitaires communs utilisés par le backend.

Ce fichier ne contient PAS de logique métier.

Il regroupe uniquement les fonctions génériques :
- dates et timestamps
- génération d'identifiants
- hash
- validation de données
- nettoyage de texte
- limites de taille
- conversion de données
- réponses communes
- sécurité basique
- helpers pour le streaming

Les fonctionnalités métier restent dans :
    api.py
    config.py
    ai.py
    credits.py
    quality.py
    storage.py
"""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import re
import secrets
import time
import uuid
from datetime import (
    datetime,
    timezone,
)
from decimal import Decimal
from typing import (
    Any,
    AsyncGenerator,
    Dict,
    Iterable,
    Iterator,
    Optional,
)


# ============================================================
# CONFIGURATION
# ============================================================

MAX_TEXT_LENGTH = int(
    os.getenv(
        "HINTAI_MAX_TEXT_LENGTH",
        "20000",
    )
)

MAX_QUESTION_LENGTH = int(
    os.getenv(
        "HINTAI_MAX_QUESTION_LENGTH",
        "5000",
    )
)

MAX_FILENAME_LENGTH = int(
    os.getenv(
        "HINTAI_MAX_FILENAME_LENGTH",
        "255",
    )
)

MAX_METADATA_SIZE = int(
    os.getenv(
        "HINTAI_MAX_METADATA_SIZE",
        "50000",
    )
)


# ============================================================
# TEMPS
# ============================================================

def utc_now() -> datetime:
    """
    Retourne la date/heure UTC actuelle avec timezone.
    """

    return datetime.now(
        timezone.utc
    )


def timestamp() -> int:
    """
    Retourne le timestamp Unix actuel.
    """

    return int(
        time.time()
    )


def timestamp_ms() -> int:
    """
    Timestamp Unix en millisecondes.
    """

    return int(
        time.time()
        * 1000
    )


def datetime_to_timestamp(
    value: Optional[datetime],
) -> Optional[int]:
    """
    Convertit une datetime en timestamp Unix.
    """

    if value is None:
        return None

    if value.tzinfo is None:
        value = value.replace(
            tzinfo=timezone.utc
        )

    return int(
        value.timestamp()
    )


def timestamp_to_datetime(
    value: Optional[int],
) -> Optional[datetime]:
    """
    Convertit un timestamp Unix en datetime UTC.
    """

    if value is None:
        return None

    return datetime.fromtimestamp(
        value,
        tz=timezone.utc,
    )


def iso_now() -> str:
    """
    Date actuelle au format ISO 8601.
    """

    return utc_now().isoformat()


def is_expired(
    expires_at: Optional[int],
) -> bool:
    """
    Vérifie si une expiration est dépassée.
    """

    if expires_at is None:
        return False

    return expires_at <= timestamp()


# ============================================================
# IDENTIFIANTS
# ============================================================

def generate_id(
    prefix: Optional[str] = None,
) -> str:
    """
    Génère un identifiant UUID hexadécimal.

    Exemple :
        usr_8c4d...
    """

    value = uuid.uuid4().hex

    if prefix:
        return (
            f"{prefix}_{value}"
        )

    return value


def generate_token(
    length: int = 32,
) -> str:
    """
    Génère un token cryptographiquement aléatoire.

    length représente approximativement le nombre de
    caractères retournés.
    """

    length = max(
        16,
        int(length),
    )

    byte_length = (
        length + 1
    ) // 2

    return secrets.token_hex(
        byte_length
    )[:length]


def generate_numeric_code(
    digits: int = 6,
) -> str:
    """
    Génère un code numérique.

    Utilisable pour une vérification temporaire.
    """

    digits = max(
        4,
        min(
            digits,
            12,
        ),
    )

    minimum = 10 ** (
        digits - 1
    )

    maximum = (
        10 ** digits
    ) - 1

    return str(
        secrets.randbelow(
            maximum - minimum + 1
        )
        + minimum
    )


# ============================================================
# HASH
# ============================================================

def sha256_bytes(
    data: bytes,
) -> str:
    """
    SHA-256 de données binaires.
    """

    return hashlib.sha256(
        data
    ).hexdigest()


def sha256_text(
    text: str,
) -> str:
    """
    SHA-256 d'un texte UTF-8.
    """

    return sha256_bytes(
        text.encode(
            "utf-8"
        )
    )


def hash_identifier(
    value: str,
) -> str:
    """
    Hash d'un identifiant.

    Utile pour les logs/analytics lorsqu'on ne veut
    pas conserver directement certaines valeurs.
    """

    return sha256_text(
        value.strip()
    )


def secure_compare(
    first: str,
    second: str,
) -> bool:
    """
    Comparaison résistante aux attaques temporelles.
    """

    return hmac.compare_digest(
        str(first),
        str(second),
    )


# ============================================================
# TEXTE
# ============================================================

def normalize_whitespace(
    text: str,
) -> str:
    """
    Nettoie les espaces inutiles.
    """

    if not text:
        return ""

    text = text.replace(
        "\r\n",
        "\n",
    )

    text = text.replace(
        "\r",
        "\n",
    )

    text = re.sub(
        r"[ \t]+",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


def clean_text(
    text: Any,
    *,
    max_length: int = MAX_TEXT_LENGTH,
) -> str:
    """
    Convertit et nettoie un texte.

    La longueur maximale protège le backend contre
    les entrées excessivement grandes.
    """

    if text is None:
        return ""

    text = str(
        text
    )

    text = text.replace(
        "\x00",
        "",
    )

    text = normalize_whitespace(
        text
    )

    return text[
        :max_length
    ]


def clean_question(
    question: Any,
) -> str:
    """
    Nettoie une question destinée à l'IA.
    """

    return clean_text(
        question,
        max_length=MAX_QUESTION_LENGTH,
    )


def clean_filename(
    filename: Any,
) -> str:
    """
    Nettoie un nom de fichier.

    Empêche notamment les chemins du type :
        ../../secret.txt
    """

    if filename is None:
        return "document"

    filename = str(
        filename
    )

    # Suppression des chemins.
    filename = filename.replace(
        "\\",
        "/",
    )

    filename = filename.split(
        "/"
    )[-1]

    # Suppression des caractères de contrôle.
    filename = re.sub(
        r"[\x00-\x1f\x7f]",
        "",
        filename,
    )

    # Évite les noms problématiques.
    filename = filename.strip(
        " ."
    )

    if not filename:
        filename = "document"

    return filename[
        :MAX_FILENAME_LENGTH
    ]


def truncate_text(
    text: str,
    max_length: int,
    suffix: str = "...",
) -> str:
    """
    Tronque un texte proprement.
    """

    text = str(
        text or ""
    )

    if len(text) <= max_length:
        return text

    if max_length <= len(
        suffix
    ):
        return text[
            :max_length
        ]

    return (
        text[
            :max_length
            - len(suffix)
        ]
        + suffix
    )


def text_length(
    text: Any,
) -> int:
    """
    Longueur d'un texte nettoyé.
    """

    return len(
        clean_text(
            text
        )
    )


# ============================================================
# VALIDATION
# ============================================================

def is_valid_email(
    email: Any,
) -> bool:
    """
    Validation basique d'une adresse email.

    La validation finale d'un email doit idéalement être
    faite par confirmation de l'utilisateur.
    """

    if not email:
        return False

    email = str(
        email
    ).strip()

    if len(email) > 320:
        return False

    pattern = (
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    return bool(
        re.match(
            pattern,
            email,
        )
    )


def normalize_email(
    email: Any,
) -> str:
    """
    Normalise une adresse email.
    """

    if email is None:
        return ""

    return str(
        email
    ).strip().lower()


def is_valid_uuid(
    value: Any,
) -> bool:
    """
    Vérifie si une valeur ressemble à un UUID.
    """

    if not value:
        return False

    try:
        uuid.UUID(
            str(value)
        )
        return True

    except (
        ValueError,
        TypeError,
        AttributeError,
    ):
        return False


def is_positive_int(
    value: Any,
) -> bool:
    """
    Vérifie un entier strictement positif.
    """

    return (
        isinstance(
            value,
            int,
        )
        and not isinstance(
            value,
            bool,
        )
        and value > 0
    )


def clamp(
    value: float,
    minimum: float,
    maximum: float,
) -> float:
    """
    Force une valeur dans un intervalle.
    """

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


def clamp_int(
    value: Any,
    minimum: int,
    maximum: int,
) -> int:
    """
    Version entière de clamp.
    """

    try:
        value = int(
            value
        )
    except (
        ValueError,
        TypeError,
    ):
        value = minimum

    return max(
        minimum,
        min(
            maximum,
            value,
        ),
    )


# ============================================================
# JSON
# ============================================================

def json_dumps(
    data: Any,
    *,
    compact: bool = False,
) -> str:
    """
    Sérialisation JSON robuste.
    """

    if compact:

        return json.dumps(
            data,
            ensure_ascii=False,
            separators=(
                ",",
                ":",
            ),
            default=str,
        )

    return json.dumps(
        data,
        ensure_ascii=False,
        default=str,
    )


def json_loads(
    data: Any,
    default: Any = None,
) -> Any:
    """
    Désérialisation JSON sécurisée.

    Retourne default si le JSON est invalide.
    """

    if data is None:
        return default

    try:

        if isinstance(
            data,
            bytes,
        ):
            data = data.decode(
                "utf-8"
            )

        return json.loads(
            data
        )

    except (
        json.JSONDecodeError,
        UnicodeDecodeError,
        TypeError,
    ):

        return default


# ============================================================
# DONNÉES / DICTIONNAIRES
# ============================================================

def remove_none(
    data: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Supprime les valeurs None d'un dictionnaire.
    """

    return {
        key: value
        for key, value
        in data.items()
        if value is not None
    }


def pick(
    data: Dict[str, Any],
    keys: Iterable[str],
) -> Dict[str, Any]:
    """
    Sélectionne uniquement certaines clés.
    """

    return {
        key: data[key]
        for key in keys
        if key in data
    }


def omit(
    data: Dict[str, Any],
    keys: Iterable[str],
) -> Dict[str, Any]:
    """
    Supprime certaines clés.
    """

    excluded = set(
        keys
    )

    return {
        key: value
        for key, value
        in data.items()
        if key not in excluded
    }


def ensure_dict(
    value: Any,
) -> Dict[str, Any]:
    """
    Retourne un dictionnaire valide.
    """

    if isinstance(
        value,
        dict,
    ):
        return value

    return {}


# ============================================================
# TAILLE
# ============================================================

def bytes_to_mb(
    size: int,
) -> float:
    """
    Convertit bytes -> MB.
    """

    return (
        int(size)
        / (
            1024 * 1024
        )
    )


def mb_to_bytes(
    size_mb: float,
) -> int:
    """
    Convertit MB -> bytes.
    """

    return int(
        float(size_mb)
        * 1024
        * 1024
    )


def validate_size(
    data: bytes,
    max_mb: float,
) -> bool:
    """
    Vérifie qu'un fichier ne dépasse pas une taille.
    """

    if not isinstance(
        data,
        bytes,
    ):
        return False

    return (
        len(data)
        <= mb_to_bytes(
            max_mb
        )
    )


# ============================================================
# TYPES DE FICHIERS
# ============================================================

IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

DOCUMENT_MIME_TYPES = {
    "application/pdf",
}

SUPPORTED_MIME_TYPES = (
    IMAGE_MIME_TYPES
    | DOCUMENT_MIME_TYPES
)


def is_supported_mime(
    mime_type: Optional[str],
) -> bool:
    """
    Vérifie si un MIME est supporté.
    """

    if not mime_type:
        return False

    return (
        mime_type.lower()
        in SUPPORTED_MIME_TYPES
    )


def is_image_mime(
    mime_type: Optional[str],
) -> bool:
    """
    Vérifie si un MIME correspond à une image.
    """

    if not mime_type:
        return False

    return (
        mime_type.lower()
        in IMAGE_MIME_TYPES
    )


def is_pdf_mime(
    mime_type: Optional[str],
) -> bool:
    """
    Vérifie si un MIME correspond à un PDF.
    """

    return (
        mime_type == "application/pdf"
    )


# ============================================================
# ERREURS
# ============================================================

class HintAIError(
    Exception
):
    """
    Erreur générique HintAI.
    """

    def __init__(
        self,
        message: str,
        *,
        code: str = "HINTAI_ERROR",
        status_code: int = 400,
        details: Optional[
            Dict[str, Any]
        ] = None,
    ):
        super().__init__(
            message
        )

        self.message = message

        self.code = code

        self.status_code = (
            status_code
        )

        self.details = (
            details or {}
        )


class ValidationError(
    HintAIError
):
    """
    Données utilisateur invalides.
    """

    def __init__(
        self,
        message: str,
        details: Optional[
            Dict[str, Any]
        ] = None,
    ):
        super().__init__(
            message,
            code="VALIDATION_ERROR",
            status_code=422,
            details=details,
        )


class AuthenticationError(
    HintAIError
):
    """
    Erreur d'authentification.
    """

    def __init__(
        self,
        message: str = "Authentification requise.",
    ):
        super().__init__(
            message,
            code="AUTHENTICATION_REQUIRED",
            status_code=401,
        )


class AuthorizationError(
    HintAIError
):
    """
    Utilisateur authentifié mais non autorisé.
    """

    def __init__(
        self,
        message: str = "Accès refusé.",
    ):
        super().__init__(
            message,
            code="FORBIDDEN",
            status_code=403,
        )


class RateLimitError(
    HintAIError
):
    """
    Limite anti-abus atteinte.
    """

    def __init__(
        self,
        message: str = "Trop de requêtes.",
    ):
        super().__init__(
            message,
            code="RATE_LIMITED",
            status_code=429,
        )


# ============================================================
# RÉPONSES API
# ============================================================

def success_response(
    data: Any = None,
    *,
    message: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Structure standard d'une réponse réussie.
    """

    response = {
        "success": True,
        "data": data,
    }

    if message is not None:
        response[
            "message"
        ] = message

    return response


def error_response(
    message: str,
    *,
    code: str = "ERROR",
    status_code: int = 400,
    details: Optional[
        Dict[str, Any]
    ] = None,
) -> Dict[str, Any]:
    """
    Structure standard d'une erreur API.
    """

    return {
        "success": False,

        "error": {
            "code":
                code,

            "message":
                message,

            "details":
                details or {},
        },

        "statusCode":
            status_code,
    }


def exception_response(
    exception: Exception,
) -> Dict[str, Any]:
    """
    Convertit une exception en réponse API.

    Les détails internes ne sont pas exposés pour les
    exceptions inconnues.
    """

    if isinstance(
        exception,
        HintAIError,
    ):

        return error_response(
            exception.message,

            code=exception.code,

            status_code=exception.status_code,

            details=exception.details,
        )

    return error_response(
        "Une erreur interne est survenue.",

        code="INTERNAL_ERROR",

        status_code=500,
    )


# ============================================================
# PAGINATION
# ============================================================

def pagination(
    *,
    page: Any = 1,
    limit: Any = 20,
    max_limit: int = 100,
) -> Dict[str, int]:
    """
    Normalise les paramètres de pagination.
    """

    page = clamp_int(
        page,
        1,
        1_000_000,
    )

    limit = clamp_int(
        limit,
        1,
        max_limit,
    )

    offset = (
        page - 1
    ) * limit

    return {
        "page":
            page,

        "limit":
            limit,

        "offset":
            offset,
    }


# ============================================================
# STREAMING
# ============================================================

def sse_event(
    data: Any,
    *,
    event: Optional[str] = None,
    event_id: Optional[str] = None,
) -> str:
    """
    Construit un événement Server-Sent Events.

    Format :

        event: token
        id: abc
        data: {"text":"Bonjour"}

    Le streaming IA pourra utiliser cette fonction.
    """

    lines = []

    if event:
        lines.append(
            f"event: {event}"
        )

    if event_id:
        lines.append(
            f"id: {event_id}"
        )

    payload = json_dumps(
        data,
        compact=True,
    )

    # SSE exige une ligne data.
    lines.append(
        f"data: {payload}"
    )

    return (
        "\n".join(
            lines
        )
        + "\n\n"
    )


def sse_comment(
    message: str,
) -> str:
    """
    Commentaire SSE.

    Utile pour garder une connexion active.
    """

    return (
        f": {message}\n\n"
    )


def sse_done() -> str:
    """
    Événement de fin du stream.
    """

    return sse_event(
        {
            "done": True,
        },
        event="done",
    )


def chunk_text(
    text: str,
    chunk_size: int = 80,
) -> Iterator[str]:
    """
    Découpe un texte en petits morceaux.

    Utilitaire de test uniquement.

    En production, les vrais tokens doivent provenir
    du flux Gemini.
    """

    if not text:
        return

    chunk_size = max(
        1,
        int(chunk_size),
    )

    for index in range(
        0,
        len(text),
        chunk_size,
    ):
        yield text[
            index:
            index + chunk_size
        ]


async def async_chunk_text(
    text: str,
    chunk_size: int = 80,
) -> AsyncGenerator[
    str,
    None,
]:
    """
    Version asynchrone du découpage.
    """

    for chunk in chunk_text(
        text,
        chunk_size,
    ):
        yield chunk


# ============================================================
# SÉCURITÉ DES ENTRÉES
# ============================================================

def sanitize_metadata(
    metadata: Any,
) -> Dict[str, Any]:
    """
    Nettoie les métadonnées avant stockage/logging.

    Les données trop volumineuses sont refusées.
    """

    if not isinstance(
        metadata,
        dict,
    ):
        return {}

    try:

        serialized = json_dumps(
            metadata
        )

    except Exception:
        return {}

    if len(
        serialized
    ) > MAX_METADATA_SIZE:

        return {}

    return metadata


def sanitize_url(
    url: Any,
) -> str:
    """
    Nettoyage basique d'une URL.

    Les vérifications métier/spécifiques seront effectuées
    par le module concerné.
    """

    if not url:
        return ""

    url = str(
        url
    ).strip()

    url = url.replace(
        "\x00",
        "",
    )

    return url[:2048]


# ============================================================
# NORMALISATION DES PLANS
# ============================================================

VALID_PLANS = {
    "free",
    "basic",
    "pro",
    "proplus",
    "super",
    "heavy",
}


def normalize_plan(
    plan: Any,
) -> str:
    """
    Normalise un nom de plan.

    Plans prévus :

        free
        basic
        pro
        proplus
        super
        heavy
    """

    if not plan:
        return "free"

    plan = str(
        plan
    ).strip().lower()

    aliases = {
        "pro_plus":
            "proplus",

        "pro-plus":
            "proplus",

        "pro plus":
            "proplus",
    }

    plan = aliases.get(
        plan,
        plan,
    )

    if plan not in VALID_PLANS:
        return "free"

    return plan


# ============================================================
# VALEURS NUMÉRIQUES SÛRES
# ============================================================

def safe_int(
    value: Any,
    default: int = 0,
) -> int:
    """
    Conversion robuste en entier.
    """

    try:

        return int(
            value
        )

    except (
        ValueError,
        TypeError,
    ):

        return default


def safe_float(
    value: Any,
    default: float = 0.0,
) -> float:
    """
    Conversion robuste en float.
    """

    try:

        return float(
            value
        )

    except (
        ValueError,
        TypeError,
    ):

        return default


def decimal_to_float(
    value: Any,
) -> Any:
    """
    Convertit Decimal en float lorsque nécessaire.
    """

    if isinstance(
        value,
        Decimal,
    ):
        return float(
            value
        )

    return value


# ============================================================
# LISTES
# ============================================================

def unique_list(
    values: Iterable[Any],
) -> list[Any]:
    """
    Supprime les doublons tout en conservant l'ordre.
    """

    result = []

    seen = set()

    for value in values:

        key = repr(
            value
        )

        if key in seen:
            continue

        seen.add(
            key
        )

        result.append(
            value
        )

    return result


def safe_list(
    value: Any,
) -> list[Any]:
    """
    Garantit une liste.
    """

    if isinstance(
        value,
        list,
    ):
        return value

    if isinstance(
        value,
        tuple,
    ):
        return list(
            value
        )

    return []


# ============================================================
# DEBUG
# ============================================================

def is_debug() -> bool:
    """
    Indique si le mode debug est activé.
    """

    return (
        os.getenv(
            "HINTAI_DEBUG",
            "false",
        ).lower()
        in {
            "1",
            "true",
            "yes",
            "on",
        }
    )


def environment() -> str:
    """
    Retourne l'environnement courant.
    """

    return os.getenv(
        "HINTAI_ENV",
        "development",
    ).lower()


def is_production() -> bool:
    """
    Indique si le backend tourne en production.
    """

    return environment() in {
        "production",
        "prod",
    }


# ============================================================
# EXPORTS
# ============================================================

__all__ = [
    # temps
    "utc_now",
    "timestamp",
    "timestamp_ms",
    "datetime_to_timestamp",
    "timestamp_to_datetime",
    "iso_now",
    "is_expired",

    # IDs
    "generate_id",
    "generate_token",
    "generate_numeric_code",

    # hash
    "sha256_bytes",
    "sha256_text",
    "hash_identifier",
    "secure_compare",

    # texte
    "normalize_whitespace",
    "clean_text",
    "clean_question",
    "clean_filename",
    "truncate_text",
    "text_length",

    # validation
    "is_valid_email",
    "normalize_email",
    "is_valid_uuid",
    "is_positive_int",
    "clamp",
    "clamp_int",

    # JSON
    "json_dumps",
    "json_loads",

    # dictionnaires
    "remove_none",
    "pick",
    "omit",
    "ensure_dict",

    # fichiers
    "bytes_to_mb",
    "mb_to_bytes",
    "validate_size",
    "is_supported_mime",
    "is_image_mime",
    "is_pdf_mime",

    # erreurs
    "HintAIError",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "RateLimitError",

    # API
    "success_response",
    "error_response",
    "exception_response",

    # pagination
    "pagination",

    # streaming
    "sse_event",
    "sse_comment",
    "sse_done",
    "chunk_text",
    "async_chunk_text",

    # sécurité
    "sanitize_metadata",
    "sanitize_url",

    # plans
    "VALID_PLANS",
    "normalize_plan",

    # nombres
    "safe_int",
    "safe_float",
    "decimal_to_float",

    # listes
    "unique_list",
    "safe_list",

    # environnement
    "is_debug",
    "environment",
    "is_production",
]
```
