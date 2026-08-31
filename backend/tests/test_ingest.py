from app.models import Page
from app.services.ingest import CHUNK_SIZE, chunk_pages, extract_pages, normalize_arabic


class TestExtractPages:
    def test_returns_one_page_per_pdf_page_numbered_from_one(self, two_page_pdf: bytes):
        pages = extract_pages(two_page_pdf)

        assert [page.number for page in pages] == [1, 2]
        assert "Alpha" in pages[0].text
        assert "Bravo" in pages[1].text

    def test_pages_with_no_text_come_back_empty_rather_than_missing(self, make_pdf):
        pages = extract_pages(make_pdf(["", ""]))

        assert len(pages) == 2
        assert all(not page.text.strip() for page in pages)


class TestNormalizeArabic:
    def test_strips_diacritics(self):
        assert normalize_arabic("مُحَمَّدٌ") == "محمد"

    def test_folds_alef_variants_onto_bare_alef(self):
        assert normalize_arabic("أحمد إسلام آمن") == "احمد اسلام امن"

    def test_strips_tatweel(self):
        assert normalize_arabic("مـــحـــمـــد") == "محمد"

    def test_folds_alef_maqsura_onto_yeh(self):
        assert normalize_arabic("على") == "علي"

    def test_maps_arabic_indic_digits_to_ascii(self):
        assert normalize_arabic("١٢٣ ٤٥٦") == "123 456"

    def test_collapses_whitespace(self):
        assert normalize_arabic("  hello   world \n there ") == "hello world there"

    def test_leaves_english_words_alone(self):
        assert normalize_arabic("Invoice Total 2024") == "Invoice Total 2024"

    def test_does_not_eat_digits_that_sit_near_the_diacritic_block(self):
        # Arabic-Indic digits live just past the tashkeel range; a sloppy
        # regex range swallows them.
        assert normalize_arabic("رقم ١٠") == "رقم 10"


class TestChunkPages:
    def test_short_page_becomes_a_single_chunk_citing_that_page(self):
        chunks = chunk_pages([Page(number=7, text="a short page")], document_id="doc")

        assert len(chunks) == 1
        assert chunks[0].page == 7
        assert chunks[0].document_id == "doc"
        assert chunks[0].text == "a short page"

    def test_long_page_splits_into_several_chunks_all_citing_the_same_page(self):
        page = Page(number=2, text=" ".join(["word"] * 1200))

        chunks = chunk_pages([page], document_id="doc")

        assert len(chunks) > 1
        assert {chunk.page for chunk in chunks} == {2}
        assert all(len(chunk.text) <= CHUNK_SIZE for chunk in chunks)

    def test_chunks_never_span_two_pages(self):
        pages = [Page(number=1, text="alpha"), Page(number=2, text="bravo")]

        chunks = chunk_pages(pages, document_id="doc")

        assert [(chunk.page, chunk.text) for chunk in chunks] == [(1, "alpha"), (2, "bravo")]

    def test_blank_pages_produce_no_chunks(self):
        chunks = chunk_pages([Page(number=1, text="   \n  ")], document_id="doc")

        assert chunks == []

    def test_ids_are_stable_so_reingesting_overwrites_instead_of_duplicating(self):
        page = Page(number=1, text="repeatable content")

        first = chunk_pages([page], document_id="doc")
        second = chunk_pages([page], document_id="doc")

        assert [chunk.id for chunk in first] == [chunk.id for chunk in second]

    def test_different_documents_get_different_ids_for_the_same_text(self):
        page = Page(number=1, text="repeatable content")

        assert chunk_pages([page], document_id="a")[0].id != (
            chunk_pages([page], document_id="b")[0].id
        )
