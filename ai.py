from google import genai
from google.genai import types

from config import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
    HINTAI_SYSTEM_CONTEXT,
    CACHE_ENABLED,
)


# ============================================================
# CLIENT
# ============================================================

if not GEMINI_API_KEY:

    raise RuntimeError(
        "GEMINI_API_KEY est absente."
    )


client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ============================================================
# CACHE CONTEXTE
# ============================================================

_cached_context = None


def get_cached_context():

    global _cached_context

    if not CACHE_ENABLED:

        return None

    if _cached_context is not None:

        return _cached_context

    try:

        cache = client.caches.create(
            model=GEMINI_MODEL,
            config=types.CreateCachedContentConfig(
                display_name="hintai_core_context",
                system_instruction=HINTAI_SYSTEM_CONTEXT,
                ttl="3600s",
            ),
        )

        _cached_context = cache.name

        return _cached_context

    except Exception:

        # Le fonctionnement de HintAI ne dépend pas
        # entièrement du cache.
        return None


# ============================================================
# TEXTE
# ============================================================

def ask_gemini(
    prompt,
    system_instruction=None,
):

    context_cache = get_cached_context()

    if context_cache:

        config = types.GenerateContentConfig(
            cached_content=context_cache
        )

    else:

        config = types.GenerateContentConfig(
            system_instruction=(
                system_instruction
                if system_instruction
                else HINTAI_SYSTEM_CONTEXT
            )
        )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=config,
    )

    return response.text


# ============================================================
# IMAGE
# ============================================================

def analyze_image(
    image_file,
    prompt,
    system_instruction=None,
):

    data = image_file.getvalue()

    mime_type = getattr(
        image_file,
        "type",
        "image/jpeg"
    )

    image_part = types.Part.from_bytes(
        data=data,
        mime_type=mime_type,
    )

    context_cache = get_cached_context()

    if context_cache:

        config = types.GenerateContentConfig(
            cached_content=context_cache
        )

    else:

        config = types.GenerateContentConfig(
            system_instruction=(
                system_instruction
                if system_instruction
                else HINTAI_SYSTEM_CONTEXT
            )
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

def analyze_exercise(
    exercise_file,
    work_file=None,
    student_class="Non précisée",
):

    prompt = f"""
Analyse cet exercice pour HintAI.

Classe :
{student_class}

Tu dois identifier :

- matière
- chapitre
- compétence recherchée
- données importantes
- objectif
- difficulté
- éventuelle erreur dans le travail de l'élève

IMPORTANT :

Ne donne PAS directement la réponse.

Prépare un parcours pédagogique.

Retourne exactement :

MATIERE:
...

CONCEPT:
...

COMPETENCE:
...

BLOCAGE:
...

INDICE_1:
...

INDICE_2:
...

INDICE_3:
...

RESOLUTION:
...

EVALUATION:
...

L'indice 1 doit être très léger.
L'indice 2 doit être plus précis.
L'indice 3 doit presque permettre de trouver
la démarche.

La résolution complète est réservée à la fin.
"""

    if work_file is not None:

        work_data = work_file.getvalue()

        work_part = types.Part.from_bytes(
            data=work_data,
            mime_type=getattr(
                work_file,
                "type",
                "image/jpeg"
            ),
        )

        contents = [
            image_part_for(exercise_file),
            work_part,
            prompt,
        ]

    else:

        contents = [
            image_part_for(exercise_file),
            prompt,
        ]

    context_cache = get_cached_context()

    if context_cache:

        config = types.GenerateContentConfig(
            cached_content=context_cache
        )

    else:

        config = types.GenerateContentConfig(
            system_instruction=HINTAI_SYSTEM_CONTEXT
        )

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=contents,
        config=config,
    )

    return response.text


def image_part_for(file):

    return types.Part.from_bytes(
        data=file.getvalue(),
        mime_type=getattr(
            file,
            "type",
            "image/jpeg"
        ),
    )


# ============================================================
# QUESTION ELEVE
# ============================================================

def ask_student_question(
    exercise_context,
    question,
):

    prompt = f"""
CONTEXTE DE L'EXERCICE :

{exercise_context}

QUESTION DE L'ELEVE :

{question}

Réponds comme un professeur particulier.

Ne donne pas immédiatement la réponse finale.

Réponds à la question de l'élève et aide-le
à franchir l'obstacle.

Si sa question demande la solution directe,
donne plutôt une piste permettant de la trouver.
"""

    return ask_gemini(prompt)


# ============================================================
# APPRENDRE UN CONCEPT
# ============================================================

def learn_concept(
    concept,
    student_class,
):

    prompt = f"""
L'élève est en classe :
{student_class}

Il veut apprendre :
{concept}

Construis une mini-séquence pédagogique.

Elle doit contenir :

1. Explication simple
2. Exemple
3. Question à l'élève
4. Exercice guidé
5. Indice
6. Correction
7. Exercice de validation
8. Compétence vérifiée

Ne fais pas seulement un cours théorique.
Le but est que l'élève sache utiliser la compétence.
"""

    return ask_gemini(prompt)