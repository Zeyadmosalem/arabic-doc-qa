# arabic-doc-qa

Ask questions about a PDF in Arabic or English, and get answers with page citations.

**[Try it →](https://arabic-doc-qa.vercel.app)** · [API docs](https://arabic-doc-qa-api.vercel.app/docs)

## What it does

- Upload a PDF — Arabic or English.
- Ask a question in either language.
- Get an answer grounded in the document, with the pages it came from — and click a
  citation to open that page beside the answer.

## Why

Most document-Q&A demos are English-only, and Arabic shows up as an afterthought that
happens to fall out of a multilingual model. This project treats Arabic as a first-class
language instead: text normalization, multilingual embeddings, and an RTL interface.

It is for teams whose paperwork is Arabic — contracts, policies, government forms — who
need an answer they can trace back to a page, not a plausible-sounding paragraph.

## How it works

```
PDF ──► extract ──► chunk ──► embed ──► Qdrant
        PyMuPDF     ≤1000 chars    jina-embeddings-v3
        reading     never crossing  1024-dim
        order       a page boundary

question ──► embed ──► search top 5 ──► Groq ──► answer + citations
                       filtered by       grounded to the retrieved
                       document_id       chunks only
```

Three decisions carry most of the weight:

**Extraction preserves reading order.** PyMuPDF's `sort=True` orders text geometrically,
which reverses Arabic word order — a heading reading `طلب حجز وجبات` comes back as
`وجبات حجز طلب`. Content-stream order is the logical reading order for both scripts.

**Chunks never cross a page boundary**, so every chunk has exactly one page to cite. A
sentence straddling a page break gets split; exact citations are worth more.

**Citations are filtered to the pages the model actually cited** inline, intersected with
what it was shown, so an invented page number cannot produce a citation.

## Limitations

**Scanned PDFs are out of scope.** They carry no text layer and need OCR. The app detects
them and says so rather than returning an empty answer. This is not a corner case — the
first real Arabic PDF tested against it was 271 photographed pages.

**Documents are capped at 20 pages,** because ingestion is synchronous. Async ingestion
for longer documents is a v2 item.

**Embeddings run through Jina's API rather than a local model.** `multilingual-e5-base`
under sentence-transformers needed ~800 MB resident, and the smallest multilingual model
available under ONNX still needed ~700 MB once its runtime had allocated its arena —
above every free tier available. Moving to an API took the service to 132 MB and cut
ingestion of a 12-page PDF from 29s to 4s. Running the model in-process is a v2 item, for
when the deployment budget allows it.

**Some PDFs damage their own text.** One government document tested against this maps the
lam-alef ligature to a single wrong character, so `سلامة` extracts as `سامة`. That is a
defect in the file's embedded font, not something extraction can repair.

## Stack

Python 3.11 · FastAPI · PyMuPDF · Jina embeddings (`jina-embeddings-v3`) · Qdrant · Groq (`qwen/qwen3.8-27b`) · Vite + React + TypeScript

## Run locally

Backend:

```bash
cp .env.example .env          # fill in GROQ_API_KEY, JINA_API_KEY, QDRANT_URL, QDRANT_API_KEY
pip install -e "backend[dev]"
make dev                      # http://127.0.0.1:8000/health
```

Front end, in a second terminal:

```bash
cd frontend && npm install
make web                      # http://localhost:5173
```

`make test` runs the tests, `make lint` runs ruff, `make build-web` builds the front end.

## Deployment

Two Vercel projects from this one repo, distinguished only by root directory:

| Project | Root directory | Serves |
| --- | --- | --- |
| `arabic-doc-qa` | `frontend` | the React app |
| `arabic-doc-qa-api` | `backend` | FastAPI, as a serverless function |

Setting the root directory on each project is required. Without it a git-triggered build
runs from the repo root and fails — the front end looks for `vite` where there is no
`node_modules`.

`backend/Dockerfile` also builds a working container, for any host that takes one.

## Evaluation

Coming soon — a 10-question set, five Arabic and five English, with the results table.

## License

MIT — see [LICENSE](LICENSE).
