"""Vercel serverless entry point.

Vercel builds every file under api/ into a function and can serve an ASGI app
directly, so this re-exports the same FastAPI application used everywhere else.
vercel.json rewrites all paths here, which means FastAPI still sees /health,
/upload and /ask rather than /api/index.
"""

import sys
from pathlib import Path

# The function's working directory is this project root (backend/), but the
# bundler does not put it on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import app  # noqa: E402

__all__ = ["app"]
