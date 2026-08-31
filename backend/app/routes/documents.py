from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["documents"])


@router.post("/upload")
def upload_document() -> None:
    """Accept a PDF, extract its pages, chunk them and index the chunks in Qdrant."""
    raise HTTPException(status_code=501, detail="upload is not implemented yet")
