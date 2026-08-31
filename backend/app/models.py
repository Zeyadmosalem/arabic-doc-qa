from pydantic import BaseModel


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
