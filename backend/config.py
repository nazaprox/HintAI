"""HintAI V2 central configuration."""
from __future__ import annotations
import os
from decimal import Decimal
from dotenv import load_dotenv
load_dotenv()
APP_NAME="HintAI"; APP_VERSION=os.getenv("HINTAI_VERSION","2.0.0"); ENVIRONMENT=os.getenv("ENVIRONMENT","production")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY"); GEMINI_MODEL="gemini-3.1-flash-lite"; API_PREFIX="/api"
INITIAL_FREE_CREDITS=20; COST_ANALYSIS=2; COST_HINT=1; COST_SOLUTION=2; COST_LEARN=2; REWARD_CREDITS=5; MAX_REQUESTS_PER_MINUTE=30
PAYMENT_ENABLED=os.getenv("PAYMENT_ENABLED","false").lower()=="true"; ADS_ENABLED=os.getenv("ADS_ENABLED","false").lower()=="true"; REWARDED_ADS_ENABLED=os.getenv("REWARDED_ADS_ENABLED","false").lower()=="true"
PAYMENT_PROVIDER=os.getenv("PAYMENT_PROVIDER",""); PAYMENT_SECRET_KEY=os.getenv("PAYMENT_SECRET_KEY",""); PAYMENT_WEBHOOK_SECRET=os.getenv("PAYMENT_WEBHOOK_SECRET","")
PLAN_CREDITS={"free":20,"basic":40,"pro":80,"pro_plus":150,"super":200,"heavy":300}; PLAN_PRICES_USD={"free":Decimal("0"),"basic":Decimal("5"),"pro":Decimal("10"),"pro_plus":Decimal("15"),"super":Decimal("20"),"heavy":Decimal("30")}
CREDIT_PACK_SIZE=10; CREDIT_PACK_PRICE_USD=Decimal("1")
ACTION_COSTS={"open_help_me":Decimal("0"),"text_input":Decimal("0"),"camera_capture":Decimal("0"),"open_learn_concept":Decimal("0"),"image_upload":Decimal("0.5"),"pdf_upload":Decimal("0.5"),"hint_1":Decimal("1"),"hint_2":Decimal("1"),"hint_3":Decimal("1"),"help_me_analysis":Decimal("2"),"full_solution":Decimal("2"),"learn_initial_explanation":Decimal("2")}
ALLOWED_UPLOAD_TYPES={"image/jpeg","image/png","image/webp","application/pdf"}; MAX_IMAGE_SIZE_MB=15; MAX_PDF_SIZE_MB=20; MAX_IMAGE_SIZE_BYTES=15*1024*1024; MAX_PDF_SIZE_BYTES=20*1024*1024; ALLOWED_IMAGE_MIME_TYPES=["image/jpeg","image/jpg","image/png","image/webp"]; ALLOWED_PDF_MIME_TYPES=["application/pdf"]; MAX_UPLOADS_PER_REQUEST=10; UPLOAD_COST=Decimal("0.5")
REWARDED_AD_CREDITS=Decimal("5"); MAX_DAILY_REWARDED_ADS=20; REWARD_CREDITS=5
STREAK_ENABLED=True; STREAK_3_DAYS=3; STREAK_3_DAYS_REWARD=Decimal("6"); STREAK_6_DAYS=6; STREAK_6_DAYS_REWARD=Decimal("12")
ALLOWED_ORIGINS=[x.strip() for x in os.getenv("HINTAI_ALLOWED_ORIGINS","*").split(",") if x.strip()]; SUPPORTED_PLANS=tuple(PLAN_CREDITS.keys())
def get_plan_credits(plan:str)->int:return PLAN_CREDITS.get(plan.lower(),20)
def get_action_cost(action:str)->Decimal:
    if action not in ACTION_COSTS: raise ValueError(f"Action inconnue : {action}")
    return ACTION_COSTS[action]
def is_streak_action(action:str)->bool:return action in {"help_me_analysis","learn_initial_explanation","full_solution","hint_1","hint_2","hint_3"}
def validate_configuration()->None:
    if not GEMINI_API_KEY: raise RuntimeError("GEMINI_API_KEY est obligatoire.")
