```python
"""
HintAI — Authentication
=======================

Gestion de l'authentification utilisateur.

Responsabilités :
- création d'un compte
- connexion
- génération de tokens
- validation des tokens
- récupération de l'utilisateur courant
- gestion des utilisateurs anonymes
- préparation de la synchronisation avec le frontend

Important :
Ce fichier ne gère PAS :
- Gemini
- crédits
- paiements
- historique
- contrôle qualité

Ces responsabilités appartiennent aux autres modules.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import time
import uuid
from typing import Any, Dict, Optional


# ============================================================
# CONFIGURATION
# ============================================================

AUTH_SECRET = os.getenv(
    "HINTAI_AUTH_SECRET",
    "",
)

TOKEN_LIFETIME = int(
    os.getenv(
        "HINTAI_TOKEN_LIFETIME",
        str(60 * 60 * 24 * 7),
    )
)

REFRESH_TOKEN_LIFETIME = int(
    os.getenv(
        "HINTAI_REFRESH_TOKEN_LIFETIME",
        str(60 * 60 * 24 * 30),
    )
)


# ============================================================
# VALIDATION DE LA CONFIGURATION
# ============================================================

def ensure_auth_secret() -> str:
    """
    Vérifie que la clé secrète d'authentification existe.

    En production, elle DOIT être définie dans les variables
    d'environnement Vercel.
    """

    if not AUTH_SECRET:
        raise RuntimeError(
            "HINTAI_AUTH_SECRET n'est pas configurée."
        )

    return AUTH_SECRET


# ============================================================
# UTILITAIRES
# ============================================================

def hash_password(
    password: str,
) -> str:
    """
    Hash sécurisé du mot de passe.

    PBKDF2 est utilisé ici pour éviter de stocker les mots
    de passe en clair.

    Le format stocké est :

        salt$iterations$hash
    """

    if not password:
        raise ValueError(
            "Le mot de passe ne peut pas être vide."
        )

    salt = secrets.token_bytes(
        16
    )

    iterations = 310_000

    derived_key = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        iterations,
    )

    return (
        f"{salt.hex()}"
        f"${iterations}"
        f"${derived_key.hex()}"
    )


def verify_password(
    password: str,
    password_hash: str,
) -> bool:
    """
    Vérifie un mot de passe.
    """

    try:
        salt_hex, iterations, hash_hex = (
            password_hash.split(
                "$"
            )
        )

        salt = bytes.fromhex(
            salt_hex
        )

        expected = bytes.fromhex(
            hash_hex
        )

        actual = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            int(iterations),
        )

        return hmac.compare_digest(
            actual,
            expected,
        )

    except (
        ValueError,
        TypeError,
    ):
        return False


# ============================================================
# TOKENS
# ============================================================

def _sign_token(
    payload: str,
) -> str:
    """
    Signature HMAC du payload.
    """

    secret = ensure_auth_secret()

    signature = hmac.new(
        secret.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return signature


def create_access_token(
    user_id: str,
) -> str:
    """
    Crée un token d'accès signé.

    Format interne :

        user_id.timestamp.random.signature
    """

    timestamp = int(
        time.time()
    )

    nonce = secrets.token_urlsafe(
        16
    )

    payload = (
        f"{user_id}."
        f"{timestamp}."
        f"{nonce}"
    )

    signature = _sign_token(
        payload
    )

    return (
        f"{payload}."
        f"{signature}"
    )


def create_refresh_token(
    user_id: str,
) -> str:
    """
    Crée un refresh token.

    Il est volontairement distinct du token d'accès.
    """

    timestamp = int(
        time.time()
    )

    nonce = secrets.token_urlsafe(
        32
    )

    payload = (
        f"{user_id}."
        f"{timestamp}."
        f"{nonce}"
    )

    signature = _sign_token(
        payload
    )

    return (
        f"{payload}."
        f"{signature}"
    )


def _parse_token(
    token: str,
) -> Optional[Dict[str, Any]]:
    """
    Vérifie la signature et extrait le contenu d'un token.
    """

    if not token:
        return None

    parts = token.split(
        "."
    )

    if len(parts) != 4:
        return None

    user_id = parts[0]
    timestamp_raw = parts[1]
    nonce = parts[2]
    signature = parts[3]

    payload = (
        f"{user_id}."
        f"{timestamp_raw}."
        f"{nonce}"
    )

    expected_signature = _sign_token(
        payload
    )

    if not hmac.compare_digest(
        signature,
        expected_signature,
    ):
        return None

    try:
        timestamp = int(
            timestamp_raw
        )
    except ValueError:
        return None

    return {
        "user_id": user_id,
        "timestamp": timestamp,
        "nonce": nonce,
    }


def verify_access_token(
    token: str,
) -> Optional[str]:
    """
    Vérifie un access token et retourne l'user_id.
    """

    payload = _parse_token(
        token
    )

    if payload is None:
        return None

    age = (
        int(time.time())
        - payload["timestamp"]
    )

    if age < 0:
        return None

    if age > TOKEN_LIFETIME:
        return None

    return payload[
        "user_id"
    ]


def verify_refresh_token(
    token: str,
) -> Optional[str]:
    """
    Vérifie un refresh token.
    """

    payload = _parse_token(
        token
    )

    if payload is None:
        return None

    age = (
        int(time.time())
        - payload["timestamp"]
    )

    if age < 0:
        return None

    if age > REFRESH_TOKEN_LIFETIME:
        return None

    return payload[
        "user_id"
    ]


# ============================================================
# IDENTIFIANT ANONYME
# ============================================================

def create_anonymous_id() -> str:
    """
    Génère un identifiant anonyme pour un utilisateur
    qui n'est pas encore connecté.
    """

    return (
        "anon_"
        + secrets.token_urlsafe(
            24
        )
    )


def validate_anonymous_id(
    anonymous_id: str,
) -> bool:
    """
    Vérification basique d'un identifiant anonyme.
    """

    if not anonymous_id:
        return False

    if len(anonymous_id) > 128:
        return False

    return anonymous_id.startswith(
        "anon_"
    )


# ============================================================
# VALIDATION EMAIL
# ============================================================

def normalize_email(
    email: str,
) -> str:
    """
    Normalise une adresse email.
    """

    return (
        email
        .strip()
        .lower()
    )


def is_valid_email(
    email: str,
) -> bool:
    """
    Validation simple d'email.

    La validation finale pourra être renforcée
    lors de l'inscription.
    """

    email = normalize_email(
        email
    )

    if not email:
        return False

    if len(email) > 320:
        return False

    if "@" not in email:
        return False

    local, domain = email.split(
        "@",
        1,
    )

    if not local or not domain:
        return False

    if "." not in domain:
        return False

    return True


# ============================================================
# VALIDATION MOT DE PASSE
# ============================================================

def validate_password(
    password: str,
) -> Optional[str]:
    """
    Retourne une erreur si le mot de passe est insuffisant.

    Retourne None si tout est correct.
    """

    if len(password) < 8:
        return (
            "Le mot de passe doit contenir "
            "au moins 8 caractères."
        )

    if len(password) > 256:
        return (
            "Le mot de passe est trop long."
        )

    if not any(
        character.isupper()
        for character in password
    ):
        return (
            "Le mot de passe doit contenir "
            "au moins une majuscule."
        )

    if not any(
        character.islower()
        for character in password
    ):
        return (
            "Le mot de passe doit contenir "
            "au moins une minuscule."
        )

    if not any(
        character.isdigit()
        for character in password
    ):
        return (
            "Le mot de passe doit contenir "
            "au moins un chiffre."
        )

    return None


# ============================================================
# UTILISATEUR
# ============================================================

def create_user_record(
    email: str,
    password: str,
    name: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Prépare un nouvel utilisateur.

    Le stockage réel sera branché dans storage.py.
    """

    email = normalize_email(
        email
    )

    password_error = validate_password(
        password
    )

    if password_error:
        raise ValueError(
            password_error
        )

    if not is_valid_email(
        email
    ):
        raise ValueError(
            "Adresse email invalide."
        )

    user_id = str(
        uuid.uuid4()
    )

    return {
        "id": user_id,

        "email": email,

        "name": (
            name.strip()
            if name
            else None
        ),

        "password_hash":
            hash_password(
                password
            ),

        "plan": "free",

        "created_at": int(
            time.time()
        ),

        "email_verified": False,

        "active": True,
    }


# ============================================================
# SESSION
# ============================================================

def create_session(
    user_id: str,
) -> Dict[str, str]:
    """
    Crée une session utilisateur.
    """

    return {
        "accessToken":
            create_access_token(
                user_id
            ),

        "refreshToken":
            create_refresh_token(
                user_id
            ),
    }


def get_public_user(
    user: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Retire les informations sensibles avant d'envoyer
    l'utilisateur au frontend.

    Le password_hash ne doit JAMAIS être envoyé à Expo.
    """

    return {
        "id": user.get(
            "id"
        ),

        "email": user.get(
            "email"
        ),

        "name": user.get(
            "name"
        ),

        "plan": user.get(
            "plan",
            "free",
        ),

        "createdAt": user.get(
            "created_at"
        ),

        "emailVerified": user.get(
            "email_verified",
            False,
        ),
    }


# ============================================================
# AUTHENTIFICATION REQUEST
# ============================================================

def authenticate_token(
    token: Optional[str],
) -> Optional[str]:
    """
    Fonction centrale utilisée par api.py.

    Retourne :
        user_id

    ou :
        None
    """

    if not token:
        return None

    return verify_access_token(
        token
    )


def authenticate_anonymous(
    anonymous_id: Optional[str],
) -> Optional[str]:
    """
    Valide un utilisateur anonyme.
    """

    if not anonymous_id:
        return None

    if not validate_anonymous_id(
        anonymous_id
    ):
        return None

    return anonymous_id


# ============================================================
# AUTHENTICATION CONTEXT
# ============================================================

def get_auth_context(
    token: Optional[str] = None,
    anonymous_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Détermine le contexte d'authentification.

    Priorité :

        utilisateur connecté
              ↓
        utilisateur anonyme
              ↓
        aucune identité
    """

    user_id = authenticate_token(
        token
    )

    if user_id:
        return {
            "authenticated": True,
            "anonymous": False,
            "user_id": user_id,
            "anonymous_id": None,
        }

    valid_anonymous_id = (
        authenticate_anonymous(
            anonymous_id
        )
    )

    if valid_anonymous_id:
        return {
            "authenticated": False,
            "anonymous": True,
            "user_id": None,
            "anonymous_id":
                valid_anonymous_id,
        }

    return {
        "authenticated": False,
        "anonymous": False,
        "user_id": None,
        "anonymous_id": None,
    }


# ============================================================
# LOGOUT / REVOCATION
# ============================================================

"""
Les tokens sont signés côté serveur.

Pour une vraie révocation immédiate, storage.py pourra
maintenir une liste de sessions/token IDs révoqués.

On garde cette responsabilité hors de ce fichier afin
d'éviter de mettre un stockage mutable dans Vercel.
"""


def logout_token(
    token: str,
) -> bool:
    """
    Point d'entrée pour la révocation.

    La révocation persistante sera branchée avec storage.py.
    """

    user_id = verify_access_token(
        token
    )

    return user_id is not None


# ============================================================
# SÉCURITÉ
# ============================================================

def constant_time_compare(
    first: str,
    second: str,
) -> bool:
    """
    Comparaison résistante aux attaques temporelles.
    """

    return hmac.compare_digest(
        first,
        second,
    )
```
