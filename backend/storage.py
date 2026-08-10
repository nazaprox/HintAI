"""
HintAI — Storage
================

Couche de stockage de HintAI.

Responsabilités :

* utilisateurs ;
* sessions ;
* crédits ;
* séries ;
* historique ;
* réponses ;
* données persistantes.

IMPORTANT :
La logique métier n'est pas placée ici.

Ce fichier fournit une couche d'accès aux données afin que
le reste de l'application ne dépende pas directement
du système de stockage utilisé.

Vercel :
Le stockage local du système de fichiers n'est pas considéré
comme persistant en production.

La fonction peut donc fonctionner avec un stockage local
pour le développement, puis être branchée sur une base
persistante sans modifier le reste de l'application.
"""

from **future** import annotations

import json
import os
import threading
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# ============================================================

# CONFIGURATION

# ============================================================

APP_ROOT = Path(
os.getenv(
"HINTAI_STORAGE_DIR",
"db",
)
)

LOCAL_DB_FILE = APP_ROOT / "hintai.json"

_storage_lock = threading.Lock()

# ============================================================

# UTILITAIRES

# ============================================================

def utc_now() -> str:
"""
Retourne la date UTC au format ISO.
"""

```
return datetime.now(
    timezone.utc
).isoformat()
```

def generate_id(
prefix: str = "",
) -> str:
"""
Génère un identifiant unique.
"""

```
value = str(uuid.uuid4())

if prefix:
    return f"{prefix}_{value}"

return value
```

def ensure_storage() -> None:
"""
Prépare le dossier de stockage local.
"""

```
APP_ROOT.mkdir(
    parents=True,
    exist_ok=True,
)
```

# ============================================================

# STRUCTURE DE LA BASE LOCALE

# ============================================================

def empty_database() -> Dict[str, Any]:
"""
Structure initiale de la base.
"""

```
return {
    "users": {},
    "sessions": {},
    "history": {},
    "responses": {},
    "streaks": {},
    "rewarded_ads": {},
    "credit_transactions": {},
}
```

def load_database() -> Dict[str, Any]:
"""
Charge la base locale.

```
Utilisée principalement pour le développement.

En production Vercel, cette fonction ne doit pas être
considérée comme une base persistante.
"""

ensure_storage()

if not LOCAL_DB_FILE.exists():
    return empty_database()

try:
    with LOCAL_DB_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    if not isinstance(data, dict):
        return empty_database()

    database = empty_database()

    for key in database:
        if isinstance(
            data.get(key),
            dict,
        ):
            database[key] = data[key]

    return database

except (
    OSError,
    json.JSONDecodeError,
):
    return empty_database()
```

def save_database(
database: Dict[str, Any],
) -> None:
"""
Sauvegarde la base locale.

```
Écriture atomique pour éviter de laisser un fichier
partiellement écrit en cas d'erreur.
"""

ensure_storage()

temporary_file = LOCAL_DB_FILE.with_suffix(
    ".tmp"
)

with temporary_file.open(
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        database,
        file,
        ensure_ascii=False,
        indent=2,
    )

temporary_file.replace(
    LOCAL_DB_FILE
)
```

def update_database(
callback,
) -> Any:
"""
Charge, modifie puis sauvegarde la base sous verrou.
"""

```
with _storage_lock:

    database = load_database()

    result = callback(
        database
    )

    save_database(
        database
    )

    return result
```

# ============================================================

# UTILISATEURS

# ============================================================

def get_user(
user_id: str,
) -> Optional[Dict[str, Any]]:
"""
Récupère un utilisateur.
"""

```
database = load_database()

user = database[
    "users"
].get(user_id)

if user is None:
    return None

return deepcopy(user)
```

def create_user(
*,
user_id: Optional[str] = None,
email: Optional[str] = None,
plan: str = "free",
) -> Dict[str, Any]:
"""
Crée un utilisateur.
"""

```
uid = user_id or generate_id(
    "usr"
)

now = utc_now()

user = {
    "id": uid,
    "email": email,
    "plan": plan,
    "createdAt": now,
    "updatedAt": now,
    "active": True,
}

def operation(
    database,
):
    database[
        "users"
    ][uid] = user

    return deepcopy(user)

return update_database(
    operation
)
```

def update_user(
user_id: str,
updates: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
"""
Met à jour un utilisateur.
"""

```
def operation(
    database,
):

    user = database[
        "users"
    ].get(user_id)

    if user is None:
        return None

    user.update(
        updates
    )

    user[
        "updatedAt"
    ] = utc_now()

    return deepcopy(user)

return update_database(
    operation
)
```

# ============================================================

# SESSIONS

# ============================================================

def create_session(
user_id: str,
*,
session_type: str,
) -> Dict[str, Any]:
"""
Crée une session Help Me ou Learn a Concept.
"""

```
session_id = generate_id(
    "ses"
)

session = {
    "id": session_id,
    "userId": user_id,
    "type": session_type,
    "createdAt": utc_now(),
    "updatedAt": utc_now(),
    "status": "active",
}

def operation(
    database,
):

    database[
        "sessions"
    ][session_id] = session

    return deepcopy(session)

return update_database(
    operation
)
```

def get_session(
session_id: str,
) -> Optional[Dict[str, Any]]:
"""
Récupère une session.
"""

```
database = load_database()

session = database[
    "sessions"
].get(session_id)

if session is None:
    return None

return deepcopy(session)
```

def update_session(
session_id: str,
updates: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
"""
Met à jour une session.
"""

```
def operation(
    database,
):

    session = database[
        "sessions"
    ].get(session_id)

    if session is None:
        return None

    session.update(
        updates
    )

    session[
        "updatedAt"
    ] = utc_now()

    return deepcopy(session)

return update_database(
    operation
)
```

# ============================================================

# HISTORIQUE

# ============================================================

def save_history(
user_id: str,
*,
session_id: Optional[str],
mode: str,
title: str,
content: Dict[str, Any],
) -> Dict[str, Any]:
"""
Sauvegarde une entrée d'historique.
"""

```
history_id = generate_id(
    "hist"
)

item = {
    "id": history_id,
    "userId": user_id,
    "sessionId": session_id,
    "mode": mode,
    "title": title,
    "content": content,
    "createdAt": utc_now(),
}

def operation(
    database,
):

    database[
        "history"
    ][history_id] = item

    return deepcopy(item)

return update_database(
    operation
)
```

def get_user_history(
user_id: str,
*,
limit: int = 100,
) -> List[Dict[str, Any]]:
"""
Retourne l'historique d'un utilisateur.
"""

```
database = load_database()

items = [
    item
    for item in database[
        "history"
    ].values()
    if item.get(
        "userId"
    ) == user_id
]

items.sort(
    key=lambda item: item.get(
        "createdAt",
        "",
    ),
    reverse=True,
)

return deepcopy(
    items[:limit]
)
```

# ============================================================

# RÉPONSES IA

# ============================================================

def save_response(
*,
response_id: str,
user_id: Optional[str],
session_id: Optional[str],
response_type: str,
content: str,
) -> Dict[str, Any]:
"""
Sauvegarde une réponse IA.
"""

```
item = {
    "id": response_id,
    "userId": user_id,
    "sessionId": session_id,
    "type": response_type,
    "content": content,
    "createdAt": utc_now(),
}

def operation(
    database,
):

    database[
        "responses"
    ][response_id] = item

    return deepcopy(item)

return update_database(
    operation
)
```

def get_response(
response_id: str,
) -> Optional[Dict[str, Any]]:
"""
Récupère une réponse déjà générée.

```
Sa consultation ne doit pas déclencher une nouvelle
requête Gemini.
"""

database = load_database()

response = database[
    "responses"
].get(response_id)

if response is None:
    return None

return deepcopy(response)
```

# ============================================================

# CRÉDITS — TRANSACTIONS

# ============================================================

def save_credit_transaction(
*,
user_id: str,
amount: float,
transaction_type: str,
action: str,
balance_after: float,
metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
"""
Enregistre une transaction de crédit.

```
amount :
    positif = ajout
    négatif = dépense
"""

transaction_id = generate_id(
    "txn"
)

transaction = {
    "id": transaction_id,
    "userId": user_id,
    "amount": amount,
    "type": transaction_type,
    "action": action,
    "balanceAfter": balance_after,
    "metadata": metadata or {},
    "createdAt": utc_now(),
}

def operation(
    database,
):

    database[
        "credit_transactions"
    ][transaction_id] = transaction

    return deepcopy(
        transaction
    )

return update_database(
    operation
)
```

def get_credit_transactions(
user_id: str,
*,
limit: int = 100,
) -> List[Dict[str, Any]]:
"""
Retourne l'historique des transactions de crédits.
"""

```
database = load_database()

transactions = [
    transaction
    for transaction in database[
        "credit_transactions"
    ].values()
    if transaction.get(
        "userId"
    ) == user_id
]

transactions.sort(
    key=lambda item: item.get(
        "createdAt",
        "",
    ),
    reverse=True,
)

return deepcopy(
    transactions[:limit]
)
```

# ============================================================

# SÉRIES

# ============================================================

def get_streak(
user_id: str,
) -> Optional[Dict[str, Any]]:
"""
Récupère la série d'un utilisateur.
"""

```
database = load_database()

streak = database[
    "streaks"
].get(user_id)

if streak is None:
    return None

return deepcopy(streak)
```

def save_streak(
user_id: str,
streak: Dict[str, Any],
) -> Dict[str, Any]:
"""
Sauvegarde une série.
"""

```
def operation(
    database,
):

    database[
        "streaks"
    ][user_id] = streak

    return deepcopy(
        streak
    )

return update_database(
    operation
)
```

# ============================================================

# REWARDED ADS

# ============================================================

def save_rewarded_ad(
*,
user_id: str,
ad_id: str,
reward: float,
) -> Dict[str, Any]:
"""
Enregistre une rewarded ad validée.

```
La validation réelle de la publicité devra être effectuée
par le système publicitaire avant l'appel à cette fonction.
"""

item = {
    "id": ad_id,
    "userId": user_id,
    "reward": reward,
    "createdAt": utc_now(),
}

def operation(
    database,
):

    database[
        "rewarded_ads"
    ][ad_id] = item

    return deepcopy(
        item
    )

return update_database(
    operation
)
```

def rewarded_ad_exists(
ad_id: str,
) -> bool:
"""
Empêche l'utilisation multiple du même identifiant
de rewarded ad.
"""

```
database = load_database()

return (
    ad_id in database[
        "rewarded_ads"
    ]
)
```

# ============================================================

# SUPPRESSION / NETTOYAGE

# ============================================================

def delete_user_data(
user_id: str,
) -> bool:
"""
Supprime les données locales associées à un utilisateur.

```
Utilisable pour une fonctionnalité future de suppression
de compte.
"""

def operation(
    database,
):

    database[
        "users"
    ].pop(
        user_id,
        None,
    )

    database[
        "streaks"
    ].pop(
        user_id,
        None,
    )

    for collection in (
        "sessions",
        "history",
        "responses",
        "credit_transactions",
    ):

        collection_data = database[
            collection
        ]

        ids_to_delete = [
            item_id
            for item_id, item in collection_data.items()
            if item.get(
                "userId"
            ) == user_id
        ]

        for item_id in ids_to_delete:
            collection_data.pop(
                item_id,
                None,
            )

    return True

return bool(
    update_database(
        operation
    )
)
```

# ============================================================

# DIAGNOSTIC

# ============================================================

def storage_status() -> Dict[str, Any]:
"""
Retourne l'état du stockage.
"""

```
return {
    "type": "local_json",
    "path": str(
        LOCAL_DB_FILE
    ),
    "vercel": bool(
        os.getenv("VERCEL")
    ),
    "warning": (
        "Le stockage local n'est pas persistant "
        "pour la production Vercel."
    ),
}
```
