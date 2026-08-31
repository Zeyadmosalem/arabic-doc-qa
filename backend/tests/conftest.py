from collections.abc import Callable

import pymupdf
import pytest


@pytest.fixture
def make_pdf() -> Callable[[list[str]], bytes]:
    """Build a small PDF in memory, one page per string. ASCII only.

    The built-in PDF fonts cannot shape Arabic, so PDF fixtures here are
    English. Arabic behaviour is covered by testing the text functions
    directly, which is where the Arabic handling actually lives.
    """

    def build(pages: list[str]) -> bytes:
        document = pymupdf.open()
        for text in pages:
            page = document.new_page()
            if text:
                page.insert_text((72, 72), text, fontsize=12)
        return document.tobytes()

    return build


@pytest.fixture
def two_page_pdf(make_pdf: Callable[[list[str]], bytes]) -> bytes:
    return make_pdf(["Alpha on the first page.", "Bravo on the second page."])
