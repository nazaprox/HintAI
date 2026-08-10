"""
HintAI Backend
FastAPI + Render
"""


from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
    Request
)

from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import (
    StreamingResponse,
    JSONResponse
)

from pydantic import BaseModel

from typing import Optional

import uuid
import json
import time
import os


from ai import (
    analyze_exercise,
    generate_hint,
    generate_solution,
    answer_question,
    explain_concept
)





# =====================================================
# APP
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

    allow_origins=[

        "https://hintai-frontend.onrender.com",

        "*"

    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]

)





# =====================================================
# MODELS
# =====================================================


class HelpRequest(BaseModel):

    inputType: str

    text: Optional[str] = None

    fileId: Optional[str] = None

    directSolution: bool = False





class HintRequest(BaseModel):

    responseId: str





class QuestionRequest(BaseModel):

    responseId: str

    question: str





class ConceptRequest(BaseModel):

    concept: str





class ResponseRequest(BaseModel):

    responseId: str







# =====================================================
# SSE
# =====================================================


def stream_text(

    response_id,

    text

):


    yield (

        "event: start\n"

        + json.dumps({

            "id":response_id

        })

        + "\n\n"

    )


    for word in text.split():


        yield (

            "event: token\n"

            + json.dumps({

                "text":word+" "

            })

            + "\n\n"

        )


        time.sleep(

            0.02

        )



    yield (

        "event: complete\n"

        + json.dumps({

            "responseId":response_id

        })

        + "\n\n"

    )







def sse(

    response_id,

    text

):


    return StreamingResponse(

        stream_text(

            response_id,

            text

        ),

        media_type="text/event-stream"

    )








# =====================================================
# ROOT
# =====================================================


@app.get("/")

def home():

    return {


        "service":"HintAI",

        "status":"online",

        "environment":os.getenv(

            "RENDER",

            "production"

        )

    }






@app.get("/api/health")

def health():

    return {

        "status":"ok",

        "service":"HintAI"

    }







# =====================================================
# HELP ME
# =====================================================


@app.post("/api/help-me/start")

async def help_start(

    data:HelpRequest

):


    if data.inputType not in [

        "text",

        "image",

        "pdf"

    ]:


        raise HTTPException(

            400,

            "Type invalide"

        )



    response_id=str(

        uuid.uuid4()

    )



    result = await analyze_exercise(

        data.text or ""

    )



    return sse(

        response_id,

        result

    )







@app.post("/api/help-me/hint/{level}")

async def hint(

    level:int,

    data:HintRequest

):


    if level not in [1,2,3]:


        raise HTTPException(

            400,

            "Niveau invalide"

        )



    result = await generate_hint(

        data.responseId,

        level

    )


    return sse(

        data.responseId,

        result

    )







@app.post("/api/help-me/question")

async def question(

    data:QuestionRequest

):


    result = await answer_question(

        data.question

    )


    return sse(

        data.responseId,

        result

    )







@app.post("/api/help-me/solution")

async def solution(

    data:ResponseRequest

):


    result = await generate_solution(

        data.responseId

    )


    return sse(

        data.responseId,

        result

    )








# =====================================================
# LEARN CONCEPT
# =====================================================


@app.post("/api/learn-concept/start")

async def learn(

    data:ConceptRequest

):


    response_id=str(

        uuid.uuid4()

    )


    result = await explain_concept(

        data.concept

    )


    return sse(

        response_id,

        result

    )







# =====================================================
# UPLOAD
# =====================================================


@app.post("/api/upload")

async def upload(

    file:UploadFile = File(...)

):


    return {


        "success":True,

        "filename":file.filename,

        "fileId":str(

            uuid.uuid4()

        )

    }







# =====================================================
# ERROR
# =====================================================


@app.exception_handler(404)

async def error404(

    request:Request,

    exc

):


    return JSONResponse(

        status_code=404,

        content={

            "success":False,

            "message":"Route inexistante"

        }

    )