"""HintAI V2 FastAPI application for Render."""

from __future__ import annotations

import json
import os
import time
import uuid
from typing import Optional

from fastapi import FastAPI, File, Header, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

from abuse import allowed
from ads import can_reward, rewarded_ad_duration, reward_amount, simple_ad_duration, simple_ad_reward
from ai import analyze_exercise, answer_question, explain_concept, generate_hint, generate_solution
from config import ALLOWED_ORIGINS, MAX_QUESTION_LENGTH, MAX_TEXT_LENGTH, REWARDED_AD_CREDITS
from credits import consume, get_account, register_action, reward, set_plan
from subscription import credit_pack, list_plans

app = FastAPI(title="HintAI", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class HelpRequest(BaseModel):
    inputType: str
    text: Optional[str] = None
    fileId: Optional[str] = None
    directSolution: bool = False


class HintRequest(BaseModel):
    responseId: str


class QuestionRequest(BaseModel):
    responseId: str
    question: str = Field(min_length=1, max_length=MAX_QUESTION_LENGTH)


class ConceptRequest(BaseModel):
    concept: str = Field(min_length=1, max_length=MAX_TEXT_LENGTH)


class ResponseRequest(BaseModel):
    responseId: str


def current_user(user_id: Optional[str]) -> str:
    return user_id or "anonymous"


def guard(user_id: str) -> None:
    if not allowed(user_id, limit=30):
        raise HTTPException(status_code=429, detail="Trop de requêtes. Réessaie dans une minute.")


def spend(user_id: str, action: str) -> dict:
    try:
        return consume(user_id, action)
    except ValueError as exc:
        raise HTTPException(status_code=402, detail=str(exc)) from exc


def educational_action(user_id: str, action: str) -> dict:
    account = register_action(user_id, action)
    return account


def stream_text(response_id: str, text: str):
    yield "event: start\n" + json.dumps({"id": response_id}) + "\n\n"
    for word in text.split():
        yield "event: token\n" + json.dumps({"text": word + " "}) + "\n\n"
        time.sleep(0.012)
    yield "event: complete\n" + json.dumps({"responseId": response_id}) + "\n\n"


def sse(response_id: str, text: str):
    return StreamingResponse(stream_text(response_id, text), media_type="text/event-stream", headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@app.get("/")
def home():
    return {"service": "HintAI", "status": "online", "version": "2.0.0", "environment": os.getenv("RENDER", "production")}


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "HintAI", "version": "2.0.0"}


@app.get("/api/account")
def account(x_user_id: Optional[str] = Header(default=None)):
    return get_account(current_user(x_user_id))


@app.get("/api/plans")
def plans():
    return {"plans": list_plans(), "creditPack": credit_pack(1)}


@app.post("/api/ads/simple/complete")
def simple_ad_complete():
    return {"durationSeconds": simple_ad_duration(), "reward": simple_ad_reward()}


@app.post("/api/ads/rewarded/claim")
def rewarded_claim(ad_id: str, x_user_id: Optional[str] = Header(default=None)):
    user_id = current_user(x_user_id)
    guard(user_id)
    if not ad_id.strip():
        raise HTTPException(status_code=400, detail="ad_id requis")
    # The frontend must supply a unique ad id; production must additionally
    # verify the ad-network server-side callback before granting the reward.
    try:
        account = reward(user_id, REWARDED_AD_CREDITS, "rewarded_ad")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"success": True, "adId": ad_id, "durationSeconds": rewarded_ad_duration(), "reward": reward_amount(), "account": account}


@app.post("/api/help-me/start")
async def help_start(data: HelpRequest, x_user_id: Optional[str] = Header(default=None)):
    user_id = current_user(x_user_id)
    guard(user_id)
    if data.inputType not in {"text", "image", "pdf"}:
        raise HTTPException(status_code=400, detail="Type invalide")
    if data.text and len(data.text) > MAX_TEXT_LENGTH:
        raise HTTPException(status_code=413, detail="Texte trop long")
    action = "help_me_analysis"
    spend(user_id, action)
    educational_action(user_id, action)
    response_id = str(uuid.uuid4())
    result = await analyze_exercise(data.text or "")
    return sse(response_id, result)


@app.post("/api/help-me/hint/{level}")
async def hint(level: int, data: HintRequest, x_user_id: Optional[str] = Header(default=None)):
    user_id = current_user(x_user_id)
    guard(user_id)
    if level not in {1, 2, 3}:
        raise HTTPException(status_code=400, detail="Niveau invalide")
    action = f"hint_{level}"
    spend(user_id, action)
    educational_action(user_id, action)
    result = await generate_hint(data.responseId, level)
    return sse(data.responseId, result)


@app.post("/api/help-me/question")
async def question(data: QuestionRequest, x_user_id: Optional[str] = Header(default=None)):
    user_id = current_user(x_user_id)
    guard(user_id)
    spend(user_id, "ai_question")
    educational_action(user_id, "ai_question")
    result = await answer_question(data.question)
    return sse(data.responseId, result)


@app.post("/api/help-me/solution")
async def solution(data: ResponseRequest, x_user_id: Optional[str] = Header(default=None)):
    user_id = current_user(x_user_id)
    guard(user_id)
    spend(user_id, "full_solution")
    educational_action(user_id, "full_solution")
    result = await generate_solution(data.responseId)
    return sse(data.responseId, result)


@app.post("/api/learn-concept/start")
async def learn(data: ConceptRequest, x_user_id: Optional[str] = Header(default=None)):
    user_id = current_user(x_user_id)
    guard(user_id)
    spend(user_id, "learn_initial_explanation")
    educational_action(user_id, "learn_initial_explanation")
    response_id = str(uuid.uuid4())
    result = await explain_concept(data.concept)
    return sse(response_id, result)


@app.post("/api/upload")
async def upload(file: UploadFile = File(...), x_user_id: Optional[str] = Header(default=None)):
    user_id = current_user(x_user_id)
    guard(user_id)
    content_type = (file.content_type or "").lower()
    if content_type not in {"image/jpeg", "image/png", "image/webp", "application/pdf"}:
        raise HTTPException(status_code=415, detail="Type de fichier non supporté")
    action = "pdf_upload" if content_type == "application/pdf" else "image_upload"
    spend(user_id, action)
    return {"success": True, "filename": file.filename, "fileId": str(uuid.uuid4()), "account": get_account(user_id)}


@app.exception_handler(404)
async def error404(request: Request, exc):
    return JSONResponse(status_code=404, content={"success": False, "message": "Route inexistante"})
