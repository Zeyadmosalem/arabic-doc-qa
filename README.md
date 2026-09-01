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
- [x] React UI with RTL
- [ ] Public deployment
- [ ] 10-question evaluation (5 Arabic, 5 English)

Scanned PDFs are out of scope for v1 — they carry no text layer and need OCR.
The app detects them and says so rather than returning an empty answer.
v1 also indexes up to 20 pages, because ingestion is synchronous.

Embeddings run through Jina's API rather than a local model. `multilingual-e5-base`
under sentence-transformers needed ~800 MB resident, and the smallest multilingual
model that fits this job still needed ~700 MB once ONNX Runtime had allocated its
arena — above every free tier available. Moving to an API took the service to
132 MB and cut ingestion of a 12-page PDF from 29s to 4s. Running the model in
-process is a v2 item, for when the deployment budget allows it.

## Stack

Python 3.11 · FastAPI · PyMuPDF · Jina embeddings (`jina-embeddings-v3`) · Qdrant · Groq (`qwen/qwen3.8-27b`) · Vite + React + TypeScript

## Run locally

Backend:

```bash
cp .env.example .env          # then fill in GROQ_API_KEY and QDRANT_URL
pip install -e "backend[dev]"
make dev                      # http://127.0.0.1:8000/health
```

Front end, in a second terminal:

```bash
cd frontend && npm install
make web                      # http://localhost:5173
```

`make test` runs the tests, `make lint` runs ruff, `make build-web` builds the front end.

## Demo

Coming soon — hosted link and a short GIF, Day 3–4.

## Architecture

Coming soon — ingestion and retrieval diagram, Day 4.

## Evaluation

Coming soon — results table for the 10-question set, Day 4.

## License

MIT — see [LICENSE](LICENSE).
