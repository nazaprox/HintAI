import os
import json
import uuid
from typing import Dict, Optional
from backend.config import Config

_sessions: Dict[str, Dict] = {}
MODEL = "gemini-3.1-flash-lite"


def get_genai_client():
    try:
        from google import genai
        key = Config.GEMINI_API_KEY or os.environ.get("GEMINI_API_KEY")
        return genai.Client(api_key=key) if key else None
    except Exception as exc:
        print(f"GenAI init error: {exc}")
        return None


def _generate(client, prompt, contents=None, temperature=0.4, json_mode=False):
    if not client:
        return None
    try:
        response = client.models.generate_content(
            model=MODEL,
            contents=contents or prompt,
            config={"temperature": temperature, **({"response_mime_type": "application/json"} if json_mode else {})},
        )
        return response.text.strip() if response and response.text else None
    except Exception as exc:
        print(f"Gemini generation error: {exc}")
        return None


def analyze_exercise(exercise_text: str = "", file_meta: Optional[Dict] = None) -> Dict:
    session_id = f"sess_{uuid.uuid4().hex[:12]}"
    prompt = f"""Tu es HintAI, un tuteur pédagogique bienveillant. Analyse l'exercice sans donner la solution finale. Identifie ce que l'élève doit comprendre, la matière, la notion clé et un premier indice très léger. Si le document est illisible, dis-le au lieu d'inventer. Exercice: {exercise_text or 'Aucun texte, document joint.'}\nRéponds uniquement en JSON avec analysis, key_concept et hint1."""
    analysis = "Je vais d'abord identifier ce que l'exercice te demande et la notion à utiliser."
    concept = "Méthode de résolution"
    hint1 = "Commence par repérer les données connues et ce que l'exercice demande exactement."
    client = get_genai_client()
    contents = [prompt]
    if file_meta and os.path.exists(file_meta.get("file_path", "")) and file_meta.get("mime_type", "").startswith("image/"):
        from google.genai import types
        with open(file_meta["file_path"], "rb") as fh:
            contents.append(types.Part.from_bytes(data=fh.read(), mime_type=file_meta["mime_type"]))
    raw = _generate(client, prompt, contents, 0.35, True)
    if raw:
        try:
            parsed = json.loads(raw)
            analysis = parsed.get("analysis", analysis)
            concept = parsed.get("key_concept", concept)
            hint1 = parsed.get("hint1", hint1)
        except json.JSONDecodeError:
            pass
    session = {"session_id": session_id, "exercise_text": exercise_text, "file_meta": file_meta, "analysis": analysis, "key_concept": concept, "hints": {1: hint1}, "unlocked_level": 1}
    _sessions[session_id] = session
    return session


def generate_hint(session_id: str, level: int) -> str:
    session = _sessions.get(session_id)
    if not session:
        raise ValueError("SESSION_NOT_FOUND")
    if level not in (1, 2, 3):
        raise ValueError("INVALID_HINT_LEVEL")
    if level in session["hints"]:
        return session["hints"][level]
    prompt = f"""Tu es HintAI, tuteur pédagogique. Exercice: {session['exercise_text']}. Notion: {session['key_concept']}. Indices précédents: {json.dumps(session['hints'], ensure_ascii=False)}. Génère l'indice {level}. Il doit être plus précis que le précédent, aider le raisonnement et ne jamais révéler directement la réponse finale."""
    text = _generate(get_genai_client(), prompt, temperature=0.45) or f"Indice {level} : identifie la règle du cours qui correspond aux données de l'exercice."
    session["hints"][level] = text
    session["unlocked_level"] = max(session["unlocked_level"], level)
    return text


def generate_solution(session_id: str) -> Dict:
    session = _sessions.get(session_id)
    if not session:
        raise ValueError("SESSION_NOT_FOUND")
    prompt = f"""Tu es HintAI. L'élève demande maintenant la méthode puis la solution complète. Exercice: {session['exercise_text']}. Notion: {session['key_concept']}. Donne une méthode réutilisable puis une solution étape par étape, avec vérification. JSON strict: method_explanation, full_solution."""
    fallback = {"method_explanation": "Identifier les données, choisir la règle adaptée, appliquer la règle, simplifier et vérifier.", "full_solution": "Étape 1 : identifier les données.\nÉtape 2 : appliquer la méthode.\nÉtape 3 : calculer et vérifier."}
    raw = _generate(get_genai_client(), prompt, temperature=0.25, json_mode=True)
    if raw:
        try:
            parsed = json.loads(raw)
            fallback.update({k: parsed[k] for k in fallback if k in parsed})
        except json.JSONDecodeError:
            pass
    return {"session_id": session_id, **fallback}


def explain_concept(concept: str, user_level: str = "Collège / Lycée") -> Dict:
    prompt = f"""Tu es HintAI, tuteur pédagogique. Un élève de niveau {user_level} veut apprendre {concept}. Construis une mini-leçon progressive : explication simple, intuition, exemple concret, quiz à 4 choix, exercice, correction guidée et 3 à 5 points à retenir. N'invente pas de faits. JSON strict avec explanation, example, quiz, exercise, correction, recap."""
    fallback = {"concept": concept, "explanation": f"{concept} est une notion que nous allons comprendre progressivement.", "example": f"Prenons un exemple simple de {concept}.", "quiz": {"question": f"Quelle idée décrit le mieux {concept} ?", "options": ["Le principe fondamental", "Une règle sans contexte", "Une réponse au hasard", "Aucune"], "correct_index": 0, "explanation": "Le principe fondamental est le point de départ."}, "exercise": f"Fais un petit exercice sur {concept}.", "correction": "Vérifie chaque étape de ton raisonnement.", "recap": ["Comprendre l'idée", "Identifier la règle", "S'entraîner"]}
    raw = _generate(get_genai_client(), prompt, temperature=0.4, json_mode=True)
    if raw:
        try:
            parsed = json.loads(raw)
            parsed["concept"] = concept
            return parsed
        except json.JSONDecodeError:
            pass
    return fallback
