"""HintAI V2 central configuration."""

from __future__ import annotations

import os
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

APP_NAME = "HintAI"
APP_VERSION = os.getenv("HINTAI_VERSION", "2.0.0")
ENVIRONMENT = os.getenv("ENVIRONMENT", os.getenv("VERCEL_ENV", "development"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

API_PREFIX = "/api"
MAX_REQUEST_SIZE_MB = 20
MAX_TEXT_LENGTH = 12000
MAX_QUESTION_LENGTH = 4000

PLAN_CREDITS = {
    "free": 20,
    "basic": 40,
    "pro": 80,
    "pro_plus": 150,
    "super": 200,
    "heavy": 300,
}

PLAN_PRICES_USD = {
    "free": Decimal("0"),
    "basic": Decimal("5"),
    "pro": Decimal("10"),
    "pro_plus": Decimal("15"),
    "super": Decimal("20"),
    "heavy": Decimal("30"),
}

CREDIT_PACK_SIZE = 10
CREDIT_PACK_PRICE_USD = Decimal("1")

ACTION_COSTS = {
    "open_help_me": Decimal("0"),
    "text_input": Decimal("0"),
    "camera_capture": Decimal("0"),
    "local_quality_check": Decimal("0"),
    "local_crop": Decimal("0"),
    "local_image_enhancement": Decimal("0"),
    "open_learn_concept": Decimal("0"),
    "local_history": Decimal("0"),
    "authentication": Decimal("0"),
    "history_view": Decimal("0"),
    "cached_response_view": Decimal("0"),
    "image_upload": Decimal("0.5"),
    "pdf_upload": Decimal("0.5"),
    "hint_1": Decimal("1"),
    "hint_2": Decimal("1"),
    "hint_3": Decimal("1"),
    "ai_question": Decimal("1"),
    "evaluation_exercise": Decimal("1"),
    "work_correction": Decimal("1"),
    "evaluation_question": Decimal("1"),
    "evaluation_hint": Decimal("1"),
    "learn_question": Decimal("1"),
    "learn_hint": Decimal("1"),
    "easy_exercise": Decimal("1"),
    "exercise_correction": Decimal("1"),
    "new_explanation": Decimal("1"),
    "document_ai_analysis": Decimal("1"),
    "help_me_analysis": Decimal("2"),
    "full_solution": Decimal("2"),
    "learn_initial_explanation": Decimal("2"),
    "difficult_exercise": Decimal("2"),
}

SIMPLE_AD_DURATION_SECONDS = 5
SIMPLE_AD_REWARD_CREDITS = Decimal("0")
REWARDED_AD_DURATION_SECONDS = 15
REWARDED_AD_CREDITS = Decimal("1")
MAX_DAILY_REWARDED_ADS = 20

STREAK_ENABLED = True
STREAK_3_DAYS = 3
STREAK_3_DAYS_REWARD = Decimal("6")
STREAK_6_DAYS = 6
STREAK_6_DAYS_REWARD = Decimal("12")

STREAK_ELIGIBLE_ACTIONS = {
    "help_me_analysis", "hint_1", "hint_2", "hint_3", "ai_question",
    "full_solution", "evaluation_exercise", "work_correction",
    "evaluation_question", "evaluation_hint", "learn_initial_explanation",
    "learn_question", "learn_hint", "easy_exercise", "difficult_exercise",
    "exercise_correction", "new_explanation", "document_ai_analysis",
}

UPLOADS_PER_CREDIT = 2
UPLOAD_COST = Decimal("0.5")
ALLOWED_UPLOAD_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}
MAX_IMAGE_SIZE_MB = 15
MAX_PDF_SIZE_MB = 20
MAX_UPLOADS_PER_REQUEST = 10

_allowed_origins = os.getenv("HINTAI_ALLOWED_ORIGINS", "*")
ALLOWED_ORIGINS = [x.strip() for x in _allowed_origins.split(",") if x.strip()]

IS_VERCEL = bool(os.getenv("VERCEL"))
VERCEL_ENV = os.getenv("VERCEL_ENV", "development")

SUPPORTED_PLANS = tuple(PLAN_CREDITS.keys())


def get_plan_credits(plan: str) -> int:
    return PLAN_CREDITS.get(plan.lower(), PLAN_CREDITS["free"])


def get_action_cost(action: str) -> Decimal:
    if action not in ACTION_COSTS:
        raise ValueError(f"Action inconnue : {action}")
    return ACTION_COSTS[action]


def is_streak_action(action: str) -> bool:
    return STREAK_ENABLED and action in STREAK_ELIGIBLE_ACTIONS


def validate_configuration() -> None:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY est obligatoire.")
    if not GEMINI_MODEL:
        raise RuntimeError("GEMINI_MODEL est obligatoire.")


# La validation est volontairement désactivée au démarrage afin que les
# routes de santé puissent fonctionner même si la clé n'est pas encore configurée.
