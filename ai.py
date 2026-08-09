from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    SYSTEM_PROMPT,
)


# ============================================================
# CLIENT GEMINI
# ============================================================

if not GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY est absente des Secrets Streamlit."
    )

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# CONTEXT CACHE
# ============================================================

_cached_content_name = None


def create_hintai_cache():
    """
    Crée le contexte pédagogique HintAI pour Gemini.

    Le cache contient les règles permanentes du professeur.
    Les exercices et les images des utilisateurs ne sont
    PAS placés dans ce cache.
    """

    global _cached_content_name

    # Si le cache existe déjà dans cette session,
    # on le réutilise.
    if _cached_content_name:
        return _cached_content_name

    try:

        cached_content = client.caches.create(
            model=GEMINI_MODEL,

            config=types.CreateCachedContentConfig(
                display_name="hintai-pedagogical-context",

                system_instruction=SYSTEM_PROMPT,

                ttl="3600s",
            ),
        )

        _cached_content_name = cached_content.name

        return _cached_content_name

    except Exception as e:

        print(
            f"[HintAI] Cache indisponible : {e}"
        )

        return None


# ============================================================
# CONFIGURATION GEMINI
# ============================================================

def get_generate_config(
    cache_name=None,
    temperature=0.4,
):
    """
    Configuration commune des appels Gemini.
    """

    return types.GenerateContentConfig(
        temperature=temperature,

        cached_content=cache_name,

        response_mime_type="text/plain",
    )


# ============================================================
# TEXTE
# ============================================================

def ask_gemini(
    prompt,
    temperature=0.4,
):
    """
    Envoie une demande texte à Gemini.

    Le contexte pédagogique HintAI est réutilisé
    grâce au Context Cache lorsqu'il est disponible.
    """

    cache_name = create_hintai_cache()

    config = get_generate_config(
        cache_name=cache_name,
        temperature=temperature,
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=config,
    )

    return response.text


# ============================================================
# IMAGE + TEXTE
# ============================================================

def analyze_image(
    image_bytes,
    mime_type,
    prompt,
    temperature=0.4,
):
    """
    Envoie une image + une instruction à Gemini.

    Le contrôle qualité de l'image est effectué
    AVANT cette fonction par notre application.
    """

    cache_name = create_hintai_cache()

    image_part = types.Part.from_bytes(
        data=image_bytes,
        mime_type=mime_type,
    )

    config = get_generate_config(
        cache_name=cache_name,
        temperature=temperature,
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,

        contents=[
            image_part,
            prompt,
        ],

        config=config,
    )

    return response.text


# ============================================================
# HELP ME
# ============================================================

def help_me(
    exercise_text,
    student_work_text="",
    subject="Mathématiques",
    level="3ème",
):
    """
    Première analyse d'un exercice.

    L'objectif est de produire l'Indice 1,
    pas de donner directement la solution.
    """

    prompt = f"""
MODE : HELP ME

Matière :
{subject}

Niveau :
{level}

ÉNONCÉ :
{exercise_text}

TRAVAIL DE L'ÉLÈVE :
{student_work_text if student_work_text else "Aucun travail fourni."}

Commence l'accompagnement.

Tu dois :

1. Comprendre l'exercice.
2. Identifier la compétence nécessaire.
3. Observer le travail de l'élève s'il existe.
4. Signaler uniquement les erreurs évidentes.
5. Donner UNIQUEMENT l'INDICE 1.
6. Ne donne pas la solution complète.
7. Termine par une question courte qui pousse
   l'élève à réfléchir.

Réponds en français.
"""

    return ask_gemini(prompt)


# ============================================================
# HELP ME AVEC IMAGE
# ============================================================

def help_me_image(
    exercise_image,
    exercise_mime,
    student_image=None,
    student_mime=None,
    subject="Mathématiques",
    level="3ème",
):
    """
    Analyse l'exercice photographié.

    L'image de l'exercice est envoyée à Gemini seulement
    après le contrôle qualité local.
    """

    cache_name = create_hintai_cache()

    contents = []

    # Image exercice
    contents.append(
        types.Part.from_bytes(
            data=exercise_image,
            mime_type=exercise_mime,
        )
    )

    # Travail de l'élève, optionnel
    if student_image and student_mime:
        contents.append(
            types.Part.from_bytes(
                data=student_image,
                mime_type=student_mime,
            )
        )

    prompt = f"""
MODE : HELP ME

Matière :
{subject}

Niveau :
{level}

La première image est l'énoncé de l'exercice.

S'il existe une deuxième image,
elle représente le travail de l'élève.

Analyse les images avec attention.

Tu dois :

1. Comprendre l'énoncé.
2. Identifier la compétence travaillée.
3. Examiner le travail de l'élève.
4. Repérer les erreurs importantes.
5. Donner uniquement l'INDICE 1.
6. Ne donne pas encore la résolution.
7. Fais réfléchir l'élève.
8. Termine par une question.

Si une information essentielle est illisible,
indique précisément ce qui doit être photographié
à nouveau.

Réponds en français.
"""

    contents.append(prompt)

    config = get_generate_config(
        cache_name=cache_name,
        temperature=0.4,
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=config,
    )

    return response.text


# ============================================================
# INDICES SUIVANTS
# ============================================================

def next_hint(
    exercise_context,
    previous_response,
    hint_level,
    student_message="",
):
    """
    Génère l'indice suivant.

    hint_level :
    1 = indice léger
    2 = indice intermédiaire
    3 = indice très guidé
    4 = résolution complète
    """

    cache_name = create_hintai_cache()

    if hint_level == 2:

        instruction = """
Donne l'INDICE 2.

Sois plus précis que l'indice précédent,
mais ne donne toujours pas toute la solution.
"""

    elif hint_level == 3:

        instruction = """
Donne l'INDICE 3.

Guide fortement l'élève vers la démarche,
mais laisse-lui encore une partie du raisonnement.
"""

    else:

        instruction = """
Donne maintenant la RÉSOLUTION COMPLÈTE.

Explique chaque étape clairement.
Montre les calculs.
Explique pourquoi chaque étape est utilisée.
Puis donne une meilleure méthode si elle existe.
"""

    prompt = f"""
MODE : PROGRESSION HELP ME

EXERCICE :
{exercise_context}

RÉPONSE PRÉCÉDENTE :
{previous_response}

MESSAGE DE L'ÉLÈVE :
{student_message}

{instruction}

Ne répète pas inutilement les informations déjà données.

Réponds en français.
"""

    config = get_generate_config(
        cache_name=cache_name,
        temperature=0.35,
    )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=config,
    )

    return response.text


# ============================================================
# QUESTION DE L'ÉLÈVE
# ============================================================

def ask_student_question(
    exercise_context,
    question,
):
    """
    Répond à une question de l'élève sans révéler
    inutilement la solution.
    """

    prompt = f"""
MODE : QUESTION DE L'ÉLÈVE

EXERCICE :
{exercise_context}

QUESTION :
{question}

Réponds comme un professeur particulier.

Si possible :
- réponds à la question,
- donne une petite explication,
- puis renvoie l'élève vers son propre raisonnement.

Ne donne pas automatiquement toute la solution.
"""

    return ask_gemini(prompt)


# ============================================================
# VALIDATION DE COMPÉTENCE
# ============================================================

def validate_skill(
    exercise_context,
    student_answer,
    subject="Mathématiques",
    level="3ème",
):
    """
    Évalue la maîtrise de la compétence après
    le travail de l'élève.
    """

    prompt = f"""
MODE : VALIDATION DE COMPÉTENCE

Matière :
{subject}

Niveau :
{level}

EXERCICE :
{exercise_context}

RÉPONSE DE L'ÉLÈVE :
{student_answer}

Évalue :

1. Compréhension
2. Méthode
3. Calculs / raisonnement
4. Résultat
5. Compétence réellement maîtrisée

Donne :

- une note indicative sur 10,
- les points réussis,
- les erreurs,
- ce qui doit être amélioré,
- un conseil précis,
- un petit exercice de validation.

Réponds en français.
"""

    return ask_gemini(prompt)


# ============================================================
# LEARN A CONCEPT
# ============================================================

def learn_concept(
    concept,
    level,
    subject="Mathématiques",
):
    """
    Mode apprentissage d'une notion.
    """

    prompt = f"""
MODE : LEARN A CONCEPT

Matière :
{subject}

Niveau :
{level}

CONCEPT :
{concept}

Enseigne cette notion comme un professeur particulier.

Structure :

1. Explication simple
2. Idée fondamentale
3. Exemple guidé
4. Erreur fréquente
5. Petit exercice
6. Question à l'élève

Ne donne pas immédiatement la réponse au petit exercice.

Adapte le niveau à l'élève.
Réponds en français.
"""

    return ask_gemini(prompt)


# ============================================================
# TEST DE CONNEXION
# ============================================================

def test_connection():
    """
    Vérifie que Gemini répond correctement.
    """

    response = ask_gemini(
        "Réponds uniquement : HintAI connecté."
    )

    return response