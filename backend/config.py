"""HintAI V2 central configuration."""
from __future__ import annotations
import os
from decimal import Decimal
from dotenv import load_dotenv
load_dotenv()
APP_NAME="HintAI"
APP_VERSION=os.getenv("HINTAI_VERSION","2.0.0")
ENVIRONMENT=os.getenv("ENVIRONMENT","production")
GEMINI_API_KEY=os.getenv("GEMINI_API_KEY")
GEMINI_MODEL="gemini-3.1-flash-lite"
API_PREFIX="/api"
MAX_REQUEST_SIZE_MB=20
MAX_TEXT_LENGTH=12000
MAX_QUESTION_LENGTH=4000
PLAN_CREDITS={"free":20,"basic":40,"pro":80,"pro_plus":150,"super":200,"heavy":300}
PLAN_PRICES_USD={"free":Decimal("0"),"basic":Decimal("5"),"pro":Decimal("10"),"pro_plus":Decimal("15"),"super":Decimal("20"),"heavy":Decimal("30")}
CREDIT_PACK_SIZE=10
CREDIT_PACK_PRICE_USD=Decimal("1")
ACTION_COSTS={"open_help_me":Decimal("0"),"text_input":Decimal("0"),"camera_capture":Decimal("0"),"open_learn_concept":Decimal("0"),"image_upload":Decimal("0.5"),"pdf_upload":Decimal("0.5"),"hint_1":Decimal("1"),"hint_2":Decimal("1"),"hint_3":Decimal("1"),"help_me_analysis":Decimal("2"),"full_solution":Decimal("2"),"learn_initial_explanation":Decimal("2")}
ALLOWED_UPLOAD_TYPES={"image/jpeg","image/png","image/webp","application/pdf"}
MAX_IMAGE_SIZE_MB=15
MAX_PDF_SIZE_MB=20
MAX_UPLOADS_PER_REQUEST=10
UPLOAD_COST=Decimal("0.5")
REWARDED_AD_CREDITS=Decimal("1")
MAX_DAILY_REWARDED_ADS=20
STREAK_ENABLED=True
STREAK_3_DAYS=3
STREAK_3_DAYS_REWARD=Decimal("6")
STREAK_6_DAYS=6
STREAK_6_DAYS_REWARD=Decimal("12")
ALLOWED_ORIGINS=[x.strip() for x in os.getenv("HINTAI_ALLOWED_ORIGINS","*").split(",") if x.strip()]
SUPPORTED_PLANS=tuple(PLAN_CREDITS.keys())
def get_plan_credits(plan:str)->int:return PLAN_CREDITS.get(plan.lower(),20)
def get_action_cost(action:str)->Decimal:
    if action not in ACTION_COSTS: raise ValueError(f"Action inconnue : {action}")
    return ACTION_COSTS[action]
def validate_configuration()->None:
    if not GEMINI_API_KEY: raise RuntimeError("GEMINI_API_KEY est obligatoire.")
    if not GEMINI_MODEL: raise RuntimeError("GEMINI_MODEL est obligatoire.")
