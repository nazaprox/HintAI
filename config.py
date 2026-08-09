import os


# ============================================================
# GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Gemini 2.5 Flash-Lite étant refusé pour ta clé actuelle,
# on utilise le modèle de remplacement.
GEMINI_MODEL = "gemini-3.1-flash-lite"


# ============================================================
# HINTAI
# ============================================================

APP_NAME = "HintAI"

FREE_MONTHLY_CREDITS = 30


# ============================================================
# OFFRES
# ============================================================

PREMIUM_PACKAGES = {
    "5$": {
        "price": 5,
        "credits": 200,
    },
    "10$": {
        "price": 10,
        "credits": 400,
    },
    "15$": {
        "price": 15,
        "credits": 700,
    },
    "30$": {
        "price": 30,
        "help_me": 2,
        "questions_per_day": 5,
    },
}


# ============================================================
# COUTS EN CREDITS
# ============================================================

CREDIT_COSTS = {
    "help_me": 5,
    "question": 1,
    "evaluation": 3,
    "concept": 3,
    "paper": 3,
}


# ============================================================
# GAMIFICATION
# ============================================================

DAILY_LOGIN_REWARDS = {
    1: 0,
    2: 2,
    3: 3,
    4: 4,
    5: 5,
    6: 6,
    7: 10,
}


# ============================================================
# AUTHENTIFICATION
# ============================================================

GOOGLE_AUTH_ENABLED = True


# ============================================================
# CONTEXT CACHE
# ============================================================

CACHE_ENABLED = True

HINTAI_SYSTEM_CONTEXT = """
Tu es HintAI, un professeur particulier spécialisé
dans l'accompagnement pédagogique des élèves.

Matières principales :
- Mathématiques
- Physique
- Chimie

REGLE PEDAGOGIQUE FONDAMENTALE :

Tu ne dois pas donner immédiatement la réponse finale.

Ton objectif est de faire progresser l'élève vers
une compétence réelle.

Utilise progressivement :

1. observation
2. question
3. indice 1
4. indice 2
5. indice 3
6. démarche guidée
7. résolution complète uniquement si nécessaire
8. vérification de compréhension
9. exercice de validation

Tu dois adapter ton explication au niveau scolaire
de l'élève.

Si l'élève se trompe, explique pourquoi sans le
décourager.

Si l'élève demande directement la réponse,
continue d'abord par une aide pédagogique,
sauf lorsqu'une résolution complète est explicitement
autorisée par le parcours HintAI.

Les figures, tableaux, schémas et écritures
mathématiques présents dans les images doivent être
pris en compte.

Réponds en français.
"""