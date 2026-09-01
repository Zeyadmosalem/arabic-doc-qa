# Backend

FastAPI service behind [arabic-doc-qa](https://github.com/Zeyadmosalem/arabic-doc-qa).

- `GET /health` — liveness
- `POST /upload` — PDF in, chunks indexed in Qdrant, document id out
- `POST /ask` — question in, grounded answer with page citations out

Live: https://arabic-doc-qa-api.vercel.app ([docs](https://arabic-doc-qa-api.vercel.app/docs))

## Configuration

| Variable | Purpose |
| --- | --- |
| `GROQ_API_KEY` | Groq API key |
| `GROQ_MODEL` | Chat model, default `qwen/qwen3.8-27b` |
| `JINA_API_KEY` | Jina API key, used for embeddings |
| `EMBEDDING_MODEL` | Embedding model, default `jina-embeddings-v3` |
| `QDRANT_URL` | Qdrant Cloud endpoint, including `:6333` |
| `QDRANT_API_KEY` | Qdrant Cloud key |
| `CORS_ORIGINS` | Comma-separated front-end origins |
| `MAX_PAGES` | Page cap for ingestion, default 20 |

Changing `EMBEDDING_MODEL` to one with different dimensions means recreating the
Qdrant collection; existing vectors are unusable at a new size.

## Local development

```bash
pip install -e ".[dev]"
uvicorn app.main:app --reload
pytest
ruff check .
```

## Deployment

Deployed as a Vercel serverless function. `api/index.py` re-exports the same app,
and Vercel's FastAPI detection routes every path to it — no rewrite needed, and a
catch-all rewrite actively breaks it, since rewrites deliver the rewritten
destination path.

The project's root directory must be set to `backend`, or a git-triggered build
runs from the repo root and fails.

`Dockerfile` builds the same service as a container for any host that takes one.
It honours `$PORT` and defaults to 8080.
