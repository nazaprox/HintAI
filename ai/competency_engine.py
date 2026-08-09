
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

Tu es le moteur de compétences HintAI.

Tu transformes une correction
en progression pédagogique.

"""





def analyze_competency(
    subject,
    exercise,
    correction
):


    prompt = f"""

Matière :

{subject}


Exercice :

{exercise}


Correction :

{correction}



Détermine :

- compétence principale
- compétences secondaires
- niveau actuel
- erreurs fréquentes
- plan d'amélioration
- exercice suivant conseillé


Réponds sous forme structurée.

"""


    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            system_instruction=SYSTEM

        )

    )


    return response.text






def create_training_plan(
    competency
):


    prompt = f"""

Compétence :

{competency}


Crée un petit plan d'entraînement :

1. notion à revoir
2. exercice facile
3. exercice moyen
4. exercice difficile
5. objectif final


"""


    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            system_instruction=SYSTEM

        )

    )


    return response.text
