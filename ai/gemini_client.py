
from google import genai
from google.genai import types

from config.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)


# ==========================================
# INITIALISATION CLIENT GEMINI
# ==========================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# ==========================================
# APPEL TEXTE GEMINI
# ==========================================

def ask_gemini(prompt, system_instruction=None):
    """
    Envoie une demande texte à Gemini.
    """

    config = types.GenerateContentConfig(
        system_instruction=system_instruction
        if system_instruction
        else None
    )


    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=config
    )


    return response.text



# ==========================================
# APPEL IMAGE + TEXTE GEMINI
# ==========================================

def analyze_image(image_file, prompt, system_instruction=None):
    """
    Analyse une image avec Gemini Vision.
    """

    image_part = types.Part.from_bytes(
        data=image_file.read(),
        mime_type=image_file.type
    )


    config = types.GenerateContentConfig(
        system_instruction=system_instruction
        if system_instruction
        else None
    )


    response = client.models.generate_content(
        model=GEMINI_MODEL,

        contents=[
            image_part,
            prompt
        ],

        config=config
    )


    return response.text



# ==========================================
# PREPARATION CONTEXT CACHE
# ==========================================

def create_hintai_context_cache():
    """
    Emplacement prévu pour Gemini Context Caching.

    Contiendra :
    - règles professeur HintAI
    - pédagogie
    - programmes scolaires
    - format JSON
    """

    return {
        "cache_name": "hintai_core_context",
        "status": "ready"
    }



# ==========================================
# TEST CONNEXION
# ==========================================

def test_connection():

    response = ask_gemini(
        "Réponds uniquement : HintAI connecté"
    )

    return response
