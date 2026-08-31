from fastapi.testclient import TestClient

from app.config import settings
from app.main import app
from app.models import Answer, Chunk, Citation

client = TestClient(app)


def a_chunk(page: int = 3, text: str = "the relevant passage") -> Chunk:
    return Chunk(id="c1", text=text, page=page, document_id="doc", score=0.9)


class TestUpload:
    def test_indexes_a_pdf_and_reports_what_it_stored(self, two_page_pdf, monkeypatch):
        stored: list[Chunk] = []
        monkeypatch.setattr("app.routes.documents.upsert_chunks", stored.extend)

        response = client.post(
            "/upload",
            files={"file": ("doc.pdf", two_page_pdf, "application/pdf")},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["pages"] == 2
        assert body["chunks"] == len(stored)
        assert body["chunks"] > 0
        assert body["filename"] == "doc.pdf"
        assert body["document_id"]
        assert {chunk.page for chunk in stored} == {1, 2}

    def test_rejects_a_file_that_is_not_a_pdf(self, monkeypatch):
        monkeypatch.setattr("app.routes.documents.upsert_chunks", lambda chunks: None)

        response = client.post("/upload", files={"file": ("notes.txt", b"hello", "text/plain")})

        assert response.status_code == 400

    def test_rejects_a_scanned_pdf_with_no_extractable_text(self, make_pdf, monkeypatch):
        monkeypatch.setattr("app.routes.documents.upsert_chunks", lambda chunks: None)

        response = client.post(
            "/upload",
            files={"file": ("scan.pdf", make_pdf(["", ""]), "application/pdf")},
        )

        assert response.status_code == 422
        assert "OCR" in response.json()["detail"]

    def test_rejects_a_pdf_it_cannot_parse(self, monkeypatch):
        monkeypatch.setattr("app.routes.documents.upsert_chunks", lambda chunks: None)

        response = client.post(
            "/upload",
            files={"file": ("broken.pdf", b"not really a pdf", "application/pdf")},
        )

        assert response.status_code == 400


class TestAsk:
    def test_returns_the_answer_with_page_citations(self, monkeypatch):
        monkeypatch.setattr(settings, "groq_api_key", "test-key")
        calls = {}

        def fake_search(query, top_k, *, document_id=None):
            calls.update(query=query, top_k=top_k, document_id=document_id)
            return [a_chunk()]

        def fake_answer(question, chunks):
            return Answer(
                text="The deadline is 30 days (p. 3).",
                citations=[Citation(page=chunks[0].page, snippet=chunks[0].text)],
            )

        monkeypatch.setattr("app.routes.qa.search", fake_search)
        monkeypatch.setattr("app.routes.qa.answer", fake_answer)

        response = client.post(
            "/ask",
            json={"question": "What is the deadline?", "document_id": "doc"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["citations"] == [{"page": 3, "snippet": "the relevant passage"}]
        assert calls == {"query": "What is the deadline?", "top_k": 5, "document_id": "doc"}

    def test_reports_503_when_no_groq_key_is_configured(self, monkeypatch):
        monkeypatch.setattr(settings, "groq_api_key", "")

        response = client.post("/ask", json={"question": "anything", "document_id": "doc"})

        assert response.status_code == 503

    def test_reports_404_when_the_document_has_nothing_indexed(self, monkeypatch):
        monkeypatch.setattr(settings, "groq_api_key", "test-key")
        monkeypatch.setattr("app.routes.qa.search", lambda *args, **kwargs: [])

        response = client.post("/ask", json={"question": "anything", "document_id": "missing"})

        assert response.status_code == 404

    def test_rejects_an_empty_question(self, monkeypatch):
        monkeypatch.setattr(settings, "groq_api_key", "test-key")

        response = client.post("/ask", json={"question": "", "document_id": "doc"})

        assert response.status_code == 422
