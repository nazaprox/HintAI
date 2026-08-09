
import json

from google import genai
from google.genai import types

from config.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


LEARNING_SYSTEM_PROMPT = """

Tu es le professeur pédagogique de HintAI.

Ton objectif n'est pas de donner directement
la réponse à l'élève.

Tu dois lui permettre de construire
la compétence lui-même.

Pour enseigner un concept :

1. Explique simplement.
2. Adapte l'explication à la classe.
3. Donne un exemple.
4. Vérifie la compréhension.
5. Donne un exercice guidé.
6. Utilise des indices progressifs.
7. Corrige les erreurs.
8. Termine par une évaluation.

Tu dois toujours privilégier
la compréhension et le raisonnement.

"""


def explain_concept(
    concept,
    class_level,
    examples=None
):

    if examples is None:
        examples = []


    prompt = f"""

Concept à apprendre :

{concept}


Classe :

{class_level}


Exercices éventuellement fournis :

{json.dumps(
    examples,
    ensure_ascii=False
)}


Construis une explication pédagogique
adaptée à cet élève.

Retourne :

- définition simple
- idée importante
- méthode
- exemple guidé
- erreur fréquente
- mini-question de vérification

"""


    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            system_instruction=
            LEARNING_SYSTEM_PROMPT

        )

    )


    return response.text


def create_guided_exercise(
    concept,
    class_level
):

    prompt = f"""

Concept :

{concept}


Classe :

{class_level}


Crée un exercice permettant
à l'élève de pratiquer ce concept.

Ne donne pas la solution.

L'exercice doit permettre
une correction par indices progressifs.

"""


    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            system_instruction=
            LEARNING_SYSTEM_PROMPT

        )

    )


    return response.text


def evaluate_concept(
    concept,
    class_level,
    student_work
):

    prompt = f"""

Concept :

{concept}


Classe :

{class_level}


Travail de l'élève :

{student_work}


Évalue sa maîtrise.

Donne :

- compétence acquise
- niveau estimé
- erreurs
- lacunes
- conseil personnalisé
- prochain exercice recommandé

Ne te contente pas de donner une note.
Explique ce que l'élève doit encore maîtriser.

"""


    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            system_instruction=
            LEARNING_SYSTEM_PROMPT

        )

    )


    return response.text
