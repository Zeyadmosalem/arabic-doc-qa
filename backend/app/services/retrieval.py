"""Finding the chunks that answer a question, and writing the answer."""

from app.models import Answer, Chunk


def search(query: str, top_k: int) -> list[Chunk]:
    """Find the chunks most similar to a question.

    Args:
        query: The user's question, in Arabic or English.
        top_k: How many chunks to return.

    Returns:
        Up to top_k chunks ordered by descending similarity, each with its
        score and source page set.
    """
    raise NotImplementedError


def answer(question: str, chunks: list[Chunk]) -> Answer:
    """Ask the Groq model to answer a question from the retrieved chunks.

    Args:
        question: The user's question, in Arabic or English.
        chunks: The chunks retrieved by search, used as the only context.

    Returns:
        An Answer in the language of the question, with a citation for each
        page it drew on.
    """
    raise NotImplementedError
