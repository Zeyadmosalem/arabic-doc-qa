"""Finding the chunks that answer a question, and writing the answer."""

import re

from groq import Groq
from qdrant_client.http import models as qmodels

from app.config import settings
from app.models import Answer, Chunk, Citation
from app.services.ingest import embed_texts, get_qdrant_client

SNIPPET_LENGTH = 240

_ARABIC = re.compile(r"[؀-ۿ]")
_LATIN = re.compile(r"[A-Za-z]")

# Matches "(p. 3)" and "(p. 10, p. 11)". Also accepts the Arabic "ص." because
# some models translate the label when answering in Arabic, and a citation
# silently dropped here falls back to listing every retrieved page.
_PAGE_REF = re.compile(r"(?:p\.|ص\.)\s*(\d+)")

SYSTEM_PROMPT = """You answer questions about a document using only the context provided.

Rules:
- Use only the context. If the answer is not there, say exactly that and stop.
- Never infer, estimate or complete a fact the context does not state, especially dates,
  numbers and names. If the context is partial, say what it does say and nothing more.
- Answer in the language named at the end of the question, including when you cannot
  answer.
- Cite the page for every claim, in the form (p. 3). Use that exact form even when
  answering in Arabic; do not translate the label.
- Answer in at most three sentences of plain prose. No headings, no bullet points, no
  bold, no markdown of any kind."""


def search(query: str, top_k: int, *, document_id: str | None = None) -> list[Chunk]:
    """Find the chunks most similar to a question.

    Args:
        query: The user's question, in Arabic or English.
        top_k: How many chunks to return.
        document_id: Restrict the search to one document, or None to search all.

    Returns:
        Up to top_k chunks ordered by descending similarity, each with its
        score and source page set. Empty if nothing has been indexed yet.
    """
    client = get_qdrant_client()
    if not client.collection_exists(settings.qdrant_collection):
        return []

    query_filter = None
    if document_id is not None:
        query_filter = qmodels.Filter(
            must=[
                qmodels.FieldCondition(
                    key="document_id",
                    match=qmodels.MatchValue(value=document_id),
                )
            ]
        )

    response = client.query_points(
        collection_name=settings.qdrant_collection,
        query=embed_texts([query], task="query")[0],
        query_filter=query_filter,
        limit=top_k,
        with_payload=True,
    )
    return [
        Chunk(
            id=str(point.id),
            text=point.payload["text"],
            page=point.payload["page"],
            document_id=point.payload["document_id"],
            score=point.score,
        )
        for point in response.points
    ]


def answer(question: str, chunks: list[Chunk]) -> Answer:
    """Ask the Groq model to answer a question from the retrieved chunks.

    Args:
        question: The user's question, in Arabic or English.
        chunks: The chunks retrieved by search, used as the only context.

    Returns:
        An Answer in the language of the question, with a citation for each
        page it drew on.
    """
    if not settings.groq_api_key:
        raise RuntimeError("GROQ_API_KEY is not set")

    context = "\n\n".join(f"[page {chunk.page}]\n{chunk.text}" for chunk in chunks)
    # Name the language rather than leaving it to a general rule. Asked only to
    # match the question's language, the model answered Arabic questions in
    # Arabic but fell back to English whenever it had to decline.
    language = "Arabic" if _is_arabic(question) else "English"
    completion = Groq(api_key=settings.groq_api_key).chat.completions.create(
        model=settings.groq_model,
        temperature=0,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    f"Context:\n{context}\n\nQuestion: {question}"
                    f"\n\nWrite the answer in {language}, including if you cannot answer."
                ),
            },
        ],
    )
    text = (completion.choices[0].message.content or "").strip()
    return Answer(text=text, citations=_citations(chunks, cited_in=text))


def _is_arabic(text: str) -> bool:
    """Whether a string is predominantly Arabic, by script count."""
    return len(_ARABIC.findall(text)) > len(_LATIN.findall(text))


def _citations(chunks: list[Chunk], *, cited_in: str = "") -> list[Citation]:
    """One citation per distinct page the answer actually leans on.

    Prefers the pages the model cited inline as "(p. 3)", keeping only those it
    was really shown so a hallucinated page number cannot invent a citation.
    Falls back to every retrieved page when the model cited nothing, which is
    the honest answer to "where did this come from?" in that case.
    """
    retrieved_pages = {chunk.page for chunk in chunks}
    wanted = {int(page) for page in _PAGE_REF.findall(cited_in)} & retrieved_pages

    citations: list[Citation] = []
    seen: set[int] = set()
    for chunk in chunks:
        if chunk.page in seen or (wanted and chunk.page not in wanted):
            continue
        seen.add(chunk.page)
        snippet = chunk.text[:SNIPPET_LENGTH]
        if len(chunk.text) > SNIPPET_LENGTH:
            snippet = snippet.rstrip() + "…"
        citations.append(Citation(page=chunk.page, snippet=snippet))
    return citations
