"""Render entrypoint for HintAI V2.

Render runs from the repository root. The application itself lives in
backend/, so this wrapper adds backend/ to the import path and exposes app.
"""

from pathlib import Path
import sys

BACKEND_DIR = Path(__file__).resolve().parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app import app  # noqa: E402
