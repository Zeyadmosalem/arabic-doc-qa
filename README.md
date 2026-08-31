# arabic-doc-qa

Ask questions about a PDF in Arabic or English, and get answers with page citations.

## What it does

- Upload a PDF — Arabic or English.
- Ask a question in either language.
- Get an answer grounded in the document, with the pages it came from.

## Why

Most document-Q&A demos are English-only, and Arabic shows up as an afterthought that
happens to fall out of a multilingual model. This project treats Arabic as a first-class
language instead: text normalization, multilingual embeddings, and an RTL interface.

It is for teams whose paperwork is Arabic — contracts, policies, government forms — who
need an answer they can trace back to a page, not a plausible-sounding paragraph.

## Status

Work in progress — v1 is being built in public.

- [x] PDF upload and extraction
- [x] Chunking with Arabic normalization
- [x] Multilingual embeddings + Qdrant
- [x] Answers with page citations
- [ ] React UI with RTL
- [ ] Public deployment
- [ ] 10-question evaluation (5 Arabic, 5 English)

## Stack

Python 3.11 · FastAPI · PyMuPDF · sentence-transformers (`intfloat/multilingual-e5-base`) · Qdrant · Groq (`qwen/qwen3.8-27b`) · Vite + React + TypeScript

## Run locally

```bash
cp .env.example .env          # then fill in GROQ_API_KEY and QDRANT_URL
pip install -e "backend[dev]"
make dev                      # http://127.0.0.1:8000/health
```

`make test` runs the tests, `make lint` runs ruff.

## Demo

Coming soon — hosted link and a short GIF, Day 3–4.

## Architecture

Coming soon — ingestion and retrieval diagram, Day 4.

## Evaluation

Coming soon — results table for the 10-question set, Day 4.

## License

MIT — see [LICENSE](LICENSE).
