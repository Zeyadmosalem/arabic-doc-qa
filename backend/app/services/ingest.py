"""Turning an uploaded PDF into indexed, searchable chunks."""

from app.models import Chunk, Page


def extract_pages(pdf_bytes: bytes) -> list[Page]:
    """Extract the text of every page of a PDF.

    Args:
        pdf_bytes: The raw bytes of the uploaded PDF.

    Returns:
        One Page per page in the document, in order, each carrying its
        1-based page number and its extracted text.
    """
    raise NotImplementedError


def chunk_pages(pages: list[Page]) -> list[Chunk]:
    """Split pages into overlapping chunks, normalizing Arabic text along the way.

    Args:
        pages: The pages returned by extract_pages, in document order.

    Returns:
        Chunks small enough to embed, each keeping the page number it came
        from so answers can cite it.
    """
    raise NotImplementedError


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed texts with the configured multilingual sentence-transformers model.

    Args:
        texts: Chunk texts (when indexing) or a question (when searching).

    Returns:
        One dense vector per input text, in the same order.
    """
    raise NotImplementedError


def upsert_chunks(chunks: list[Chunk]) -> None:
    """Embed chunks and write them to the Qdrant collection.

    Args:
        chunks: The chunks to index. Existing chunks with the same id are
        overwritten, so re-ingesting a document is safe to repeat.

    Returns:
        Nothing.
    """
    raise NotImplementedError
