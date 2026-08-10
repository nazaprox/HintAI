````python
"""
HintAI — AI Engine
==================

Moteur IA central de HintAI.

Responsabilités :
- communication avec Gemini
- génération des indices 1 → 3
- résolution complète
- réponses aux questions de l'élève
- Learn a Concept
- génération d'exercices
- vérification pédagogique
- prompts structurés
- préparation du prompt caching
- streaming des réponses

Le fichier ne gère PAS :
- authentification
- crédits
- stockage
- contrôle qualité des images
- routes HTTP

Ces responsabilités appartiennent aux autres modules.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Generator, Iterable, Optional

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


# ============================================================
# CONFIGURATION GEMINI
# ============================================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

# Modèle principal.
#
# IMPORTANT :
# Le nom exact du modèle peut être changé uniquement
# depuis la variable d'environnement.
#
# Cela évite de modifier le code lors d'un changement
# de modèle côté Google.
GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.1-flash-lite",
)


# ============================================================
# CLIENT GEMINI
# ============================================================

_client = None


def get_client():
    """
    Initialise le client Gemini une seule fois.

    Le client est conservé en mémoire pendant la durée de vie
    du processus serverless lorsque Vercel réutilise l'instance.
    """

    global _client

    if _client is not None:
        return _client

    if genai is None:
        raise RuntimeError(
            "Le package google-genai n'est pas installé."
        )

    if not GEMINI_API_KEY:
        raise RuntimeError(
            "GEMINI_API_KEY n'est pas configurée."
        )

    _client = genai.Client(
        api_key=GEMINI_API_KEY
    )

    return _client


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
Tu es HintAI, un tuteur pédagogique intelligent.

Ta mission n'est PAS simplement de donner la réponse.

Tu dois aider l'élève à comprendre et à progresser.

RÈGLES PÉDAGOGIQUES :

1. Ne donne jamais immédiatement la solution complète
   lorsqu'un indice est demandé.

2. Les indices doivent être progressifs.

3. Indice 1 :
   - très léger
   - oriente l'élève
   - ne révèle pas directement la méthode complète.

4. Indice 2 :
   - explique davantage la méthode
   - peut rappeler une formule ou une propriété
   - ne fait toujours pas tout l'exercice.

5. Indice 3 :
   - presque toute la démarche est guidée
   - l'élève doit encore pouvoir comprendre
     pourquoi chaque étape est effectuée.

6. Résolution complète :
   - toutes les étapes
   - calculs détaillés
   - justification
   - résultat final clairement indiqué.

7. Si l'élève pose une question :
   - réponds précisément à sa question
   - reste pédagogique
   - ne donne pas inutilement toute la solution.

8. Utilise le niveau réel de l'élève.
   Évite le jargon inutile.

9. Pour les mathématiques :
   - vérifie les calculs
   - vérifie les signes
   - vérifie les unités
   - vérifie la cohérence du résultat.

10. Pour les sciences :
    - explique les lois utilisées
    - indique les unités
    - justifie les étapes.

11. Pour les langues :
    - explique la grammaire
    - corrige sans humilier.

12. Si l'énoncé est ambigu ou illisible :
    indique précisément ce qui manque.

13. Ne prétends jamais avoir vu une information
    qui n'est pas présente dans l'entrée.

STYLE :

- clair
- encourageant
- concis mais suffisamment détaillé
- adapté à un élève
- jamais condescendant

Tu dois favoriser l'apprentissage actif.
"""


# ============================================================
# PROMPTS HELP ME
# ============================================================

def build_help_me_prompt(
    problem: str,
    level: int = 1,
    context: Optional[str] = None,
) -> str:
    """
    Construit le prompt pour Help Me.
    """

    if level == 1:
        instruction = """
Donne uniquement un INDICE 1.

L'indice doit orienter l'élève vers la première
idée utile sans effectuer la résolution.
"""

    elif level == 2:
        instruction = """
Donne uniquement un INDICE 2.

L'élève a besoin d'une aide plus importante.
Explique la méthode ou la propriété pertinente,
mais ne réalise pas encore toute la résolution.
"""

    elif level == 3:
        instruction = """
Donne uniquement un INDICE 3.

Guide presque complètement l'élève à travers
la démarche, mais garde une logique pédagogique
qui lui permet de comprendre et de participer.
"""

    else:
        raise ValueError(
            "Le niveau d'indice doit être 1, 2 ou 3."
        )

    context_block = ""

    if context:
        context_block = f"""
CONTEXTE FOURNI PAR L'ÉLÈVE :

{context}
"""

    return f"""
{instruction}

ÉNONCÉ :

{problem}

{context_block}

Ne donne pas de résolution complète.
"""


def build_solution_prompt(
    problem: str,
) -> str:
    """
    Prompt pour la résolution complète.
    """

    return f"""
Résous complètement l'exercice suivant.

ÉNONCÉ :

{problem}

FORMAT :

1. Compréhension de l'énoncé
2. Données utiles
3. Méthode
4. Calculs / raisonnement étape par étape
5. Vérification
6. Réponse finale

Explique chaque étape pédagogiquement.
"""


def build_question_prompt(
    problem: str,
    question: str,
    previous_context: Optional[str] = None,
) -> str:
    """
    Prompt pour une question pendant une session.
    """

    context = ""

    if previous_context:
        context = f"""
CONTEXTE DE LA SESSION :

{previous_context}
"""

    return f"""
L'élève travaille sur cet exercice :

{problem}

{context}

Il pose maintenant cette question :

{question}

Réponds directement à sa question.

Ne donne pas automatiquement la solution complète
si la question ne la demande pas.
"""


# ============================================================
# LEARN A CONCEPT
# ============================================================

def build_learn_concept_prompt(
    concept: str,
    student_knowledge: Optional[str] = None,
    exercises: Optional[Iterable[str]] = None,
) -> str:
    """
    Construit le prompt du mode Learn a Concept.
    """

    knowledge = (
        student_knowledge.strip()
        if student_knowledge
        else "Aucune information fournie."
    )

    exercises_text = ""

    if exercises:
        exercises_text = "\n".join(
            f"- {exercise}"
            for exercise in exercises
        )

    return f"""
Tu es le tuteur HintAI.

L'élève veut apprendre le concept :

{concept}

CE QUE L'ÉLÈVE PENSE DÉJÀ SAVOIR :

{knowledge}

EXERCICES ÉVENTUELLEMENT FOURNIS :

{exercises_text or "Aucun exercice fourni."}

Construis une mini-séquence pédagogique.

ÉTAPE 1 — EXPLICATION

Explique le concept simplement.

Commence par l'intuition.

Puis donne la règle ou la méthode.

Puis donne un exemple simple.

ÉTAPE 2 — EXERCICE 1

Crée un exercice assez simple permettant
de vérifier les bases.

ÉTAPE 3 — EXERCICE 2

Crée un exercice extrêmement difficile
qui force l'élève à combiner plusieurs idées
du concept.

IMPORTANT :

- Ne donne pas immédiatement les solutions.
- L'élève doit pouvoir demander un indice.
- Les indices seront donnés progressivement.
- L'objectif est la compréhension, pas seulement
  l'obtention de la réponse.
"""


def build_concept_question_prompt(
    concept: str,
    question: str,
    context: Optional[str] = None,
) -> str:
    """
    Question pendant Learn a Concept.
    """

    context_block = (
        f"\nCONTEXTE :\n{context}\n"
        if context
        else ""
    )

    return f"""
L'élève apprend :

{concept}

{context_block}

Question :

{question}

Réponds comme un professeur particulier.

Explique suffisamment pour que l'élève puisse
continuer seul.

Ne donne pas inutilement la solution complète
d'un exercice.
"""


def build_concept_hint_prompt(
    concept: str,
    exercise: str,
    level: int,
) -> str:
    """
    Indice pour un exercice Learn a Concept.
    """

    if level == 1:
        instruction = (
            "Donne une petite orientation."
        )

    elif level == 2:
        instruction = (
            "Donne une aide méthodologique claire."
        )

    elif level == 3:
        instruction = (
            "Guide presque complètement la démarche."
        )

    else:
        raise ValueError(
            "Le niveau doit être 1, 2 ou 3."
        )

    return f"""
Concept :

{concept}

Exercice :

{exercise}

{instruction}

Ne donne pas directement la réponse finale.
"""


# ============================================================
# EXERCICE DE VÉRIFICATION
# ============================================================

def build_verification_exercise_prompt(
    problem: str,
) -> str:
    """
    Génère un exercice similaire mais différent
    afin de vérifier la compréhension de l'élève.
    """

    return f"""
À partir de cet exercice :

{problem}

Crée un nouvel exercice qui teste
la même compétence.

L'exercice doit :

- être différent de l'original
- tester réellement la compréhension
- éviter de simplement changer les nombres
- avoir un énoncé clair
- être adapté au niveau de l'exercice original

Ne donne pas la solution.
"""


def build_work_verification_prompt(
    exercise: str,
    student_work: str,
) -> str:
    """
    Vérifie le travail de l'élève.
    """

    return f"""
ÉNONCÉ :

{exercise}

TRAVAIL DE L'ÉLÈVE :

{student_work}

Analyse son travail.

Indique :

1. Ce qui est correct
2. Les erreurs éventuelles
3. Pourquoi l'erreur est une erreur
4. La prochaine étape à effectuer
5. Si la réponse finale est correcte

Ne sois pas simplement binaire.
Le but est de faire progresser l'élève.
"""


# ============================================================
# GENERATION SIMPLE
# ============================================================

def generate(
    prompt: str,
    *,
    system_prompt: str = SYSTEM_PROMPT,
    temperature: float = 0.3,
) -> str:
    """
    Génération non-streaming.

    Utilisée pour :
    - réponses courtes
    - vérification
    - génération d'exercices
    - opérations nécessitant une réponse complète.
    """

    client = get_client()

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
        ),
    )

    return (
        getattr(
            response,
            "text",
            None,
        )
        or ""
    ).strip()


# ============================================================
# STREAMING GEMINI
# ============================================================

def generate_stream(
    prompt: str,
    *,
    system_prompt: str = SYSTEM_PROMPT,
    temperature: float = 0.3,
) -> Generator[str, None, None]:
    """
    Génère la réponse Gemini morceau par morceau.

    Le résultat peut ensuite être transformé en SSE
    dans api.py.

    Cela permet :

        Gemini
           ↓
        chunk 1
           ↓
        chunk 2
           ↓
        chunk 3
           ↓
        Expo
    """

    client = get_client()

    stream = client.models.generate_content_stream(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=temperature,
        ),
    )

    for chunk in stream:
        text = getattr(
            chunk,
            "text",
            None,
        )

        if text:
            yield text


# ============================================================
# HELP ME
# ============================================================

def help_me(
    problem: str,
    level: int = 1,
    context: Optional[str] = None,
) -> str:
    """
    Génère un indice Help Me.
    """

    prompt = build_help_me_prompt(
        problem,
        level,
        context,
    )

    return generate(
        prompt,
        temperature=0.25,
    )


def help_me_stream(
    problem: str,
    level: int = 1,
    context: Optional[str] = None,
) -> Generator[str, None, None]:
    """
    Version streaming de Help Me.
    """

    prompt = build_help_me_prompt(
        problem,
        level,
        context,
    )

    yield from generate_stream(
        prompt,
        temperature=0.25,
    )


def solve_problem(
    problem: str,
) -> str:
    """
    Résolution complète.
    """

    prompt = build_solution_prompt(
        problem
    )

    return generate(
        prompt,
        temperature=0.2,
    )


def solve_problem_stream(
    problem: str,
) -> Generator[str, None, None]:
    """
    Résolution complète en streaming.
    """

    prompt = build_solution_prompt(
        problem
    )

    yield from generate_stream(
        prompt,
        temperature=0.2,
    )


def answer_question(
    problem: str,
    question: str,
    previous_context: Optional[str] = None,
) -> str:
    """
    Répond à une question pendant Help Me.
    """

    prompt = build_question_prompt(
        problem,
        question,
        previous_context,
    )

    return generate(
        prompt,
        temperature=0.3,
    )


def answer_question_stream(
    problem: str,
    question: str,
    previous_context: Optional[str] = None,
) -> Generator[str, None, None]:
    """
    Question Help Me en streaming.
    """

    prompt = build_question_prompt(
        problem,
        question,
        previous_context,
    )

    yield from generate_stream(
        prompt,
        temperature=0.3,
    )


# ============================================================
# LEARN A CONCEPT
# ============================================================

def learn_concept(
    concept: str,
    student_knowledge: Optional[str] = None,
    exercises: Optional[Iterable[str]] = None,
) -> str:
    """
    Lance une séquence Learn a Concept.
    """

    prompt = build_learn_concept_prompt(
        concept,
        student_knowledge,
        exercises,
    )

    return generate(
        prompt,
        temperature=0.35,
    )


def learn_concept_stream(
    concept: str,
    student_knowledge: Optional[str] = None,
    exercises: Optional[Iterable[str]] = None,
) -> Generator[str, None, None]:
    """
    Learn a Concept en streaming.
    """

    prompt = build_learn_concept_prompt(
        concept,
        student_knowledge,
        exercises,
    )

    yield from generate_stream(
        prompt,
        temperature=0.35,
    )


def answer_concept_question(
    concept: str,
    question: str,
    context: Optional[str] = None,
) -> str:
    """
    Répond à une question Learn a Concept.
    """

    prompt = build_concept_question_prompt(
        concept,
        question,
        context,
    )

    return generate(
        prompt,
        temperature=0.3,
    )


def concept_hint(
    concept: str,
    exercise: str,
    level: int,
) -> str:
    """
    Génère un indice Learn a Concept.
    """

    prompt = build_concept_hint_prompt(
        concept,
        exercise,
        level,
    )

    return generate(
        prompt,
        temperature=0.25,
    )


# ============================================================
# VÉRIFICATION
# ============================================================

def generate_verification_exercise(
    problem: str,
) -> str:
    """
    Crée un exercice de contrôle de compréhension.
    """

    prompt = build_verification_exercise_prompt(
        problem
    )

    return generate(
        prompt,
        temperature=0.4,
    )


def verify_student_work(
    exercise: str,
    student_work: str,
) -> str:
    """
    Vérifie le travail de l'élève.
    """

    prompt = build_work_verification_prompt(
        exercise,
        student_work,
    )

    return generate(
        prompt,
        temperature=0.2,
    )


# ============================================================
# PROMPT CACHE
# ============================================================

"""
Prompt caching
--------------

HintAI doit éviter de renvoyer inutilement le même contexte
long à Gemini.

La stratégie prévue est :

    SYSTEM_PROMPT
          +
    règles pédagogiques
          +
    contexte stable
          ↓
       CACHE
          ↓
    requête utilisateur

Le support exact du cache dépendra du modèle/API Gemini
utilisé au moment du déploiement.

Cette fonction prépare donc le contexte stable sans
introduire de dépendance fragile à une API de cache
spécifique.

Le backend pourra ensuite brancher le mécanisme de cache
Gemini ici sans modifier les écrans Expo.
"""


def get_cacheable_system_prompt() -> str:
    """
    Retourne le contexte stable destiné au caching.
    """

    return SYSTEM_PROMPT.strip()


# ============================================================
# STRUCTURATION
# ============================================================

def parse_json_response(
    text: str,
) -> Dict[str, Any]:
    """
    Essaie de convertir une réponse IA JSON.

    Utile pour les fonctions qui devront retourner
    des structures strictes au frontend.
    """

    cleaned = text.strip()

    if cleaned.startswith(
        "```json"
    ):
        cleaned = cleaned[
            7:
        ]

    if cleaned.endswith(
        "```"
    ):
        cleaned = cleaned[
            :-3
        ]

    cleaned = cleaned.strip()

    try:
        data = json.loads(
            cleaned
        )

    except json.JSONDecodeError as exc:
        raise ValueError(
            "La réponse Gemini n'est pas un JSON valide."
        ) from exc

    if not isinstance(
        data,
        dict,
    ):
        raise ValueError(
            "La réponse Gemini doit être un objet JSON."
        )

    return data
````
