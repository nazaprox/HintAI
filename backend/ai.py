"""Gemini AI engine for HintAI."""
from __future__ import annotations

import os
from google import genai
from google.genai import types

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY manquante")

client = genai.Client(api_key=API_KEY)
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

async def ask_ai(prompt: str) -> str:
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=2048,
            ),
        )
        return response.text or "Je n'ai pas pu générer de réponse."
    except Exception:
        return "Le service IA est temporairement indisponible. Réessaie dans quelques secondes."

async def analyze_exercise(text: str) -> str:
    return await ask_ai(f"""
Tu es HintAI, un professeur IA bienveillant.
Analyse l'exercice suivant sans donner immédiatement la solution finale.
Explique ce qui est demandé, les notions nécessaires et la première étape.
Adapte le niveau à un élève.

EXERCICE:
{text}
""")

async def generate_hint(context: str, level: int) -> str:
    return await ask_ai(f"""
Tu es HintAI.
Donne un indice de niveau {level} pour aider l'élève sans révéler toute la solution.
Contexte de l'exercice/analyse:
{context}
""")

async def generate_solution(context: str) -> str:
    return await ask_ai(f"""
Tu es HintAI.
Donne maintenant une solution complète et pédagogique.
Montre les étapes, les calculs et explique pourquoi chaque étape est faite.
Contexte:
{context}
""")

async def explain_concept(concept: str) -> str:
    return await ask_ai(f"""
Tu es un excellent professeur.
Explique simplement le concept suivant à un élève:
{concept}

Structure:
1. définition simple
2. idée essentielle
3. exemple
4. méthode
5. petit exercice pour vérifier la compréhension
""")