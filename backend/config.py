"""
HintAI — Configuration V1
=========================

Configuration centralisée de l'application.

Compatible :

* Vercel
* développement local
* FastAPI
* Gemini API

IMPORTANT :
La clé Gemini n'est jamais écrite directement dans ce fichier.

Vercel :
Project Settings
→ Environment Variables
→ GEMINI_API_KEY

Local :
créer un fichier .env contenant :

```
GEMINI_API_KEY=ta_cle_ici
```

"""

from **future** import annotations

import os
from decimal import Decimal
from dotenv import load_dotenv

# ============================================================

# ENVIRONNEMENT

# ============================================================

# Charge .env uniquement lorsqu'il existe.

# Sur Vercel, les variables d'environnement sont déjà disponibles.

load_dotenv()

ENVIRONMENT = os.getenv(
"VERCEL_ENV",
os.getenv(
"ENVIRONMENT",
"development",
),
)

APP_NAME = "HintAI"

APP_VERSION = os.getenv(
"HINTAI_VERSION",
"1.0.0",
)

# ============================================================

# GEMINI

# ============================================================

GEMINI_API_KEY = os.getenv(
"GEMINI_API_KEY"
)

if not GEMINI_API_KEY:
raise RuntimeError(
"GEMINI_API_KEY est absente. "
"Ajoutez-la dans les variables d'environnement "
"de Vercel ou dans votre fichier .env local."
)

GEMINI_MODEL = os.getenv(
"GEMINI_MODEL",
"gemini-3.1-flash-lite",
)

# ============================================================

# API

# ============================================================

API_PREFIX = "/api"

MAX_REQUEST_SIZE_MB = 20

MAX_TEXT_LENGTH = 12000

MAX_QUESTION_LENGTH = 4000

# ============================================================

# CREDITS

# ============================================================

# Crédits mensuels inclus dans chaque abonnement.

PLAN_CREDITS = {
"free": 20,
"basic": 40,
"pro": 80,
"pro_plus": 150,
"super": 200,
"heavy": 300,
}

# ============================================================

# PRIX DES ABONNEMENTS

# ============================================================

# Prix mensuels en dollars US.

PLAN_PRICES_USD = {
"free": Decimal("0"),
"basic": Decimal("5"),
"pro": Decimal("10"),
"pro_plus": Decimal("15"),
"super": Decimal("20"),
"heavy": Decimal("30"),
}

# ============================================================

# PACKS DE CRÉDITS

# ============================================================

# 10 crédits = 1 USD

CREDIT_PACK_SIZE = 10

CREDIT_PACK_PRICE_USD = Decimal("1")

# ============================================================

# COÛT DES ACTIONS

# ============================================================

# Les coûts sont exprimés en demi-crédits afin de permettre

# notamment les uploads à 0,5 crédit.

ACTION_COSTS = {

```
# --------------------------------------------------------
# ACTIONS GRATUITES
# --------------------------------------------------------

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


# --------------------------------------------------------
# 0,5 CRÉDIT
# --------------------------------------------------------

"image_upload": Decimal("0.5"),

"pdf_upload": Decimal("0.5"),


# --------------------------------------------------------
# 1 CRÉDIT
# --------------------------------------------------------

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


# --------------------------------------------------------
# 2 CRÉDITS
# --------------------------------------------------------

"help_me_analysis": Decimal("2"),

"full_solution": Decimal("2"),

"learn_initial_explanation": Decimal("2"),

"difficult_exercise": Decimal("2"),
```

}

# ============================================================

# PUBLICITÉS

# ============================================================

# Publicité simple :

# - 5 secondes

# - aucun crédit gagné

SIMPLE_AD_DURATION_SECONDS = 5

SIMPLE_AD_REWARD_CREDITS = Decimal("0")

# Rewarded Ad :

# - 15 secondes

# - +1 crédit

REWARDED_AD_DURATION_SECONDS = 15

REWARDED_AD_CREDITS = Decimal("1")

# ============================================================

# BONUS DE SÉRIE

# ============================================================

# Une journée n'est validée que lorsqu'une véritable action

# pédagogique est réalisée.

STREAK_ENABLED = True

STREAK_3_DAYS = 3

STREAK_3_DAYS_REWARD = Decimal("6")

STREAK_6_DAYS = 6

STREAK_6_DAYS_REWARD = Decimal("12")

# Actions pouvant valider une journée de série.

#

# Les actions purement visuelles ou locales ne comptent pas.

STREAK_ELIGIBLE_ACTIONS = {
"help_me_analysis",
"hint_1",
"hint_2",
"hint_3",
"ai_question",
"full_solution",
"evaluation_exercise",
"work_correction",
"evaluation_question",
"evaluation_hint",
"learn_initial_explanation",
"learn_question",
"learn_hint",
"easy_exercise",
"difficult_exercise",
"exercise_correction",
"new_explanation",
"document_ai_analysis",
}

# ============================================================

# UPLOADS

# ============================================================

# 2 uploads = 1 crédit.

UPLOADS_PER_CREDIT = 2

UPLOAD_COST = Decimal("0.5")

ALLOWED_UPLOAD_TYPES = {
"image/jpeg",
"image/png",
"image/webp",
"application/pdf",
}

# ============================================================

# LIMITES DE SÉCURITÉ

# ============================================================

MAX_IMAGE_SIZE_MB = 15

MAX_PDF_SIZE_MB = 20

MAX_UPLOADS_PER_REQUEST = 10

MAX_DAILY_REWARDED_ADS = 20

# ============================================================

# CORS

# ============================================================

# En développement, "*" facilite les tests.

#

# En production, définir :

#

# HINTAI_ALLOWED_ORIGINS=

# https://ton-domaine.com,https://www.ton-domaine.com

_allowed_origins = os.getenv(
"HINTAI_ALLOWED_ORIGINS",
"*",
)

ALLOWED_ORIGINS = [
origin.strip()
for origin in _allowed_origins.split(",")
if origin.strip()
]

# ============================================================

# VERCEL

# ============================================================

IS_VERCEL = bool(
os.getenv("VERCEL")
)

VERCEL_ENV = os.getenv(
"VERCEL_ENV",
"development",
)

# ============================================================

# VALIDATION

# ============================================================

SUPPORTED_PLANS = tuple(
PLAN_CREDITS.keys()
)

def get_plan_credits(
plan: str,
) -> int:
"""
Retourne le nombre de crédits mensuels
correspondant à un abonnement.
"""

```
return PLAN_CREDITS.get(
    plan.lower(),
    PLAN_CREDITS["free"],
)
```

def get_action_cost(
action: str,
) -> Decimal:
"""
Retourne le coût d'une action.
"""

```
if action not in ACTION_COSTS:
    raise ValueError(
        f"Action inconnue : {action}"
    )

return ACTION_COSTS[action]
```

def is_streak_action(
action: str,
) -> bool:
"""
Vérifie si une action valide une journée de série.
"""

```
return (
    STREAK_ENABLED
    and action in STREAK_ELIGIBLE_ACTIONS
)
```

def validate_configuration() -> None:
"""
Vérifie la configuration essentielle.
"""

```
if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY est obligatoire."
    )

if not GEMINI_MODEL:
    raise RuntimeError(
        "GEMINI_MODEL est obligatoire."
    )
```

# Vérification au chargement.

validate_configuration()
