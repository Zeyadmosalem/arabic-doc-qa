from fastapi import APIRouter, HTTPException

from app.config import settings
from app.models import Answer, AskRequest
from app.services.retrieval import answer, search

router = APIRouter(tags=["qa"])


@router.post("/ask", response_model=Answer)
def ask_question(request: AskRequest) -> Answer:
    """Answer a question about an indexed document, with page citations."""
    if not settings.groq_api_key:
        raise HTTPException(status_code=503, detail="GROQ_API_KEY is not configured")

    chunks = search(request.question, request.top_k, document_id=request.document_id)
    if not chunks:
        raise HTTPException(status_code=404, detail="no indexed content for this document")

    return answer(request.question, chunks)
