
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



SYSTEM_PROMPT = """
Tu es le moteur d'analyse pédagogique de HintAI.

Tu analyses des exercices de :
- mathématiques
- physique
- chimie

Ton rôle :

Comprendre l'exercice,
mais ne jamais donner la solution.

Tu dois extraire :

- matière
- niveau
- énoncé
- données
- questions
- compétences
- concepts
- présence d'une figure
- difficulté

Tu dois retourner uniquement du JSON.

Ne jamais inventer une information absente.
"""



def analyze_image(image_bytes, mime_type="image/jpeg"):


    prompt = """

Analyse cette image d'exercice.

Retourne uniquement :

{
"subject":"",
"level":"",
"statement":"",
"data":[],
"questions":[],
"skills":[],
"concepts":[],
"has_figure":false,
"figure_description":"",
"difficulty":"",
"uncertain_elements":[]
}

Ne résous pas l'exercice.
"""


    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=[

            types.Part.from_bytes(
                data=image_bytes,
                mime_type=mime_type
            ),

            prompt
        ],

        config=types.GenerateContentConfig(

            system_instruction=SYSTEM_PROMPT,

            response_mime_type="application/json"

        )

    )


    try:

        return json.loads(
            response.text
        )

    except:

        return {
            "error":"JSON invalide",
            "raw":response.text
        }




def analyze_text(text):


    response = client.models.generate_content(

        model=GEMINI_MODEL,

        contents=f"""

Analyse cet exercice :

{text}

Retourne le même format JSON.
Ne résous pas.

""",

        config=types.GenerateContentConfig(

            system_instruction=SYSTEM_PROMPT,

            response_mime_type="application/json"

        )

    )


    try:

        return json.loads(
            response.text
        )

    except:

        return {
            "error":"JSON invalide",
            "raw":response.text
        }
