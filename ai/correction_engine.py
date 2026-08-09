
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

Tu es le correcteur pédagogique HintAI.

Tu ne dois pas seulement dire vrai ou faux.

Tu dois comprendre :

- la méthode utilisée
- l'erreur de raisonnement
- la notion mal comprise
- le niveau de l'élève

Tu agis comme un professeur.

Tu guides avec des indices.

"""





def compare_work(
    exercise,
    student_work
):


    prompt = f"""

Exercice :

{exercise}



Travail de l'élève :

{student_work}



Analyse :

1. La démarche est-elle correcte ?
2. Où est l'erreur ?
3. Quelle compétence manque ?
4. Quel indice donner en premier ?
5. Quelle amélioration proposer ?


Retourne une analyse structurée.

"""


    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            system_instruction=SYSTEM

        )

    )


    return response.text






def generate_progressive_hint(
    error_analysis,
    level
):


    prompt = f"""

Erreur détectée :

{error_analysis}


Niveau actuel :

{level}


Crée un indice pédagogique.

Règles :

Indice 1 :
faire réfléchir

Indice 2 :
orienter fortement

Indice 3 :
presque guider la méthode


Ne donne pas directement la solution.

"""


    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=prompt,

        config=types.GenerateContentConfig(

            system_instruction=SYSTEM

        )

    )


    return response.text
