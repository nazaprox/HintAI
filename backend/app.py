"""HintAI V2 production FastAPI application."""
from __future__ import annotations

import os
import uuid
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from ai import analyze_exercise, explain_concept, generate_hint, generate_solution
from config import ALLOWED_ORIGINS

APP_NAME = "HintAI"
APP_VERSION = "2.0.0"

uploads: dict[str, bytes] = {}
responses: dict[str, str] = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="AI educational tutor for guided problem solving and learning.",
    lifespan=lifespan,
    docs_url="/docs" if os.getenv("ENVIRONMENT", "production") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT", "production") != "production" else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-User-ID"],
)


class HelpRequest(BaseModel):
    inputType: str = "text"
    text: str = ""
    fileId: str | None = None


class ResponseRequest(BaseModel):
    responseId: str


class LearnRequest(BaseModel):
    concept: str


@app.get("/")
async def root() -> dict[str, str]:
    return {"service": APP_NAME, "status": "online", "version": APP_VERSION}


@app.get("/health")
@app.get("/api/health", include_in_schema=False)
async def health() -> dict[str, str]:
    return {"status": "ok", "service": APP_NAME, "version": APP_VERSION}


@app.get("/ready")
@app.get("/api/ready", include_in_schema=False)
async def ready() -> dict[str, str]:
    return {"status": "ready", "service": APP_NAME, "version": APP_VERSION}


@app.post("/api/upload")
async def upload(file: UploadFile = File(...)) -> dict[str, Any]:
    data = await file.read()
    if not data:
        raise HTTPException(400, "Fichier vide")
    if len(data) > 20 * 1024 * 1024:
        raise HTTPException(413, "Fichier trop volumineux (20 Mo maximum)")
    allowed = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
    if file.content_type not in allowed:
        raise HTTPException(415, "Format non supporté")
    file_id = str(uuid.uuid4())
    uploads[file_id] = data
    return {"fileId": file_id, "file_id": file_id, "filename": file.filename, "contentType": file.content_type}


@app.post("/api/help-me/start")
async def help_me_start(request: HelpRequest) -> dict[str, Any]:
    text = request.text.strip()
    if request.fileId:
        if request.fileId not in uploads:
            raise HTTPException(404, "Fichier introuvable")
        text = text or "Analyse le document envoyé par l'utilisateur. Décris ce que tu peux identifier et demande une précision si l'exercice n'est pas lisible."
    if not text:
        raise HTTPException(400, "Ajoute un exercice ou un fichier")
    answer = await analyze_exercise(text)
    response_id = str(uuid.uuid4())
    responses[response_id] = answer
    return {"responseId": response_id, "response_id": response_id, "text": answer, "answer": answer}


@app.post("/api/help-me/hint/{level}")
async def help_me_hint(level: int, request: ResponseRequest) -> dict[str, Any]:
    if level not in (1, 2, 3):
        raise HTTPException(400, "Niveau d'indice invalide")
    if request.responseId not in responses:
        raise HTTPException(404, "Réponse introuvable")
    answer = await generate_hint(request.responseId, level)
    return {"responseId": request.responseId, "text": answer, "answer": answer}


@app.post("/api/help-me/solution")
async def help_me_solution(request: ResponseRequest) -> dict[str, Any]:
    if request.responseId not in responses:
        raise HTTPException(404, "Réponse introuvable")
    answer = await generate_solution(request.responseId)
    return {"responseId": request.responseId, "text": answer, "answer": answer}


@app.post("/api/learn-concept/start")
async def learn_concept(request: LearnRequest) -> dict[str, Any]:
    concept = request.concept.strip()
    if not concept:
        raise HTTPException(400, "Concept manquant")
    answer = await explain_concept(concept)
    response_id = str(uuid.uuid4())
    responses[response_id] = answer
    return {"responseId": response_id, "response_id": response_id, "text": answer, "answer": answer}
