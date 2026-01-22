from __future__ import annotations

from pathlib import Path
import fitz


def extract_pdf_pages(pdf_path: Path) -> list[dict]:
    pages: list[dict] = []
    with fitz.open(pdf_path) as doc:
        for page_idx in range(len(doc)):
            page = doc.load_page(page_idx)
            text = page.get_text("text")
            pages.append(
                {
                    "page_number": page_idx + 1,
                    "text": text,
                }
            )
    return pages
