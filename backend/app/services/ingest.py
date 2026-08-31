"""Turning an uploaded PDF into indexed, searchable chunks."""

import re
import uuid

import pymupdf
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels
from sentence_transformers import SentenceTransformer

from app.config import settings
from app.models import Chunk, Page

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150
VECTOR_SIZE = 768

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

_model: SentenceTransformer | None = None
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


def embed_texts(texts: list[str], *, prefix: str = "passage") -> list[list[float]]:
    """Embed texts with the configured multilingual sentence-transformers model.

    E5 is asymmetric: stored text must be prefixed "passage: " and questions
    "query: ", or retrieval quality drops sharply.

    Args:
        texts: Chunk texts (when indexing) or a question (when searching).
        prefix: "passage" for indexing, "query" for searching.

    Returns:
        One L2-normalized 768-dim vector per input text, in the same order.
    """
    model = _get_model()
    prepared = [f"{prefix}: {normalize_arabic(text)}" for text in texts]
    vectors = model.encode(prepared, normalize_embeddings=True, show_progress_bar=False)
    return [vector.tolist() for vector in vectors]


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


def _get_model() -> SentenceTransformer:
    """Load the embedding model once per process."""
    global _model
    if _model is None:
        _model = SentenceTransformer(settings.embedding_model)
    return _model
