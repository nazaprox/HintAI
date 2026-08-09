import streamlit as st


# ============================================================
# HINTAI - CONFIGURATION V1
# ============================================================

# -----------------------------
# GEMINI
# -----------------------------

GEMINI_MODEL = "gemini-2.5-flash-lite"

try:
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except Exception:
    GEMINI_API_KEY = ""


# -----------------------------
# APPLICATION
# -----------------------------

APP_NAME = "HintAI"
APP_VERSION = "1.0.0"


# -----------------------------
# CREDITS
# -----------------------------

FREE_INITIAL_CREDITS = 30

# Coût des principales actions
HELP_ME_COST = 10
LEARN_CONCEPT_COST = 8
EXTRA_QUESTION_COST = 1


# -----------------------------
# LIMITES
# -----------------------------

# Protection supplémentaire contre
# les utilisations accidentelles.
MAX_IMAGE_SIZE_MB = 10

MAX_HISTORY_ITEMS = 50


# -----------------------------
# MATIÈRES
# -----------------------------

SUBJECTS = [
    "Mathématiques",
    "Physique",
    "Chimie",
]


# -----------------------------
# NIVEAUX
# -----------------------------

CLASS_LEVELS = [
    "6ème",
    "5ème",
    "4ème",
    "3ème",
    "Seconde",
    "Première",
    "Terminale",
]


# -----------------------------
# FORMULES
# -----------------------------

PLANS = {
    "Free": {
        "credits": 30,
        "ads": True,
    },

    "Pro 200": {
        "credits": 200,
        "price": 5,
        "ads": False,
    },

    "Pro 400": {
        "credits": 400,
        "price": 10,
        "ads": False,
    },

    "Pro 700": {
        "credits": 700,
        "price": 15,
        "ads": False,
    },
}


# -----------------------------
# PUBLICITÉ
# -----------------------------

ADS_ENABLED = True

REWARDED_AD_CREDIT_REWARD = 3


# -----------------------------
# PROMPT PÉDAGOGIQUE
# -----------------------------

SYSTEM_PROMPT = """
Tu es HintAI, un professeur particulier spécialisé
dans l'accompagnement scolaire.

Matières principales :
- Mathématiques
- Physique
- Chimie

Ton objectif n'est PAS de donner immédiatement la réponse.

Tu dois aider l'élève à développer une compétence.

RÈGLES PÉDAGOGIQUES :

1. Commence par comprendre l'exercice.

2. Analyse le travail de l'élève lorsqu'il en fournit un.

3. Ne donne jamais directement la solution au premier message.

4. Commence par un indice progressif.

5. L'indice 1 doit être léger et pousser l'élève
   à réfléchir.

6. Si l'élève demande de l'aide supplémentaire,
   donne un indice plus précis.

7. L'indice 3 peut être beaucoup plus guidé,
   mais évite encore de faire tout le raisonnement
   à la place de l'élève.

8. La résolution complète n'est donnée que lorsque
   l'élève demande la résolution ou lorsqu'il est
   arrivé au dernier niveau d'aide.

9. Explique les erreurs présentes dans le travail
   de l'élève sans le rabaisser.

10. Après la résolution, évalue la compétence.

11. Donne une meilleure méthode lorsque cela est utile.

12. Propose éventuellement un petit exercice
    de validation.

13. Adapte toujours les explications au niveau scolaire
    indiqué par l'élève.

14. Utilise un français clair, naturel et pédagogique.

15. Ne prétends jamais avoir lu une information
    qui n'est pas présente dans l'image ou le texte.

16. Si une image est illisible ou incomplète,
    demande une nouvelle photo.

FORMAT DE RÉPONSE :

Pour Help Me, structure la réponse avec :

- compréhension de l'exercice
- indice actuel
- question à l'élève
- prochaine action possible

Pour une correction finale :

- démarche
- erreurs éventuelles
- résolution
- meilleure méthode
- compétence évaluée
- conseil de progression
"""


# -----------------------------
# VALIDATION
# -----------------------------

def validate_config():
    """
    Vérifie que la configuration minimale
    de HintAI est correcte.
    """

    errors = []

    if not GEMINI_API_KEY:
        errors.append(
            "GEMINI_API_KEY n'est pas configurée."
        )

    if not GEMINI_MODEL:
        errors.append(
            "Le modèle Gemini n'est pas configuré."
        )

    return errors