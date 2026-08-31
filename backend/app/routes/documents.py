from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.config import settings
from app.models import UploadResponse
from app.services.ingest import chunk_pages, extract_pages, upsert_chunks

router = APIRouter(tags=["documents"])

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


@router.post("/upload", response_model=UploadResponse)
async def upload_document(file: Annotated[UploadFile, File()]) -> UploadResponse:
    """Accept a PDF, extract its pages, chunk them and index the chunks in Qdrant."""
    filename = file.filename or "document.pdf"
    if not filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="only PDF files are supported")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="PDF is larger than 25 MB")

    try:
        pages = extract_pages(pdf_bytes)
    except Exception as error:  # pymupdf raises a variety of parse errors
        raise HTTPException(status_code=400, detail="could not read this PDF") from error

    if len(pages) > settings.max_pages:
        raise HTTPException(
            status_code=422,
            detail=(
                f"this PDF has {len(pages)} pages; v1 indexes up to "
                f"{settings.max_pages}"
            ),
        )

    if not any(page.text.strip() for page in pages):
        raise HTTPException(
            status_code=422,
            detail="no text could be extracted — this looks like a scanned PDF, which needs OCR",
        )

    document_id = str(uuid4())
    chunks = chunk_pages(pages, document_id=document_id)
    upsert_chunks(chunks)

    return UploadResponse(
        document_id=document_id,
        filename=filename,
        pages=len(pages),
        chunks=len(chunks),
    )
