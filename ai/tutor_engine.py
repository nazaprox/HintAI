
from google import genai
from google.genai import types

from config.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)


client = genai.Client(
    api_key=GEMINI_API_KEY
)


SYSTEM = """

Tu es le professeur particulier HintAI.

Objectif :

Faire progresser l'élève.

Règles :

- Ne donne jamais directement la réponse.
- Pose des questions utiles.
- Explique l'erreur.
- Donne des indices progressifs.
- Adapte le niveau.

Tu es patient et pédagogique.

"""



def answer_student_question(
    exercise,
    student_work,
    question,
    hint_level
):


    prompt = f"""

Exercice :

{exercise}


Travail élève :

{student_work}


Question élève :

{question}


Niveau d'aide actuel :

Indice {hint_level}


Réponds comme un professeur.

Si l'élève est bloqué :

- explique la notion nécessaire
- pose une question intermédiaire
- donne un indice adapté


"""


    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            system_instruction=SYSTEM

        )

    )


    return response.text




def generate_next_hint(
    exercise,
    mistake,
    level
):


    prompt = f"""

Exercice :

{exercise}


Erreur :

{mistake}


Niveau :

{level}



Génère un nouvel indice.


Indice 1 :
réflexion


Indice 2 :
orientation


Indice 3 :
méthode presque complète



Ne donne pas la solution finale.

"""


    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            system_instruction=SYSTEM

        )

    )


    return response.text



def final_explanation(
    exercise,
    attempts
):


    prompt = f"""

Exercice :

{exercise}


Tentatives :

{attempts}



Explique maintenant :

- la méthode complète
- les erreurs rencontrées
- la meilleure stratégie


C'est la dernière étape après les indices.

"""


    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt

    )


    return response.text
