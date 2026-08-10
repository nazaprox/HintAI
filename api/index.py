```python
"""
HintAI - FastAPI Backend
Compatible Vercel

Entrypoint:
    api/index.py

Architecture:
    ai.py
    config.py
    storage.py
    user.py
"""

from fastapi import (
    FastAPI,
    Request,
    UploadFile,
    File,
    HTTPException,
)
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    StreamingResponse,
    JSONResponse,
)
from pydantic import BaseModel
from typing import Optional
import json
import uuid
import time
import os


# =====================================================
# APPLICATION
# =====================================================

app = FastAPI(
    title="HintAI",
    version="1.0.0"
)


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=[
        "*"
    ],
    allow_headers=[
        "*"
    ],
)


# =====================================================
# CONFIG
# =====================================================

APP_NAME = "HintAI"

ENVIRONMENT = os.getenv(
    "VERCEL_ENV",
    "development"
)


# =====================================================
# MODELES
# =====================================================

class HelpRequest(BaseModel):

    inputType: str

    text: Optional[str] = None

    fileId: Optional[str] = None

    directSolution: bool = False



class QuestionRequest(BaseModel):

    responseId: str

    question: str



class ConceptRequest(BaseModel):

    concept: str

    explanation: Optional[str] = ""

    exercises: list = []



class ResponseRequest(BaseModel):

    responseId: str



# =====================================================
# STREAM SSE
# =====================================================

def stream_answer(
    response_id: str,
    message: str
):

    yield (
        "event: start\n"
        f"data: {json.dumps({'id': response_id})}\n\n"
    )


    words = message.split()


    for word in words:

        yield (
            "event: token\n"
            f"data: {json.dumps({'text': word + ' '})}\n\n"
        )

        time.sleep(
            0.03
        )


    yield (
        "event: complete\n"
        f"data: {json.dumps({'responseId': response_id})}\n\n"
    )



def sse_response(
    response_id,
    text
):

    return StreamingResponse(
        stream_answer(
            response_id,
            text
        ),
        media_type="text/event-stream"
    )


# =====================================================
# ROOT
# =====================================================

@app.get("/")
def root():

    return {
        "service": APP_NAME,
        "status": "online",
        "environment": ENVIRONMENT
    }



@app.get("/api/health")
def health():

    return {
        "status": "ok",
        "service": APP_NAME
    }



# =====================================================
# HELP ME
# =====================================================

@app.post(
    "/api/help-me/start"
)
def help_me_start(
    data: HelpRequest
):

    if data.inputType not in [
        "text",
        "image",
        "pdf"
    ]:

        raise HTTPException(
            400,
            "Invalid input type"
        )


    response_id = str(
        uuid.uuid4()
    )


    return sse_response(
        response_id,
        "Je vais analyser ton exercice étape par étape."
    )



@app.post(
    "/api/help-me/hint/{level}"
)
def help_hint(
    level: int,
    data: ResponseRequest
):

    if level not in [
        1,
        2,
        3
    ]:

        raise HTTPException(
            400,
            "Invalid hint level"
        )


    return sse_response(
        data.responseId,
        f"Voici un indice niveau {level}."
    )



@app.post(
    "/api/help-me/question"
)
def help_question(
    data: QuestionRequest
):

    return sse_response(
        data.responseId,
        "Je réponds à ta question."
    )



@app.post(
    "/api/help-me/solution"
)
def help_solution(
    data: ResponseRequest
):

    return sse_response(
        data.responseId,
        "Voici la résolution complète."
    )



# =====================================================
# LEARN CONCEPT
# =====================================================

@app.post(
    "/api/learn-concept/start"
)
def learn_concept(
    data: ConceptRequest
):

    response_id = str(
        uuid.uuid4()
    )


    return sse_response(
        response_id,
        f"Apprentissage du concept : {data.concept}"
    )



# =====================================================
# UPLOAD
# =====================================================

@app.post(
    "/api/upload"
)
async def upload(
    file: UploadFile = File(...)
):

    return {
        "success": True,
        "filename": file.filename,
        "fileId": str(
            uuid.uuid4()
        )
    }



# =====================================================
# ERREURS
# =====================================================

@app.exception_handler(
    404
)
async def not_found(
    request: Request,
    exc
):

    return JSONResponse(
        status_code=404,
        content={
            "success": False,
            "message": "Endpoint introuvable"
        }
    )
```
