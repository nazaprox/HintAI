```python
"""
HintAI — app.py
===============

Point d'entrée FastAPI de HintAI.

Ce fichier :
- expose l'API HTTP ;
- relie ai.py, user.py et storage.py ;
- gère le streaming ;
- protège la consommation des crédits ;
- prépare le déploiement Vercel.

La logique IA reste dans ai.py.
La logique crédits/utilisateur reste dans user.py.
La persistance reste dans storage.py.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Generator, Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

import ai
import config
import storage
import user


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title=config.APP_NAME,
    version=config.APP_VERSION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS
    if config.ALLOWED_ORIGINS != ["*"]
    else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODÈLES
# ============================================================

class HelpMeStartRequest(BaseModel):
    inputType: str = Field(default="text")
    text: Optional[str] = None
    directSolution: bool = False
    fileName: Optional[str] = None
    mimeType: Optional[str] = None


class HelpMeHintRequest(BaseModel):
    responseId: Optional[str] = None
    sessionId: Optional[str] = None
    conversationId: Optional[str] = None


class HelpMeQuestionRequest(BaseModel):
    responseId: Optional[str] = None
    sessionId: Optional[str] = None
    conversationId: Optional[str] = None
    question: str


class HelpMeEvaluationRequest(BaseModel):
    responseId: Optional[str] = None
    sessionId: Optional[str] = None
    conversationId: Optional[str] = None
    exercise: Optional[str] = None


class HelpMeCorrectionRequest(BaseModel):
    responseId: Optional[str] = None
    sessionId: Optional[str] = None
    conversationId: Optional[str] = None
    exercise: Optional[str] = None
    studentAnswer: str


class LearnConceptStartRequest(BaseModel):
    concept: str
    understanding: Optional[str] = None
    exercises: Optional[list[str]] = None


class LearnConceptQuestionRequest(BaseModel):
    responseId: Optional[str] = None
    sessionId: Optional[str] = None
    lessonId: Optional[str] = None
    question: str
    concept: Optional[str] = None


class LearnConceptHintRequest(BaseModel):
    responseId: Optional[str] = None
    sessionId: Optional[str] = None
    lessonId: Optional[str] = None
    concept: Optional[str] = None
    exercise: Optional[str] = None


class LearnConceptExerciseRequest(BaseModel):
    responseId: Optional[str] = None
    sessionId: Optional[str] = None
    lessonId: Optional[str] = None
    concept: Optional[str] = None


class LearnConceptCorrectionRequest(BaseModel):
    responseId: Optional[str] = None
    sessionId: Optional[str] = None
    lessonId: Optional[str] = None
    concept: Optional[str] = None
    exercise: Optional[str] = None
    studentAnswer: str


class CreditPackRequest(BaseModel):
    userId: Optional[str] = None


class RewardedAdRequest(BaseModel):
    adId: str


# ============================================================
# OUTILS
# ============================================================

def json_error(
    message: str,
    *,
    status_code: int = 400,
    code: str = "ERROR",
    details: Optional[Dict[str, Any]] = None,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details or {},
            },
        },
    )


def json_success(
    data: Any,
    *,
    status_code: int = 200,
):
    return JSONResponse(
        status_code=status_code,
        content={
            "success": True,
            "data": data,
        },
    )


def sse_event(
    event: str,
    data: Dict[str, Any],
) -> str:
    return (
        f"event: {event}\n"
        f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
    )


def stream_with_persistence(
    *,
    user_id: str,
    session_id: Optional[str],
    response_type: str,
    title: str,
    mode: str,
    generator: Generator[str, None, None],
    extra_history: Optional[Dict[str, Any]] = None,
) -> StreamingResponse:
    """
    Transforme un générateur de chunks texte en SSE
    et sauvegarde la réponse à la fin.
    """

    response_id = storage.generate_id("rsp")

    def event_stream():
        chunks: list[str] = []

        yield sse_event(
            "start",
            {
                "id": response_id,
                "responseId": response_id,
                "sessionId": session_id,
                "userId": user_id,
                "type": response_type,
            },
        )

        try:
            for chunk in generator:
                if not chunk:
                    continue

                chunks.append(chunk)

                yield sse_event(
                    "token",
                    {
                        "text": chunk,
                    },
                )

            full_text = "".join(chunks)

            storage.save_response(
                response_id=response_id,
                user_id=user_id,
                session_id=session_id,
                response_type=response_type,
                content=full_text,
            )

            storage.save_history(
                user_id,
                session_id=session_id,
                mode=mode,
                title=title,
                content={
                    "responseId": response_id,
                    "type": response_type,
                    "text": full_text,
                    **(extra_history or {}),
                },
            )

            yield sse_event(
                "complete",
                {
                    "responseId": response_id,
                    "sessionId": session_id,
                    "done": True,
                },
            )

        except Exception as exc:
            yield sse_event(
                "error",
                {
                    "message": str(exc),
                },
            )

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream; charset=utf-8",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


def get_user_from_request(request: Request) -> Dict[str, Any]:
    """
    Récupère ou crée un utilisateur à partir du header
    X-Anonymous-ID.
    """

    anonymous_id = (
        request.headers.get("X-Anonymous-ID")
        or request.headers.get("X-User-Id")
        or request.headers.get("Authorization")
    )

    if anonymous_id and anonymous_id.startswith("Bearer "):
        anonymous_id = anonymous_id.removeprefix("Bearer ").strip()

    if not anonymous_id:
        user_record = user.create_user(plan="free")
        return user_record

    current = storage.get_user(anonymous_id)

    if current is not None:
        return user.get_user(current["id"]) or current

    created = user.create_user(
        user_id=anonymous_id,
        plan="free",
    )
    return created


def charge(
    user_id: str,
    action: str,
):
    """
    Dépense les crédits nécessaires pour une action.
    """
    try:
        return user.spend_credits(user_id, action)
    except ValueError as exc:
        raise HTTPException(
            status_code=402,
            detail=str(exc),
        ) from exc


def register_real_action(user_id: str):
    """
    Enregistre une vraie action pour le bonus de série.
    """
    try:
        user.register_real_action(user_id)
    except ValueError:
        pass


def resolve_session_from_request(
    payload: Any,
) -> Optional[Dict[str, Any]]:
    """
    Résout une session à partir de sessionId / conversationId
    ou via responseId.
    """

    session_id = (
        getattr(payload, "sessionId", None)
        or getattr(payload, "conversationId", None)
    )

    if session_id:
        session = storage.get_session(session_id)
        if session is not None:
            return session

    response_id = getattr(payload, "responseId", None)

    if response_id:
        response = storage.get_response(response_id)
        if response and response.get("sessionId"):
            return storage.get_session(response["sessionId"])

    return None


def get_session_problem(session: Dict[str, Any]) -> str:
    return str(
        session.get("problem")
        or session.get("concept")
        or session.get("title")
        or ""
    ).strip()


# ============================================================
# ROUTES GÉNÉRALES
# ============================================================

@app.get("/")
def root():
    return json_success(
        {
            "service": config.APP_NAME,
            "version": config.APP_VERSION,
            "status": "online",
        }
    )


@app.get("/api/health")
def health():
    return json_success(
        {
            "status": "ok",
            "service": config.APP_NAME,
            "version": config.APP_VERSION,
            "environment": config.ENVIRONMENT,
            "storage": storage.storage_status(),
            "creditSystem": user.credit_system(),
        }
    )


@app.get("/api/me")
def me(request: Request):
    current_user = get_user_from_request(request)
    summary = user.account_summary(current_user["id"])
    return json_success(summary)


@app.get("/api/history")
def history(request: Request, limit: int = 50):
    current_user = get_user_from_request(request)
    items = storage.get_user_history(current_user["id"], limit=limit)
    return json_success(items)


@app.get("/api/responses/{response_id}")
def get_response(response_id: str):
    response = storage.get_response(response_id)
    if response is None:
        raise HTTPException(status_code=404, detail="Réponse introuvable.")
    return json_success(response)


@app.post("/api/credits/purchase")
def purchase_credits(request: Request, payload: CreditPackRequest):
    current_user = get_user_from_request(request)
    if payload.userId and payload.userId != current_user["id"]:
        raise HTTPException(status_code=403, detail="Utilisateur non autorisé.")
    updated = user.purchase_credit_pack(current_user["id"])
    return json_success(user.account_summary(updated["id"]))


@app.post("/api/ads/simple")
def simple_ad():
    return json_success(user.simple_ad_completed())


@app.post("/api/ads/rewarded")
def rewarded_ad(request: Request, payload: RewardedAdRequest):
    current_user = get_user_from_request(request)
    updated = user.reward_ad(current_user["id"], payload.adId)
    return json_success(user.account_summary(updated["id"]))


@app.post("/api/streak/register")
def streak_register(request: Request):
    current_user = get_user_from_request(request)
    updated = user.register_real_action(current_user["id"])
    return json_success(updated)


# ============================================================
# HELP ME
# ============================================================

@app.post("/api/help-me/start")
def help_me_start(request: Request, payload: HelpMeStartRequest):
    current_user = get_user_from_request(request)

    if payload.inputType not in {"text", "image", "pdf"}:
        raise HTTPException(status_code=400, detail="inputType invalide.")

    text = (payload.text or "").strip()

    if payload.inputType == "text" and not text:
        raise HTTPException(status_code=400, detail="Le texte est vide.")

    action = "full_solution" if payload.directSolution else "help_me_analysis"
    charge(current_user["id"], action)
    register_real_action(current_user["id"])

    session = storage.create_session(
        current_user["id"],
        session_type="help_me",
    )

    storage.update_session(
        session["id"],
        {
            "mode": "help_me",
            "problem": text,
            "directSolution": payload.directSolution,
            "inputType": payload.inputType,
            "fileName": payload.fileName,
            "mimeType": payload.mimeType,
        },
    )

    if payload.directSolution:
        generator = ai.solve_exercise_stream(text)
        response_type = "help_solution"
        title = "Résolution complète"
    else:
        generator = ai.analyze_exercise_stream(text)
        response_type = "help_analysis"
        title = "Analyse Help Me"

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type=response_type,
        title=title,
        mode="help_me",
        generator=generator,
        extra_history={
            "directSolution": payload.directSolution,
            "inputType": payload.inputType,
        },
    )


@app.post("/api/help-me/hint/{level}")
def help_me_hint(
    request: Request,
    level: int,
    payload: HelpMeHintRequest,
):
    current_user = get_user_from_request(request)
    session = resolve_session_from_request(payload)

    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable.")

    if level not in (1, 2, 3):
        raise HTTPException(status_code=400, detail="Niveau d'indice invalide.")

    problem = get_session_problem(session)
    if not problem:
        raise HTTPException(status_code=400, detail="Exercice introuvable dans la session.")

    charge(current_user["id"], f"hint_{level}")
    register_real_action(current_user["id"])

    generator = ai.generate_hint_stream(problem, level)

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type=f"help_hint_{level}",
        title=f"Indice {level}",
        mode="help_me",
        generator=generator,
        extra_history={"level": level},
    )


@app.post("/api/help-me/question")
def help_me_question(
    request: Request,
    payload: HelpMeQuestionRequest,
):
    current_user = get_user_from_request(request)
    session = resolve_session_from_request(payload)

    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable.")

    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question vide.")

    problem = get_session_problem(session)
    if not problem:
        raise HTTPException(status_code=400, detail="Exercice introuvable dans la session.")

    charge(current_user["id"], "help_me_question")
    register_real_action(current_user["id"])

    generator = ai.answer_question_stream(problem, question)

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type="help_question",
        title="Question Help Me",
        mode="help_me",
        generator=generator,
        extra_history={"question": question},
    )


@app.post("/api/help-me/solution")
def help_me_solution(
    request: Request,
    payload: HelpMeEvaluationRequest,
):
    current_user = get_user_from_request(request)
    session = resolve_session_from_request(payload)

    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable.")

    problem = get_session_problem(session)
    if not problem:
        raise HTTPException(status_code=400, detail="Exercice introuvable dans la session.")

    charge(current_user["id"], "help_me_solution")
    register_real_action(current_user["id"])

    generator = ai.solve_exercise_stream(problem)

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type="help_solution",
        title="Résolution complète",
        mode="help_me",
        generator=generator,
    )


@app.post("/api/help-me/evaluation")
def help_me_evaluation(
    request: Request,
    payload: HelpMeEvaluationRequest,
):
    current_user = get_user_from_request(request)
    session = resolve_session_from_request(payload)

    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable.")

    problem = payload.exercise or get_session_problem(session)
    if not problem:
        raise HTTPException(status_code=400, detail="Exercice introuvable.")

    charge(current_user["id"], "evaluation_exercise")
    register_real_action(current_user["id"])

    generator = ai.generate_evaluation(problem)

    def wrap():
        yield generator

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type="evaluation_exercise",
        title="Exercice d'évaluation",
        mode="help_me",
        generator=wrap(),
    )


@app.post("/api/help-me/evaluation/correct")
def help_me_evaluation_correct(
    request: Request,
    payload: HelpMeCorrectionRequest,
):
    current_user = get_user_from_request(request)
    session = resolve_session_from_request(payload)

    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable.")

    exercise = payload.exercise or get_session_problem(session)
    if not exercise:
        raise HTTPException(status_code=400, detail="Exercice introuvable.")

    student_answer = payload.studentAnswer.strip()
    if not student_answer:
        raise HTTPException(status_code=400, detail="Réponse vide.")

    charge(current_user["id"], "evaluation_correction")
    register_real_action(current_user["id"])

    generator_text = ai.correct_work(exercise, student_answer)

    def wrap():
        yield generator_text

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type="evaluation_correction",
        title="Correction",
        mode="help_me",
        generator=wrap(),
    )


# ============================================================
# LEARN A CONCEPT
# ============================================================

@app.post("/api/learn-concept/start")
def learn_concept_start(
    request: Request,
    payload: LearnConceptStartRequest,
):
    current_user = get_user_from_request(request)

    concept = payload.concept.strip()
    if not concept:
        raise HTTPException(status_code=400, detail="Concept vide.")

    charge(current_user["id"], "concept_explanation")
    register_real_action(current_user["id"])

    session = storage.create_session(
        current_user["id"],
        session_type="learn_concept",
    )

    storage.update_session(
        session["id"],
        {
            "mode": "learn_concept",
            "concept": concept,
            "understanding": payload.understanding,
            "referenceExercises": payload.exercises or [],
        },
    )

    generator = ai.explain_concept(concept)

    def wrap():
        yield generator

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type="concept_explanation",
        title="Explication du concept",
        mode="learn_concept",
        generator=wrap(),
        extra_history={
            "concept": concept,
        },
    )


@app.post("/api/learn-concept/question")
def learn_concept_question(
    request: Request,
    payload: LearnConceptQuestionRequest,
):
    current_user = get_user_from_request(request)
    session = resolve_session_from_request(payload)

    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable.")

    concept = payload.concept or str(session.get("concept", "")).strip()
    if not concept:
        raise HTTPException(status_code=400, detail="Concept introuvable.")

    question = payload.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question vide.")

    charge(current_user["id"], "concept_question")
    register_real_action(current_user["id"])

    generator = ai.ask_concept_question(concept, question)

    def wrap():
        yield generator

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type="concept_question",
        title="Question concept",
        mode="learn_concept",
        generator=wrap(),
        extra_history={"question": question},
    )


@app.post("/api/learn-concept/hint")
def learn_concept_hint(
    request: Request,
    payload: LearnConceptHintRequest,
):
    current_user = get_user_from_request(request)
    session = resolve_session_from_request(payload)

    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable.")

    concept = payload.concept or str(session.get("concept", "")).strip()
    exercise = payload.exercise or str(session.get("exercise", "")).strip()

    if not concept:
        raise HTTPException(status_code=400, detail="Concept introuvable.")
    if not exercise:
        raise HTTPException(status_code=400, detail="Exercice introuvable.")

    charge(current_user["id"], "concept_hint")
    register_real_action(current_user["id"])

    generator = ai.generate_concept_hint(concept, exercise)

    def wrap():
        yield generator

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type="concept_hint",
        title="Indice concept",
        mode="learn_concept",
        generator=wrap(),
    )


@app.post("/api/learn-concept/easy")
def learn_concept_easy(
    request: Request,
    payload: LearnConceptExerciseRequest,
):
    current_user = get_user_from_request(request)
    session = resolve_session_from_request(payload)

    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable.")

    concept = payload.concept or str(session.get("concept", "")).strip()
    if not concept:
        raise HTTPException(status_code=400, detail="Concept introuvable.")

    charge(current_user["id"], "easy_exercise")
    register_real_action(current_user["id"])

    generator = ai.generate_easy_exercise(concept)

    def wrap():
        yield generator

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type="easy_exercise",
        title="Exercice simple",
        mode="learn_concept",
        generator=wrap(),
    )


@app.post("/api/learn-concept/difficult")
def learn_concept_difficult(
    request: Request,
    payload: LearnConceptExerciseRequest,
):
    current_user = get_user_from_request(request)
    session = resolve_session_from_request(payload)

    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable.")

    concept = payload.concept or str(session.get("concept", "")).strip()
    if not concept:
        raise HTTPException(status_code=400, detail="Concept introuvable.")

    charge(current_user["id"], "difficult_exercise")
    register_real_action(current_user["id"])

    generator = ai.generate_difficult_exercise(concept)

    def wrap():
        yield generator

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type="difficult_exercise",
        title="Exercice difficile",
        mode="learn_concept",
        generator=wrap(),
    )


@app.post("/api/learn-concept/correct")
def learn_concept_correct(
    request: Request,
    payload: LearnConceptCorrectionRequest,
):
    current_user = get_user_from_request(request)
    session = resolve_session_from_request(payload)

    if session is None:
        raise HTTPException(status_code=404, detail="Session introuvable.")

    concept = payload.concept or str(session.get("concept", "")).strip()
    exercise = payload.exercise or str(session.get("exercise", "")).strip()

    if not concept:
        raise HTTPException(status_code=400, detail="Concept introuvable.")
    if not exercise:
        raise HTTPException(status_code=400, detail="Exercice introuvable.")

    answer = payload.studentAnswer.strip()
    if not answer:
        raise HTTPException(status_code=400, detail="Réponse vide.")

    charge(current_user["id"], "concept_correction")
    register_real_action(current_user["id"])

    generator = ai.correct_concept_exercise(concept, exercise, answer)

    def wrap():
        yield generator

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type="concept_correction",
        title="Correction concept",
        mode="learn_concept",
        generator=wrap(),
    )


# ============================================================
# DOCUMENT
# ============================================================

@app.post("/api/document/analyze")
def document_analyze(request: Request, payload: Dict[str, Any]):
    """
    Analyse simple d'un document déjà validé localement.
    Le fichier binaire n'est pas géré ici dans cette V1.
    """
    current_user = get_user_from_request(request)

    text = str(payload.get("text", "")).strip()
    if not text:
        raise HTTPException(status_code=400, detail="Document vide.")

    charge(current_user["id"], "document_ai_analysis")
    register_real_action(current_user["id"])

    session = storage.create_session(
        current_user["id"],
        session_type="document",
    )

    generator = ai.analyze_document_stream(
        prompt="Analyse le document fourni et aide l'élève.",
        file_bytes=text.encode("utf-8"),
        mime_type="text/plain",
    )

    return stream_with_persistence(
        user_id=current_user["id"],
        session_id=session["id"],
        response_type="document_analysis",
        title="Analyse document",
        mode="document",
        generator=generator,
    )


# ============================================================
# GESTION D'ERREURS
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return json_error(
        str(exc.detail),
        status_code=exc.status_code,
        code="HTTP_ERROR",
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return json_error(
        "Erreur interne du serveur.",
        status_code=500,
        code="INTERNAL_ERROR",
        details={"message": str(exc)},
    )


# ============================================================
# DÉMARRAGE LOCAL
# ============================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
```
