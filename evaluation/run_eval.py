"""Run the evaluation set against a deployed or local API and print a table.

    python evaluation/run_eval.py --api https://arabic-doc-qa-api.vercel.app

Uploads the document once, asks every question, and grades each answer on three
independent things: whether the expected fact appears, whether it cites the page
that fact is actually on, and whether it is written in the language it was asked
in. A right answer citing the wrong page is not a pass — the citation is the
product.
"""

import argparse
import json
import re
import sys
import time
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]

# Phrases the model uses when it declines to answer. Checked in both languages
# because the prompt makes it answer in the language it was asked in.
REFUSALS = [
    "does not",
    "not provide",
    "no information",
    "not mention",
    "not contain",
    "cannot",
    "لا يحتوي",
    "لا يذكر",
    "لا توجد",
    "لا يوجد",
    "غير متوفر",
    "لم يذكر",
    "لا تتوفر",
    "لا يمكنني",
    "لا يمكن",
    "غير مذكور",
    "غير متوفرة",
]

ARABIC_DIGITS = {ord("٠") + i: str(i) for i in range(10)}
ARABIC_LETTERS = re.compile(r"[؀-ۿ]")
LATIN_LETTERS = re.compile(r"[A-Za-z]")


def flatten(text: str) -> str:
    """Lowercase, map Arabic-Indic digits, and drop separators inside numbers.

    The model may write 7,009,120 or 7.009.120 or ٧٠٠٩١٢٠ for the same figure.
    """
    text = text.translate(ARABIC_DIGITS).lower()
    return re.sub(r"(?<=\d)[,.٫٬\s](?=\d)", "", text)


def answered_in(language: str, answer: str) -> bool:
    """Whether the answer is written in the language it was asked in.

    Graded separately because the failure is easy to miss: an answer can be
    correct, cite the right page, and still come back in the wrong language.
    """
    arabic = len(ARABIC_LETTERS.findall(answer))
    latin = len(LATIN_LETTERS.findall(answer))
    return arabic > latin if language == "ar" else latin > arabic


def looks_like_refusal(answer: str) -> bool:
    lowered = answer.lower()
    return any(phrase.lower() in lowered for phrase in REFUSALS)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", default="http://127.0.0.1:8000")
    parser.add_argument("--out", default=str(Path(__file__).parent / "results.md"))
    args = parser.parse_args()
    api = args.api.rstrip("/")

    spec = json.loads((Path(__file__).parent / "questions.json").read_text(encoding="utf-8"))
    pdf = ROOT / spec["document"]
    if not pdf.exists():
        print(f"missing document: {pdf}", file=sys.stderr)
        return 1

    print(f"uploading {pdf.name} to {api}")
    started = time.time()
    with pdf.open("rb") as handle:
        upload = httpx.post(
            f"{api}/upload",
            files={"file": (pdf.name, handle, "application/pdf")},
            timeout=300,
        )
    upload.raise_for_status()
    document = upload.json()
    print(
        f"  indexed {document['pages']} pages, {document['chunks']} chunks "
        f"in {time.time() - started:.1f}s\n"
    )

    rows, passed = [], 0
    for question in spec["questions"]:
        started = time.time()
        response = httpx.post(
            f"{api}/ask",
            json={"question": question["question"], "document_id": document["document_id"]},
            timeout=120,
        )
        elapsed = time.time() - started
        response.raise_for_status()
        answer = response.json()
        text, cited = answer["text"], [c["page"] for c in answer["citations"]]

        if question.get("expect_refusal"):
            fact_ok = page_ok = looks_like_refusal(text)
            expected = "declines to answer"
        else:
            flat = flatten(text)
            fact_ok = any(flatten(candidate) in flat for candidate in question["expect_any"])
            page_ok = bool(set(cited) & set(question["expect_pages"]))
            expected = f"{question['expect_any'][0]} on p.{question['expect_pages'][0]}"

        lang_ok = answered_in(question["language"], text)
        ok = fact_ok and page_ok and lang_ok
        passed += ok
        rows.append(
            {
                "id": question["id"],
                "lang": question["language"],
                "question": question["question"],
                "expected": expected,
                "answer": " ".join(text.split()),
                "cited": cited,
                "fact_ok": fact_ok,
                "page_ok": page_ok,
                "lang_ok": lang_ok,
                "ok": ok,
                "seconds": round(elapsed, 2),
            }
        )
        mark = "PASS" if ok else "FAIL"
        print(
            f"  [{mark}] {question['id']:5} fact={fact_ok!s:5} page={page_ok!s:5} "
            f"lang={lang_ok!s:5} {elapsed:5.2f}s"
        )

    lines = [
        "# Evaluation results",
        "",
        (
            f"Document: `{spec['document']}` — {document['pages']} pages, "
            f"{document['chunks']} chunks."
        ),
        "",
        (
            f"**{passed}/{len(rows)} correct.** A question passes only if the answer "
            "contains the expected fact, cites the page that fact is on, and is "
            "written in the language it was asked in."
        ),
        "",
        "| # | Lang | Question | Expected | Fact | Page | Lang | Cited | Time |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    tick = {True: "yes", False: "no"}
    for row in rows:
        lines.append(
            f"| {row['id']} | {row['lang']} | {row['question']} | {row['expected']} "
            f"| {tick[row['fact_ok']]} | {tick[row['page_ok']]} | {tick[row['lang_ok']]} "
            f"| {row['cited'] or '—'} | {row['seconds']}s |"
        )
    lines += ["", "## Answers", ""]
    for row in rows:
        lines += [f"**{row['id']}** — {row['question']}", "", f"> {row['answer']}", ""]

    Path(args.out).write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"\n{passed}/{len(rows)} correct — written to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
