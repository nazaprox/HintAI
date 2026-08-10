```python
"""
HintAI — Main API
==================

Point d'entrée du backend Python pour Vercel.

Responsabilités :
- API HTTP principale
- CORS
- health check
- réception des requêtes Help Me
- réception des requêtes Learn a Concept
- streaming SSE vers Expo / React Native
- validation minimale des requêtes
- connexion future avec ai.py, auth.py, credits.py,
  quality.py, storage.py et utils.py

IMPORTANT :
La logique métier lourde reste dans les autres modules.
Ce fichier sert de contrôleur/API.

Déploiement :
    Vercel -> backend.api:app
"""

from __future__ import annotations

import json
import os
import time
import uuid
from typing import Any, Dict, Generator, Optional

from flask import Flask, Response, jsonify, request
from flask_cors import CORS


# ============================================================
# APPLICATION
# ============================================================

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/api/*": {
            "origins": "*",
            "methods": [
                "GET",
                "POST",
                "PUT",
                "PATCH",
                "DELETE",
                "OPTIONS",
            ],
            "allow_headers": [
                "Content-Type",
                "Authorization",
                "X-Anonymous-ID",
            ],
        }
    },
)


# ============================================================
# CONFIGURATION
# ============================================================

APP_NAME = "HintAI"

APP_VERSION = os.getenv(
    "HINTAI_VERSION",
    "2.0.0",
)

ENVIRONMENT = os.getenv(
    "VERCEL_ENV",
    os.getenv(
        "ENVIRONMENT",
        "development",
    ),
)


# ============================================================
# UTILITAIRES API
# ============================================================

def json_error(
    message: str,
    status_code: int = 400,
    code: Optional[str] = None,
):
    """
    Retourne une erreur API uniforme.
    """

    payload: Dict[str, Any] = {
        "success": False,
        "message": message,
    }

    if code:
        payload["code"] = code

    return jsonify(payload), status_code


def json_success(
    data: Any,
    status_code: int = 200,
):
    """
    Retourne une réponse API uniforme.
    """

    return (
        jsonify(
            {
                "success": True,
                "data": data,
            }
        ),
        status_code,
    )


def get_json_body() -> Dict[str, Any]:
    """
    Récupère proprement le JSON envoyé par le frontend.
    """

    if not request.is_json:
        raise ValueError(
            "Le corps de la requête doit être au format JSON."
        )

    body = request.get_json(
        silent=True
    )

    if not isinstance(body, dict):
        raise ValueError(
            "Le corps JSON est invalide."
        )

    return body


def get_auth_token() -> Optional[str]:
    """
    Récupère le Bearer token.

    Format :
        Authorization: Bearer <token>
    """

    header = request.headers.get(
        "Authorization"
    )

    if not header:
        return None

    if not header.startswith(
        "Bearer "
    ):
        return None

    return header[
        len("Bearer "):
    ].strip() or None


def get_anonymous_id() -> Optional[str]:
    """
    Identifiant anonyme envoyé par l'application Expo.

    Il ne remplace pas l'authentification.
    Il sert notamment à gérer les utilisateurs Free
    avant connexion et à limiter certains abus.
    """

    value = request.headers.get(
        "X-Anonymous-ID"
    )

    if not value:
        return None

    value = value.strip()

    if not value:
        return None

    return value[:128]


# ============================================================
# SSE / STREAMING
# ============================================================

def sse_event(
    event: str,
    data: Dict[str, Any],
) -> str:
    """
    Construit un événement Server-Sent Event.

    Exemple :

        event: token
        data: {"text": "Bonjour"}

    """

    return (
        f"event: {event}\n"
        f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    )


def stream_demo(
    response_id: str,
) -> Generator[str, None, None]:
    """
    Streaming temporaire.

    Cette fonction sera remplacée par le véritable flux Gemini
    dans ai.py.

    Elle permet néanmoins de tester immédiatement :

        Backend Python
            ↓
        SSE
            ↓
        Expo / React Native
    """

    yield sse_event(
        "start",
        {
            "id": response_id,
        },
    )

    yield sse_event(
        "status",
        {
            "message": "Analyse de l'exercice...",
        },
    )

    time.sleep(0.05)

    text = (
        "Je vais t'aider à comprendre "
        "cet exercice étape par étape."
    )

    words = text.split(" ")

    for index, word in enumerate(words):
        suffix = (
            " "
            if index < len(words) - 1
            else ""
        )

        yield sse_event(
            "token",
            {
                "text": word + suffix,
            },
        )

        time.sleep(0.025)

    yield sse_event(
        "complete",
        {
            "responseId": response_id,
        },
    )


def stream_response(
    generator: Generator[str, None, None],
) -> Response:
    """
    Crée une réponse SSE compatible avec les clients mobiles.
    """

    return Response(
        generator,
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================
# HEALTH
# ============================================================

@app.get("/api/health")
def health():
    """
    Vérification de disponibilité du backend.
    """

    return jsonify(
        {
            "status": "ok",
            "service": APP_NAME,
            "version": APP_VERSION,
            "environment": ENVIRONMENT,
        }
    )


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():
    """
    Endpoint racine.
    """

    return jsonify(
        {
            "service": APP_NAME,
            "version": APP_VERSION,
            "status": "online",
        }
    )


# ============================================================
# HELP ME — INITIALISATION
# ============================================================

@app.post("/api/help-me/start")
def help_me_start():
    """
    Démarre une session Help Me.

    Entrée possible :

    {
        "inputType": "text",
        "text": "Résoudre 2x + 4 = 10"
    }

    ou :

    {
        "inputType": "image",
        "fileId": "..."
    }

    ou :

    {
        "inputType": "pdf",
        "fileId": "..."
    }

    directSolution=true permet de demander directement
    la résolution complète.
    """

    try:
        body = get_json_body()

    except ValueError as exc:
        return json_error(
            str(exc),
            400,
            "INVALID_JSON",
        )

    input_type = body.get(
        "inputType"
    )

    if input_type not in {
        "text",
        "image",
        "pdf",
    }:
        return json_error(
            "inputType doit être text, image ou pdf.",
            400,
            "INVALID_INPUT_TYPE",
        )

    if (
        input_type == "text"
        and not str(
            body.get("text", "")
        ).strip()
    ):
        return json_error(
            "Le texte de l'exercice est vide.",
            400,
            "EMPTY_TEXT",
        )

    if input_type in {
        "image",
        "pdf",
    }:
        if not body.get(
            "fileId"
        ) and not body.get(
            "fileUri"
        ):
            return json_error(
                "Un fichier est requis.",
                400,
                "MISSING_FILE",
            )

    response_id = str(
        uuid.uuid4()
    )

    direct_solution = bool(
        body.get(
            "directSolution",
            False,
        )
    )

    anonymous_id = (
        get_anonymous_id()
    )

    token = get_auth_token()

    # --------------------------------------------------------
    # TODO :
    # 1. auth.py
    # 2. credits.py
    # 3. quality.py
    # 4. ai.py
    # 5. storage.py
    #
    # seront branchés ici.
    # --------------------------------------------------------

    return stream_response(
        stream_demo(
            response_id
        )
    )


# ============================================================
# HELP ME — INDICE
# ============================================================

@app.post(
    "/api/help-me/hint/<int:level>"
)
def help_me_hint(level: int):
    """
    Demande un indice.

    level :
        1 = indice léger
        2 = indice intermédiaire
        3 = indice très explicite

    La résolution complète n'est PAS envoyée ici.
    """

    if level not in {
        1,
        2,
        3,
    }:
        return json_error(
            "Le niveau d'indice doit être compris entre 1 et 3.",
            400,
            "INVALID_HINT_LEVEL",
        )

    try:
        body = get_json_body()

    except ValueError as exc:
        return json_error(
            str(exc),
            400,
            "INVALID_JSON",
        )

    response_id = body.get(
        "responseId"
    )

    if not response_id:
        return json_error(
            "responseId est requis.",
            400,
            "MISSING_RESPONSE_ID",
        )

    return stream_response(
        stream_demo(
            str(response_id)
        )
    )


# ============================================================
# HELP ME — QUESTION
# ============================================================

@app.post(
    "/api/help-me/question"
)
def help_me_question():
    """
    Permet à l'élève de poser une question
    pendant la résolution.
    """

    try:
        body = get_json_body()

    except ValueError as exc:
        return json_error(
            str(exc),
            400,
            "INVALID_JSON",
        )

    response_id = body.get(
        "responseId"
    )

    question = str(
        body.get(
            "question",
            ""
        )
    ).strip()

    if not response_id:
        return json_error(
            "responseId est requis.",
            400,
            "MISSING_RESPONSE_ID",
        )

    if not question:
        return json_error(
            "La question est vide.",
            400,
            "EMPTY_QUESTION",
        )

    if len(question) > 4000:
        return json_error(
            "La question est trop longue.",
            400,
            "QUESTION_TOO_LONG",
        )

    return stream_response(
        stream_demo(
            str(response_id)
        )
    )


# ============================================================
# HELP ME — SOLUTION COMPLÈTE
# ============================================================

@app.post(
    "/api/help-me/solution"
)
def help_me_solution():
    """
    Demande la résolution complète.
    """

    try:
        body = get_json_body()

    except ValueError as exc:
        return json_error(
            str(exc),
            400,
            "INVALID_JSON",
        )

    response_id = body.get(
        "responseId"
    )

    if not response_id:
        return json_error(
            "responseId est requis.",
            400,
            "MISSING_RESPONSE_ID",
        )

    return stream_response(
        stream_demo(
            str(response_id)
        )
    )


# ============================================================
# LEARN A CONCEPT
# ============================================================

@app.post(
    "/api/learn-concept/start"
)
def learn_concept_start():
    """
    Démarre Learn a Concept.

    Entrée :

    {
        "concept": "Dérivées",
        "exercises": [],
        "explanation": "Je connais les bases..."
    }

    Le véritable processus pédagogique sera géré
    par ai.py.
    """

    try:
        body = get_json_body()

    except ValueError as exc:
        return json_error(
            str(exc),
            400,
            "INVALID_JSON",
        )

    concept = str(
        body.get(
            "concept",
            ""
        )
    ).strip()

    if not concept:
        return json_error(
            "Le concept à apprendre est requis.",
            400,
            "MISSING_CONCEPT",
        )

    if len(concept) > 1000:
        return json_error(
            "Le concept est trop long.",
            400,
            "CONCEPT_TOO_LONG",
        )

    response_id = str(
        uuid.uuid4()
    )

    return stream_response(
        stream_demo(
            response_id
        )
    )


# ============================================================
# GLOBAL ERROR HANDLER
# ============================================================

@app.errorhandler(404)
def not_found(error):
    return json_error(
        "Endpoint introuvable.",
        404,
        "NOT_FOUND",
    )


@app.errorhandler(405)
def method_not_allowed(error):
    return json_error(
        "Méthode HTTP non autorisée.",
        405,
        "METHOD_NOT_ALLOWED",
    )


@app.errorhandler(500)
def internal_error(error):
    return json_error(
        "Erreur interne du serveur.",
        500,
        "INTERNAL_ERROR",
    )


# ============================================================
# LOCAL DEVELOPMENT
# ============================================================

if __name__ == "__main__":
    port = int(
        os.getenv(
            "PORT",
            "8000",
        )
    )

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True,
    )
```
