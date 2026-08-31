from app.models import Chunk
from app.services.retrieval import SNIPPET_LENGTH, _citations


def chunk(page: int, text: str = "some text") -> Chunk:
    return Chunk(id=f"c{page}", text=text, page=page, document_id="doc", score=0.8)


class TestCitations:
    def test_keeps_only_the_pages_the_model_cited(self):
        chunks = [chunk(10), chunk(8), chunk(1), chunk(4)]

        citations = _citations(chunks, cited_in="19 methods (p. 1).")

        assert [c.page for c in citations] == [1]

    def test_keeps_every_page_when_the_model_cites_several(self):
        chunks = [chunk(10), chunk(8), chunk(1)]

        citations = _citations(chunks, cited_in="see (p. 10, p. 1)")

        assert [c.page for c in citations] == [10, 1]

    def test_falls_back_to_all_retrieved_pages_when_the_model_cites_none(self):
        chunks = [chunk(3), chunk(7)]

        citations = _citations(chunks, cited_in="a bare answer with no page refs")

        assert [c.page for c in citations] == [3, 7]

    def test_ignores_a_page_the_model_invented(self):
        chunks = [chunk(2), chunk(5)]

        citations = _citations(chunks, cited_in="according to (p. 99) and (p. 5)")

        assert [c.page for c in citations] == [5]

    def test_falls_back_when_every_cited_page_was_invented(self):
        chunks = [chunk(2), chunk(5)]

        citations = _citations(chunks, cited_in="see (p. 99)")

        assert [c.page for c in citations] == [2, 5]

    def test_reports_each_page_once_even_with_several_chunks_from_it(self):
        chunks = [chunk(4, "first"), chunk(4, "second"), chunk(9)]

        citations = _citations(chunks, cited_in="(p. 4) and (p. 9)")

        assert [c.page for c in citations] == [4, 9]
        assert citations[0].snippet == "first"

    def test_truncates_long_snippets(self):
        citations = _citations([chunk(1, "x" * 500)], cited_in="(p. 1)")

        assert citations[0].snippet.endswith("…")
        assert len(citations[0].snippet) == SNIPPET_LENGTH + 1
