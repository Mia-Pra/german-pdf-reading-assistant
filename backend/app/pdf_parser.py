from pathlib import Path

import fitz


def split_paragraphs(text: str) -> list[dict[str, str | int]]:
    parts = [part.strip() for part in text.split("\n\n") if part.strip()]
    if not parts and text.strip():
        parts = [line.strip() for line in text.splitlines() if line.strip()]

    return [
        {
            "paragraph_id": index,
            "text": paragraph,
        }
        for index, paragraph in enumerate(parts, start=1)
    ]


def parse_pdf(pdf_path: Path) -> list[dict[str, object]]:
    pages: list[dict[str, object]] = []

    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            pages.append(
                {
                    "page_number": page_index,
                    "text": text,
                    "paragraphs": split_paragraphs(text),
                }
            )

    return pages
