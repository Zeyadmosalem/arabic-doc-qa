from pydantic import BaseModel, Field


class Page(BaseModel):
    """One page of extracted PDF text."""

    number: int
    text: str


class Chunk(BaseModel):
    """A retrievable slice of a document, tracked back to the page it came from."""

    id: str
    text: str
    page: int
    document_id: str
    score: float | None = None


class Citation(BaseModel):
    """A page the answer draws on."""

    page: int
    snippet: str


class Answer(BaseModel):
    """A generated answer plus the pages it is grounded in."""

    text: str
    citations: list[Citation]


class UploadResponse(BaseModel):
    """What /upload hands back so the client can ask about the document."""

    document_id: str
    filename: str
    pages: int
    chunks: int


class AskRequest(BaseModel):
    """A question about one previously uploaded document."""

    question: str = Field(min_length=1)
    document_id: str = Field(min_length=1)
    top_k: int = Field(default=5, ge=1, le=20)
