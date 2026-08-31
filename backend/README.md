---
title: Arabic Doc QA API
emoji: 📄
colorFrom: green
colorTo: gray
sdk: gradio
app_file: space_app.py
pinned: false
---

# Backend

FastAPI service behind [arabic-doc-qa](https://github.com/Zeyadmosalem/arabic-doc-qa).

- `GET /health` — liveness
- `POST /upload` — PDF in, chunks indexed in Qdrant, document id out
- `POST /ask` — question in, grounded answer with page citations out

## Required configuration

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Groq API key |
| `GROQ_MODEL` | Chat model, default `qwen/qwen3.8-27b` |
| `QDRANT_URL` | Qdrant Cloud endpoint, including `:6333` |
| `QDRANT_API_KEY` | Qdrant Cloud key |
| `CORS_ORIGINS` | Comma-separated front-end origins |
| `MAX_PAGES` | Page cap for ingestion, default 20 |

## Local development

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
pytest
ruff check .
```

The embedding model is baked into the Docker image, so a cold start does not
have to download 1.1 GB before answering the first request.
