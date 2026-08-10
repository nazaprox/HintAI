```python
"""
HintAI — Storage Layer
======================

Couche de persistance de HintAI.

Objectif :
    Isoler complètement le backend de la technologie
    de stockage utilisée en production.

Architecture :

    api.py
      │
      ├── auth.py
      ├── credits.py
      ├── quality.py
      ├── ai.py
      │
      ▼
    storage.py
      │
      ▼
    Base de données / stockage persistant

IMPORTANT POUR VERCEL :

Le filesystem local d'une fonction serverless ne doit PAS
être utilisé comme base de données permanente.

Ce fichier fournit donc une interface unique.

Le reste du backend ne doit jamais faire directement :

    open("users.json", "w")

ou compter sur un fichier local persistant.

En production, DATABASE_URL / les variables de connexion
seront utilisées pour brancher la vraie base.

Ce module contient :

- utilisateurs
- sessions
- crédits
- historique
- conversations
- documents
- exercices
- détection de doublons
- événements d'utilisation
- abonnement
"""

from __future__ import annotations

import hashlib
import os
import threading
import time
import uuid
from copy import deepcopy
from typing import Any, Dict, List, Optional


# ============================================================
# CONFIGURATION
# ============================================================

STORAGE_MODE = os.getenv(
    "HINTAI_STORAGE_MODE",
    "memory",
).lower()

MAX_HISTORY_ITEMS = int(
    os.getenv(
        "HINTAI_MAX_HISTORY_ITEMS",
        "100",
    )
)

MAX_DOCUMENTS_PER_USER = int(
    os.getenv(
        "HINTAI_MAX_DOCUMENTS_PER_USER",
        "500",
    )
)


# ============================================================
# MÉMOIRE DE DÉVELOPPEMENT
# ============================================================

_MEMORY_USERS: Dict[
    str,
    Dict[str, Any]
] = {}

_MEMORY_SESSIONS: Dict[
    str,
    Dict[str, Any]
] = {}

_MEMORY_CREDITS: Dict[
    str,
    Dict[str, Any]
] = {}

_MEMORY_HISTORY: Dict[
    str,
    List[Dict[str, Any]]
] = {}

_MEMORY_DOCUMENTS: Dict[
    str,
    Dict[str, Any]
] = {}

_MEMORY_USAGE: List[
    Dict[str, Any]
] = []

_MEMORY_LOCK = threading.RLock()


# ============================================================
# UTILITAIRES
# ============================================================

def now() -> int:
    """
    Timestamp UTC.
    """

    return int(
        time.time()
    )


def generate_id(
    prefix: str = "",
) -> str:
    """
    Génère un identifiant unique.
    """

    value = uuid.uuid4().hex

    if prefix:
        return f"{prefix}_{value}"

    return value


def clone(
    value: Any,
) -> Any:
    """
    Copie défensive des objets stockés.
    """

    return deepcopy(
        value
    )


def hash_value(
    value: str,
) -> str:
    """
    SHA-256 d'une valeur.
    """

    return hashlib.sha256(
        value.encode(
            "utf-8"
        )
    ).hexdigest()


# ============================================================
# UTILISATEURS
# ============================================================

def create_user(
    *,
    email: Optional[str] = None,
    name: Optional[str] = None,
    provider: str = "email",
    provider_user_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Crée un utilisateur.

    Le mot de passe ne doit jamais être stocké ici.

    auth.py sera responsable de l'authentification.
    """

    user_id = generate_id(
        "usr"
    )

    timestamp = now()

    user = {
        "id": user_id,

        "email": email,

        "name": name,

        "provider":
            provider,

        "providerUserId":
            provider_user_id,

        "plan":
            "free",

        "subscriptionStatus":
            "active",

        "createdAt":
            timestamp,

        "updatedAt":
            timestamp,

        "lastSeenAt":
            timestamp,

        "settings": {
            "language": "fr",

            "theme": "system",

            "notifications": True,
        },
    }

    with _MEMORY_LOCK:

        _MEMORY_USERS[
            user_id
        ] = clone(
            user
        )

    return clone(
        user
    )


def get_user(
    user_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Récupère un utilisateur.
    """

    with _MEMORY_LOCK:

        user = _MEMORY_USERS.get(
            user_id
        )

        if user is None:
            return None

        return clone(
            user
        )


def get_user_by_email(
    email: str,
) -> Optional[Dict[str, Any]]:
    """
    Recherche un utilisateur par email.
    """

    normalized = email.strip().lower()

    with _MEMORY_LOCK:

        for user in _MEMORY_USERS.values():

            current = (
                user.get(
                    "email"
                )
                or ""
            ).lower()

            if current == normalized:

                return clone(
                    user
                )

    return None


def update_user(
    user_id: str,
    updates: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Met à jour un utilisateur.

    Certains champs sensibles sont protégés.
    """

    protected = {
        "id",
        "createdAt",
    }

    safe_updates = {
        key: value
        for key, value in updates.items()
        if key not in protected
    }

    with _MEMORY_LOCK:

        user = _MEMORY_USERS.get(
            user_id
        )

        if user is None:
            return None

        user.update(
            safe_updates
        )

        user[
            "updatedAt"
        ] = now()

        _MEMORY_USERS[
            user_id
        ] = user

        return clone(
            user
        )


def touch_user(
    user_id: str,
) -> None:
    """
    Met à jour la dernière activité.
    """

    with _MEMORY_LOCK:

        user = _MEMORY_USERS.get(
            user_id
        )

        if user is None:
            return

        user[
            "lastSeenAt"
        ] = now()

        user[
            "updatedAt"
        ] = now()


# ============================================================
# SESSIONS
# ============================================================

def create_session(
    user_id: str,
    *,
    expires_at: Optional[int] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Crée une session serveur.

    Le token réel sera généré/validé par auth.py.
    """

    session_id = generate_id(
        "ses"
    )

    session = {
        "id":
            session_id,

        "userId":
            user_id,

        "createdAt":
            now(),

        "expiresAt":
            expires_at,

        "revoked":
            False,

        "metadata":
            metadata or {},
    }

    with _MEMORY_LOCK:

        _MEMORY_SESSIONS[
            session_id
        ] = clone(
            session
        )

    return clone(
        session
    )


def get_session(
    session_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Récupère une session.
    """

    with _MEMORY_LOCK:

        session = _MEMORY_SESSIONS.get(
            session_id
        )

        if session is None:
            return None

        if session.get(
            "revoked",
            False,
        ):
            return None

        expires_at = session.get(
            "expiresAt"
        )

        if (
            expires_at is not None
            and expires_at <= now()
        ):
            return None

        return clone(
            session
        )


def revoke_session(
    session_id: str,
) -> bool:
    """
    Révoque une session.
    """

    with _MEMORY_LOCK:

        session = _MEMORY_SESSIONS.get(
            session_id
        )

        if session is None:
            return False

        session[
            "revoked"
        ] = True

        session[
            "revokedAt"
        ] = now()

        return True


def revoke_user_sessions(
    user_id: str,
) -> int:
    """
    Révoque toutes les sessions d'un utilisateur.
    """

    count = 0

    with _MEMORY_LOCK:

        for session in _MEMORY_SESSIONS.values():

            if (
                session.get(
                    "userId"
                )
                == user_id
                and not session.get(
                    "revoked",
                    False,
                )
            ):

                session[
                    "revoked"
                ] = True

                session[
                    "revokedAt"
                ] = now()

                count += 1

    return count


# ============================================================
# CRÉDITS
# ============================================================

def create_credit_account(
    user_id: str,
    account: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Enregistre le compte de crédits.
    """

    with _MEMORY_LOCK:

        _MEMORY_CREDITS[
            user_id
        ] = clone(
            account
        )

        return clone(
            _MEMORY_CREDITS[
                user_id
            ]
        )


def get_credit_account(
    user_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Récupère le compte de crédits.
    """

    with _MEMORY_LOCK:

        account = _MEMORY_CREDITS.get(
            user_id
        )

        if account is None:
            return None

        return clone(
            account
        )


def update_credit_account(
    user_id: str,
    updates: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Mise à jour du compte de crédits.
    """

    with _MEMORY_LOCK:

        account = _MEMORY_CREDITS.get(
            user_id
        )

        if account is None:
            return None

        account.update(
            clone(
                updates
            )
        )

        account[
            "updatedAt"
        ] = now()

        return clone(
            account
        )


def atomic_credit_operation(
    user_id: str,
    operation,
) -> Dict[str, Any]:
    """
    Exécute une opération de crédit sous verrou.

    operation(account) doit :
        - retourner le compte modifié
        - lever une exception si l'opération échoue

    En production, cette logique devra être remplacée
    par une transaction atomique de base de données.
    """

    with _MEMORY_LOCK:

        account = _MEMORY_CREDITS.get(
            user_id
        )

        if account is None:
            raise RuntimeError(
                "Compte de crédits introuvable."
            )

        updated = operation(
            clone(
                account
            )
        )

        if not isinstance(
            updated,
            dict,
        ):
            raise RuntimeError(
                "Opération de crédit invalide."
            )

        updated[
            "updatedAt"
        ] = now()

        _MEMORY_CREDITS[
            user_id
        ] = clone(
            updated
        )

        return clone(
            updated
        )


# ============================================================
# HISTORIQUE
# ============================================================

def add_history(
    user_id: str,
    item: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Ajoute un élément à l'historique.

    L'historique serveur est séparé du localStorage Expo.

    Le localStorage permettra un accès rapide côté appareil,
    tandis que cette couche permet la synchronisation.
    """

    history_id = generate_id(
        "hist"
    )

    entry = {
        "id":
            history_id,

        "userId":
            user_id,

        "createdAt":
            now(),

        **clone(
            item
        ),
    }

    with _MEMORY_LOCK:

        history = _MEMORY_HISTORY.setdefault(
            user_id,
            [],
        )

        history.insert(
            0,
            clone(
                entry
            ),
        )

        if len(history) > (
            MAX_HISTORY_ITEMS
        ):
            del history[
                MAX_HISTORY_ITEMS:
            ]

    return clone(
        entry
    )


def get_history(
    user_id: str,
    *,
    limit: int = 50,
    offset: int = 0,
) -> List[Dict[str, Any]]:
    """
    Retourne l'historique paginé.
    """

    limit = max(
        1,
        min(
            limit,
            MAX_HISTORY_ITEMS,
        ),
    )

    offset = max(
        0,
        offset,
    )

    with _MEMORY_LOCK:

        history = _MEMORY_HISTORY.get(
            user_id,
            [],
        )

        return clone(
            history[
                offset:
                offset + limit
            ]
        )


def delete_history_item(
    user_id: str,
    history_id: str,
) -> bool:
    """
    Supprime une entrée d'historique.
    """

    with _MEMORY_LOCK:

        history = _MEMORY_HISTORY.get(
            user_id,
            [],
        )

        for index, item in enumerate(
            history
        ):

            if item.get(
                "id"
            ) == history_id:

                del history[
                    index
                ]

                return True

    return False


def clear_history(
    user_id: str,
) -> int:
    """
    Supprime tout l'historique serveur.
    """

    with _MEMORY_LOCK:

        history = _MEMORY_HISTORY.get(
            user_id,
            [],
        )

        count = len(
            history
        )

        _MEMORY_HISTORY[
            user_id
        ] = []

        return count


# ============================================================
# CONVERSATIONS
# ============================================================

def create_conversation(
    user_id: str,
    *,
    mode: str,
    title: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Crée une conversation.

    Une conversation sera représentée dans l'historique.
    """

    conversation_id = generate_id(
        "conv"
    )

    conversation = {
        "id":
            conversation_id,

        "userId":
            user_id,

        "mode":
            mode,

        "title":
            title,

        "createdAt":
            now(),

        "updatedAt":
            now(),

        "messages":
            [],
    }

    add_history(
        user_id,
        {
            "type":
                "conversation",

            "conversationId":
                conversation_id,

            "mode":
                mode,

            "title":
                title,
        },
    )

    return conversation


# ============================================================
# DOCUMENTS / BIBLIOTHÈQUE
# ============================================================

def create_document(
    user_id: str,
    *,
    filename: str,
    mime_type: str,
    sha256: str,
    perceptual_hash: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Enregistre un document dans la bibliothèque.

    Le fichier binaire lui-même ne doit pas être conservé
    dans le filesystem temporaire de Vercel.

    En production :
        objet storage
        +
        métadonnées DB
    """

    existing = find_document_by_sha256(
        sha256
    )

    if existing is not None:

        raise ValueError(
            "Document déjà présent."
        )

    # Limite utilisateur.
    if count_user_documents(
        user_id
    ) >= MAX_DOCUMENTS_PER_USER:

        raise RuntimeError(
            "Limite de documents atteinte."
        )

    document_id = generate_id(
        "doc"
    )

    document = {
        "id":
            document_id,

        "userId":
            user_id,

        "filename":
            filename,

        "mimeType":
            mime_type,

        "sha256":
            sha256,

        "perceptualHash":
            perceptual_hash,

        "metadata":
            metadata or {},

        "status":
            "pending",

        "createdAt":
            now(),

        "updatedAt":
            now(),
    }

    with _MEMORY_LOCK:

        _MEMORY_DOCUMENTS[
            document_id
        ] = clone(
            document
        )

    return clone(
        document
    )


def get_document(
    document_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Récupère un document.
    """

    with _MEMORY_LOCK:

        document = _MEMORY_DOCUMENTS.get(
            document_id
        )

        if document is None:
            return None

        return clone(
            document
        )


def update_document(
    document_id: str,
    updates: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """
    Met à jour les métadonnées d'un document.
    """

    with _MEMORY_LOCK:

        document = _MEMORY_DOCUMENTS.get(
            document_id
        )

        if document is None:
            return None

        document.update(
            clone(
                updates
            )
        )

        document[
            "updatedAt"
        ] = now()

        return clone(
            document
        )


def list_user_documents(
    user_id: str,
    *,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Liste les documents d'un utilisateur.
    """

    limit = max(
        1,
        min(
            limit,
            MAX_DOCUMENTS_PER_USER,
        ),
    )

    with _MEMORY_LOCK:

        documents = [
            document
            for document
            in _MEMORY_DOCUMENTS.values()
            if document.get(
                "userId"
            ) == user_id
        ]

        documents.sort(
            key=lambda item:
                item.get(
                    "createdAt",
                    0,
                ),
            reverse=True,
        )

        return clone(
            documents[
                :limit
            ]
        )


def count_user_documents(
    user_id: str,
) -> int:
    """
    Nombre de documents utilisateur.
    """

    with _MEMORY_LOCK:

        return sum(
            1
            for document
            in _MEMORY_DOCUMENTS.values()
            if document.get(
                "userId"
            ) == user_id
        )


def find_document_by_sha256(
    sha256: str,
) -> Optional[Dict[str, Any]]:
    """
    Recherche exacte d'un document.
    """

    with _MEMORY_LOCK:

        for document in (
            _MEMORY_DOCUMENTS.values()
        ):

            if document.get(
                "sha256"
            ) == sha256:

                return clone(
                    document
                )

    return None


def find_similar_documents(
    perceptual_hash: str,
    *,
    threshold: int = 12,
) -> List[Dict[str, Any]]:
    """
    Recherche les documents potentiellement similaires.

    La distance perceptuelle réelle est calculée dans
    quality.py.

    Pour garder storage.py indépendant, on compare ici
    simplement les hashes compatibles.
    """

    if not perceptual_hash:
        return []

    results = []

    try:

        target = int(
            perceptual_hash,
            16,
        )

    except ValueError:

        return []

    with _MEMORY_LOCK:

        for document in (
            _MEMORY_DOCUMENTS.values()
        ):

            candidate_hash = document.get(
                "perceptualHash"
            )

            if not candidate_hash:
                continue

            try:

                candidate = int(
                    candidate_hash,
                    16,
                )

            except ValueError:
                continue

            distance = (
                target
                ^ candidate
            ).bit_count()

            if distance <= threshold:

                result = clone(
                    document
                )

                result[
                    "similarityDistance"
                ] = distance

                results.append(
                    result
                )

    results.sort(
        key=lambda item:
            item.get(
                "similarityDistance",
                999999,
            )
    )

    return results


# ============================================================
# ÉVÉNEMENTS D'UTILISATION
# ============================================================

def record_usage(
    user_id: str,
    *,
    operation: str,
    success: bool,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Enregistre une opération.

    Ces événements serviront pour :
    - anti-abus
    - analytics
    - quotas
    - facturation
    - debugging
    """

    event = {
        "id":
            generate_id(
                "evt"
            ),

        "userId":
            user_id,

        "operation":
            operation,

        "success":
            bool(
                success
            ),

        "timestamp":
            now(),

        "metadata":
            metadata or {},
    }

    with _MEMORY_LOCK:

        _MEMORY_USAGE.append(
            clone(
                event
            )
        )

        # On garde une fenêtre mémoire limitée.
        if len(
            _MEMORY_USAGE
        ) > 10000:

            del _MEMORY_USAGE[
                :5000
            ]

    return clone(
        event
    )


def count_recent_usage(
    user_id: str,
    *,
    seconds: int = 60,
    operation: Optional[str] = None,
) -> int:
    """
    Compte les opérations récentes.

    Utilisé par l'anti-abus.
    """

    minimum_timestamp = (
        now()
        - seconds
    )

    count = 0

    with _MEMORY_LOCK:

        for event in _MEMORY_USAGE:

            if event.get(
                "userId"
            ) != user_id:
                continue

            if event.get(
                "timestamp",
                0,
            ) < minimum_timestamp:
                continue

            if (
                operation is not None
                and event.get(
                    "operation"
                ) != operation
            ):
                continue

            count += 1

    return count


# ============================================================
# REWARDED ADS
# ============================================================

def record_rewarded_ad(
    user_id: str,
    *,
    provider: str,
    reward_id: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Enregistre un reward publicitaire validé.

    reward_id doit provenir du système publicitaire,
    pas du frontend seul.
    """

    event = {
        "id":
            generate_id(
                "reward"
            ),

        "userId":
            user_id,

        "provider":
            provider,

        "rewardId":
            reward_id,

        "createdAt":
            now(),

        "metadata":
            metadata or {},
    }

    record_usage(
        user_id,
        operation="rewarded_ad",
        success=True,
        metadata=event,
    )

    return event


def reward_already_processed(
    reward_id: str,
) -> bool:
    """
    Empêche le traitement deux fois du même reward.
    """

    with _MEMORY_LOCK:

        for event in _MEMORY_USAGE:

            if event.get(
                "operation"
            ) != "rewarded_ad":
                continue

            metadata = event.get(
                "metadata",
                {},
            )

            if metadata.get(
                "rewardId"
            ) == reward_id:

                return True

    return False


# ============================================================
# ABONNEMENTS
# ============================================================

def set_subscription(
    user_id: str,
    *,
    plan: str,
    status: str,
    provider: Optional[str] = None,
    provider_subscription_id: Optional[str] = None,
    current_period_end: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    """
    Met à jour l'abonnement d'un utilisateur.

    La validation du paiement sera effectuée par le module
    d'authentification/paiement.

    Ne jamais faire confiance au frontend pour changer
    directement le plan.
    """

    user = get_user(
        user_id
    )

    if user is None:
        return None

    updates = {
        "plan":
            plan,

        "subscriptionStatus":
            status,

        "subscriptionProvider":
            provider,

        "providerSubscriptionId":
            provider_subscription_id,

        "currentPeriodEnd":
            current_period_end,

        "updatedAt":
            now(),
    }

    return update_user(
        user_id,
        updates,
    )


def get_subscription(
    user_id: str,
) -> Optional[Dict[str, Any]]:
    """
    Retourne les informations d'abonnement.
    """

    user = get_user(
        user_id
    )

    if user is None:
        return None

    return {
        "plan":
            user.get(
                "plan",
                "free",
            ),

        "status":
            user.get(
                "subscriptionStatus",
                "active",
            ),

        "provider":
            user.get(
                "subscriptionProvider"
            ),

        "providerSubscriptionId":
            user.get(
                "providerSubscriptionId"
            ),

        "currentPeriodEnd":
            user.get(
                "currentPeriodEnd"
            ),
    }


# ============================================================
# STATISTIQUES
# ============================================================

def get_user_statistics(
    user_id: str,
) -> Dict[str, Any]:
    """
    Statistiques simples d'un utilisateur.
    """

    history_count = len(
        get_history(
            user_id,
            limit=MAX_HISTORY_ITEMS,
        )
    )

    document_count = (
        count_user_documents(
            user_id
        )
    )

    recent_operations = (
        count_recent_usage(
            user_id,
            seconds=86400,
        )
    )

    return {
        "historyCount":
            history_count,

        "documentCount":
            document_count,

        "operationsLast24Hours":
            recent_operations,
    }


# ============================================================
# HEALTH CHECK
# ============================================================

def health_check() -> Dict[str, Any]:
    """
    Vérification de l'état du storage.
    """

    with _MEMORY_LOCK:

        return {
            "status":
                "ok",

            "mode":
                STORAGE_MODE,

            "users":
                len(
                    _MEMORY_USERS
                ),

            "sessions":
                len(
                    _MEMORY_SESSIONS
                ),

            "documents":
                len(
                    _MEMORY_DOCUMENTS
                ),

            "usageEvents":
                len(
                    _MEMORY_USAGE
                ),
        }


# ============================================================
# RESET DEV
# ============================================================

def clear_memory_storage() -> None:
    """
    Vide le stockage mémoire.

    UNIQUEMENT pour les tests/dev.

    Ne doit jamais être exposé dans une route publique.
    """

    with _MEMORY_LOCK:

        _MEMORY_USERS.clear()

        _MEMORY_SESSIONS.clear()

        _MEMORY_CREDITS.clear()

        _MEMORY_HISTORY.clear()

        _MEMORY_DOCUMENTS.clear()

        _MEMORY_USAGE.clear()


# ============================================================
# INFORMATION DE CONFIGURATION
# ============================================================

def storage_info() -> Dict[str, Any]:
    """
    Informations non sensibles sur le stockage.
    """

    return {
        "mode":
            STORAGE_MODE,

        "persistent":
            STORAGE_MODE not in {
                "memory",
                "test",
            },

        "maxHistoryItems":
            MAX_HISTORY_ITEMS,

        "maxDocumentsPerUser":
            MAX_DOCUMENTS_PER_USER,
    }
```
