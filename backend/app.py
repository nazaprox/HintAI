from fastapi import FastAPI, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from backend.config import Config
from backend.models import StartAnalysisRequest, RequestHintRequest, RequestSolutionRequest, LearnConceptRequest, AuthRegisterRequest, AuthLoginRequest, RewardRequest
from backend import credits, user, abuse, uploads, ai

app = FastAPI(title="HintAI API", version="2.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

def success_res(data: dict):
    return JSONResponse(status_code=200, content={"success": True, "data": data})

def error_res(code: str, message: str, status_code: int = 400):
    return JSONResponse(status_code=status_code, content={"success": False, "error": {"code": code, "message": message}})

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_ip = request.client.host if request.client else "127.0.0.1"
    if not abuse.check_rate_limit(client_ip):
        return error_res("RATE_LIMIT_EXCEEDED", "Trop de requêtes. Veuillez patienter une minute.", 429)
    return await call_next(request)

@app.get("/")
@app.get("/health")
@app.get("/api/health")
async def health_check():
    return success_res({"status": "ok", "app": "HintAI", "version": "2.0.0", "gemini_model": "gemini-3.1-flash-lite"})

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        valid, meta, err_code = uploads.validate_and_save_upload(file.filename or "upload", file.content_type or "application/octet-stream", contents)
        if not valid:
            return error_res(err_code or "INVALID_FILE", "Format ou taille de fichier non supporté.")
        return success_res(meta)
    except Exception:
        return error_res("UPLOAD_FAILED", "Erreur lors de l'envoi du fichier.", 500)

@app.post("/api/help-me/start")
async def help_me_start(req: StartAnalysisRequest):
    user_id = req.user_id or "anon_user"
    if not req.exercise_text and not req.file_id:
        return error_res("EMPTY_EXERCISE", "Veuillez saisir un énoncé ou importer un fichier.")
    if not credits.can_spend(user_id, int(Config.COST_ANALYSIS)):
        return error_res("INSUFFICIENT_CREDITS", f"Crédits insuffisants. Il te faut {Config.COST_ANALYSIS} crédits.")
    file_meta = uploads.get_file_meta(req.file_id) if req.file_id else None
    rem = credits.spend(user_id, int(Config.COST_ANALYSIS))
    result = ai.analyze_exercise(req.exercise_text or "", file_meta)
    result["credits_remaining"] = rem
    credits.add_history(user_id, {"type":"help-me","title":result.get("key_concept","Analyse"),"session_id":result["session_id"]})
    return success_res(result)

@app.post("/api/help-me/hint/{level}")
async def help_me_hint(level: int, req: RequestHintRequest):
    if level not in (1,2,3): return error_res("INVALID_HINT_LEVEL", "Niveau d'indice invalide.")
    user_id = req.user_id or "anon_user"
    if not credits.can_spend(user_id, int(Config.COST_HINT)): return error_res("INSUFFICIENT_CREDITS", "Crédits insuffisants.")
    try:
        rem = credits.spend(user_id, int(Config.COST_HINT))
        hint = ai.generate_hint(req.session_id, level)
        return success_res({"session_id":req.session_id,"level":level,"hint":hint,"credits_remaining":rem})
    except ValueError as exc:
        return error_res(str(exc), "Session ou niveau invalide.", 404)

@app.post("/api/help-me/solution")
async def help_me_solution(req: RequestSolutionRequest):
    user_id = req.user_id or "anon_user"
    if not credits.can_spend(user_id, int(Config.COST_SOLUTION)): return error_res("INSUFFICIENT_CREDITS", "Crédits insuffisants.")
    try:
        rem = credits.spend(user_id, int(Config.COST_SOLUTION))
        result = ai.generate_solution(req.session_id)
        result["credits_remaining"] = rem
        return success_res(result)
    except ValueError:
        return error_res("SESSION_NOT_FOUND", "Session introuvable.", 404)

@app.post("/api/learn-concept/start")
async def learn_concept_start(req: LearnConceptRequest):
    user_id = req.user_id or "anon_user"
    if not req.concept.strip(): return error_res("EMPTY_CONCEPT", "Veuillez entrer une notion ou un concept.")
    if not credits.can_spend(user_id, int(Config.COST_LEARN)): return error_res("INSUFFICIENT_CREDITS", "Crédits insuffisants.")
    rem = credits.spend(user_id, int(Config.COST_LEARN))
    result = ai.explain_concept(req.concept.strip(), req.user_level or "Collège / Lycée")
    result["credits_remaining"] = rem
    credits.add_history(user_id, {"type":"learn","title":f"Apprendre : {req.concept}"})
    return success_res(result)

@app.get("/api/user/me")
async def get_current_user(user_id: str = "anon_user"):
    return success_res(user.get_profile(user_id))

@app.get("/api/user/credits")
async def get_user_credits(user_id: str = "anon_user"):
    return success_res({"credits":credits.get_balance(user_id),"is_premium":credits.is_premium(user_id)})

@app.post("/api/user/reward")
async def claim_reward(req: RewardRequest):
    if not Config.REWARDED_ADS_ENABLED:
        return error_res("ADS_DISABLED", "Les publicités récompensées ne sont pas encore activées.", 403)
    user_id=req.user_id or "anon_user"
    new_bal=credits.add(user_id, int(Config.REWARD_CREDITS))
    return success_res({"credits_added":Config.REWARD_CREDITS,"new_balance":new_bal,"message":f"Bravo ! Tu as gagné +{Config.REWARD_CREDITS} crédits !"})

@app.post("/api/auth/register")
async def auth_register(req: AuthRegisterRequest):
    try: return success_res(user.register_user(req.email,req.password,req.name or "Élève",req.anon_user_id))
    except ValueError as exc: return error_res("EMAIL_EXISTS" if str(exc)=="EMAIL_ALREADY_EXISTS" else "REGISTRATION_FAILED", "Un compte existe déjà avec cette adresse email." if str(exc)=="EMAIL_ALREADY_EXISTS" else str(exc))

@app.post("/api/auth/login")
async def auth_login(req: AuthLoginRequest):
    try: return success_res(user.login_user(req.email,req.password))
    except ValueError: return error_res("INVALID_CREDENTIALS", "Email ou mot de passe incorrect.")

@app.post("/api/auth/logout")
async def auth_logout(): return success_res({"message":"Déconnexion réussie"})
