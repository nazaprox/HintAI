"""
HintAI - AI Engine
Gemini backend
"""


import os

from google import genai
from google.genai import types


# =====================================================
# CONFIG GEMINI
# =====================================================


API_KEY = os.getenv(
    "GEMINI_API_KEY"
)


if not API_KEY:

    raise RuntimeError(
        "GEMINI_API_KEY manquante"
    )



client = genai.Client(
    api_key=API_KEY
)



MODEL = "gemini-3.1-flash-lite"





# =====================================================
# GENERATION GENERALE
# =====================================================


async def ask_ai(prompt: str):


    try:


        response = client.models.generate_content(

            model=MODEL,

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0.4,

                max_output_tokens=2048

            )

        )



        return response.text



    except Exception as error:


        return (

            "Erreur IA : "

            + str(error)

        )







# =====================================================
# HELP ME - ANALYSE
# =====================================================


async def analyze_exercise(
    text: str
):


    prompt = f"""

Tu es HintAI, un professeur IA.

Analyse cet exercice :

{text}


Consignes :

- Ne donne pas directement la réponse au début.
- Explique la méthode.
- Découpe en étapes simples.
- Adapte l'explication au niveau étudiant.


Réponse :

"""


    return await ask_ai(
        prompt
    )







# =====================================================
# INDICES
# =====================================================


async def generate_hint(

    response_id:str,

    level:int

):


    prompt = f"""

Tu es HintAI.

Donne un indice de niveau {level}.

Niveau 1 :
petit rappel.

Niveau 2 :
orientation plus précise.

Niveau 3 :
presque la solution mais sans tout donner.


Référence exercice :
{response_id}

"""


    return await ask_ai(
        prompt
    )







# =====================================================
# SOLUTION COMPLETE
# =====================================================


async def generate_solution(

    response_id:str

):


    prompt = f"""

Tu es HintAI.

Donne une résolution complète :

- étapes détaillées
- calculs
- explication finale


Exercice ID :

{response_id}

"""


    return await ask_ai(
        prompt
    )







# =====================================================
# QUESTION
# =====================================================


async def answer_question(

    question:str

):


    prompt = f"""

Réponds clairement à cette question :

{question}


Explique simplement.

"""


    return await ask_ai(
        prompt
    )







# =====================================================
# LEARN CONCEPT
# =====================================================


async def explain_concept(

    concept:str

):


    prompt = f"""

Tu es un professeur.

Apprends le concept suivant :

{concept}


Structure :

1. Explication simple
2. Exemple
3. Méthode
4. Petit exercice


"""


    return await ask_ai(
        prompt
    )