from pathlib import Path

import fitz


def parse_pdf(pdf_path: Path) -> list[dict[str, object]]:
    pages: list[dict[str, object]] = []

    with fitz.open(pdf_path) as document:
        for page_index, page in enumerate(document, start=1):
            text = page.get_text("text").strip()
            pages.append(
                {
                    "page_number": page_index,
                    "text": text,
                }
            )

    return pages
