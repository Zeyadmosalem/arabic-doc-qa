from fastapi import APIRouter, HTTPException

router = APIRouter(tags=["qa"])


@router.post("/ask")
def ask_question() -> None:
    """Answer a question about an indexed document, with page citations."""
    raise HTTPException(status_code=501, detail="ask is not implemented yet")
