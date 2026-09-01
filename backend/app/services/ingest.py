"""Turning an uploaded PDF into indexed, searchable chunks."""

import math
import re
import uuid

import httpx
import pymupdf
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.config import settings
from app.models import Chunk, Page

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
VECTOR_SIZE = 1024
JINA_URL = "https://api.jina.ai/v1/embeddings"
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models"
EMBEDDING_TIMEOUT = 60.0

# Stable namespace so re-ingesting the same document overwrites its chunks
# instead of duplicating them.
_NAMESPACE = uuid.UUID("6f1e6f8a-1f3a-4b7e-9a2c-0d5f6d3b8a41")

# Arabic normalization. Kept deliberately light: E5 is a semantic model trained
# on natural text, so we strip what is purely orthographic noise (diacritics,
# tatweel, alef spellings, Arabic-Indic digits) and leave the words themselves
# alone.
_DIACRITICS = re.compile("[ً-ٰٟۖ-ۭ]")
_TATWEEL = re.compile("ـ")
_ZERO_WIDTH = re.compile("[​-‏‪-‮﻿]")
_ALEF_VARIANTS = re.compile("[آأإٱ]")
_ALEF_MAQSURA = re.compile("ى")
_WHITESPACE = re.compile(r"\s+")
_DIGIT_MAP = {base + i: str(i) for base in (0x0660, 0x06F0) for i in range(10)}

_client: QdrantClient | None = None


def normalize_arabic(text: str) -> str:
    """Strip orthographic noise so Arabic text matches regardless of spelling.

    Removes diacritics, tatweel and bidi control characters, folds the alef
    variants (آ أ إ) onto bare alef and alef maqsura (ى) onto yeh, maps
    Arabic-Indic digits onto ASCII, and collapses whitespace. Latin text passes
    through unchanged apart from the whitespace collapse.
    """
    text = _ZERO_WIDTH.sub("", text)
    text = _DIACRITICS.sub("", text)
    text = _TATWEEL.sub("", text)
    text = _ALEF_VARIANTS.sub("ا", text)
    text = _ALEF_MAQSURA.sub("ي", text)
    text = text.translate(_DIGIT_MAP)
    return _WHITESPACE.sub(" ", text).strip()


def extract_pages(pdf_bytes: bytes) -> list[Page]:
    """Extract the text of every page of a PDF.

    Args:
        pdf_bytes: The raw bytes of the uploaded PDF.

    Returns:
        One Page per page in the document, in order, each carrying its
        1-based page number and its extracted text.
    """
    with pymupdf.open(stream=pdf_bytes, filetype="pdf") as document:
        # sort=False is deliberate. Sorting reorders text geometrically, which
        # reverses Arabic word order: a heading that reads "طلب حجز وجبات"
        # comes back as "وجبات حجز طلب". Content-stream order is the logical
        # reading order for both scripts.
        return [
            Page(number=number, text=page.get_text("text", sort=False))
            for number, page in enumerate(document, start=1)
        ]


def chunk_pages(pages: list[Page], *, document_id: str) -> list[Chunk]:
    """Split pages into overlapping chunks, one page at a time.

    Chunking never crosses a page boundary, so every chunk has exactly one
    page number to cite.

    Args:
        pages: The pages returned by extract_pages, in document order.
        document_id: The document these chunks belong to.

    Returns:
        Chunks small enough to embed, each keeping the page number it came
        from. Blank pages produce no chunks.
    """
    chunks: list[Chunk] = []
    for page in pages:
        text = _WHITESPACE.sub(" ", page.text).strip()
        for index, piece in enumerate(_split(text)):
            chunks.append(
                Chunk(
                    id=str(uuid.uuid5(_NAMESPACE, f"{document_id}:{page.number}:{index}")),
                    text=piece,
                    page=page.number,
                    document_id=document_id,
                )
            )
    return chunks


def _split(text: str) -> list[str]:
    """Cut text into CHUNK_SIZE pieces overlapping by CHUNK_OVERLAP, on word boundaries."""
    if not text:
        return []
    if len(text) <= CHUNK_SIZE:
        return [text]

    pieces: list[str] = []
    start = 0
    while start < len(text):
        end = start + CHUNK_SIZE
        if end < len(text):
            boundary = text.rfind(" ", start + CHUNK_SIZE - CHUNK_OVERLAP, end)
            if boundary != -1:
                end = boundary
        piece = text[start:end].strip()
        if piece:
            pieces.append(piece)
        if end >= len(text):
            break
        start = max(end - CHUNK_OVERLAP, start + 1)
    return pieces


def embed_texts(texts: list[str], *, task: str = "passage") -> list[list[float]]:
    """Embed texts with the configured provider.

    Runs through an API rather than a local model: the smallest multilingual
    model that fits this job still needs ~700 MB resident once its ONNX runtime
    has allocated its arena, which no free host will give us.

    Both providers are asymmetric, so stored text and questions must be embedded
    for different tasks or retrieval quality drops, and both are configured to
    return 1024 dimensions so switching between them needs no re-indexing.

    Args:
        texts: Chunk texts (when indexing) or a question (when searching).
        task: "passage" for indexing, "query" for searching.

    Returns:
        One 1024-dim vector per input text, in the same order.
    """
    if not texts:
        return []

    prepared = [normalize_arabic(text) for text in texts]
    if settings.embedding_provider == "gemini":
        return _embed_gemini(prepared, task)
    return _embed_jina(prepared, task)


def _embed_jina(texts: list[str], task: str) -> list[list[float]]:
    """Embed via Jina. https://jina.ai/embeddings"""
    if not settings.jina_api_key:
        raise RuntimeError("JINA_API_KEY is not set")

    response = httpx.post(
        JINA_URL,
        timeout=EMBEDDING_TIMEOUT,
        headers={"Authorization": f"Bearer {settings.jina_api_key}"},
        json={
            "model": settings.embedding_model,
            "task": f"retrieval.{task}",
            "input": texts,
        },
    )
    response.raise_for_status()
    # The API is documented to echo input order, but it also returns an index
    # per item; sorting on it costs nothing and removes the assumption.
    data = sorted(response.json()["data"], key=lambda item: item["index"])
    return [item["embedding"] for item in data]


def _embed_gemini(texts: list[str], task: str) -> list[list[float]]:
    """Embed via Google AI Studio. https://aistudio.google.com/apikey"""
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not set")

    model = settings.embedding_model
    task_type = "RETRIEVAL_QUERY" if task == "query" else "RETRIEVAL_DOCUMENT"
    response = httpx.post(
        f"{GEMINI_URL}/{model}:batchEmbedContents",
        timeout=EMBEDDING_TIMEOUT,
        params={"key": settings.gemini_api_key},
        json={
            "requests": [
                {
                    "model": f"models/{model}",
                    "content": {"parts": [{"text": text}]},
                    "taskType": task_type,
                    "outputDimensionality": VECTOR_SIZE,
                }
                for text in texts
            ]
        },
    )
    response.raise_for_status()
    # Truncated Gemini embeddings are not unit length, and cosine distance in
    # Qdrant assumes they are.
    return [_unit(item["values"]) for item in response.json()["embeddings"]]


def _unit(vector: list[float]) -> list[float]:
    """Scale a vector to unit length, leaving an all-zero vector alone."""
    norm = math.sqrt(sum(value * value for value in vector))
    return [value / norm for value in vector] if norm else vector


def upsert_chunks(chunks: list[Chunk]) -> None:
    """Embed chunks and write them to the Qdrant collection.

    Args:
        chunks: The chunks to index. Ids are derived from the document, so
        re-ingesting a document overwrites rather than duplicates.

    Returns:
        Nothing.
    """
    if not chunks:
        return
    client = get_qdrant_client()
    ensure_collection(client)
    vectors = embed_texts([chunk.text for chunk in chunks])
    client.upsert(
        collection_name=settings.qdrant_collection,
        points=[
            qmodels.PointStruct(
                id=chunk.id,
                vector=vector,
                payload={
                    "text": chunk.text,
                    "page": chunk.page,
                    "document_id": chunk.document_id,
                },
            )
            for chunk, vector in zip(chunks, vectors, strict=True)
        ],
        wait=True,
    )


def get_qdrant_client() -> QdrantClient:
    """Return the process-wide Qdrant client, creating it on first use."""
    global _client
    if _client is None:
        _client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key or None,
        )
    return _client


def ensure_collection(client: QdrantClient) -> None:
    """Create the collection and its document_id index if they do not exist yet."""
    if client.collection_exists(settings.qdrant_collection):
        return
    client.create_collection(
        collection_name=settings.qdrant_collection,
        vectors_config=qmodels.VectorParams(
            size=VECTOR_SIZE,
            distance=qmodels.Distance.COSINE,
        ),
    )
    client.create_payload_index(
        collection_name=settings.qdrant_collection,
        field_name="document_id",
        field_schema=qmodels.PayloadSchemaType.KEYWORD,
    )
