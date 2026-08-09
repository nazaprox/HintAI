
import os
from dotenv import load_dotenv

# Chargement des variables secrètes
load_dotenv()


# ==============================
# GEMINI CONFIGURATION
# ==============================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


if not GEMINI_API_KEY:
    raise ValueError(
        "❌ GEMINI_API_KEY introuvable. "
        "Ajoute-la dans les secrets ou variables environnement."
    )


# Modèle principal HintAI V1
GEMINI_MODEL = "gemini-2.5-flash-lite"


# ==============================
# HINTAI SETTINGS
# ==============================

APP_NAME = "HintAI"

VERSION = "1.0 MVP"


# Matières supportées V1
SUBJECTS = [
    "Mathématiques",
    "Physique",
    "Chimie"
]


# Niveaux scolaires
LEVELS = [
    "6ème",
    "5ème",
    "4ème",
    "3ème",
    "Seconde",
    "Première",
    "Terminale"
]


# ==============================
# CONTEXT CACHE
# ==============================

# Préparation future Gemini Context Caching

CACHE_NAME = "hintai_core_context"


# Durée prévue du cache (sera utilisé plus tard)
CACHE_TTL_SECONDS = 3600
