from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from src.utils.config import RAW_DIR, PROJECT_ROOT
from src.utils.logging import setup_logging
import logging


logger = logging.getLogger("scrape_pdfs")


def is_pdf_url(url: str) -> bool:
    return url.lower().endswith(".pdf")


def sanitize_filename(name: str) -> str:
    name = re.sub(r"[^\w\-\.]+", "_", name)
    return name[:200]


def download_pdf(url: str, output_dir: Path, session: requests.Session) -> Path:
    response = session.get(url, timeout=30)
    response.raise_for_status()

    parsed = urlparse(url)
    filename = sanitize_filename(Path(parsed.path).name or "document.pdf")
    if not filename.lower().endswith(".pdf"):
        filename += ".pdf"

    output_path = output_dir / filename
    output_path.write_bytes(response.content)
    return output_path


def extract_pdf_links(page_url: str, session: requests.Session) -> set[str]:
    response = session.get(page_url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    links = set()
    for link in soup.find_all("a", href=True):
        href = link["href"]
        full_url = urljoin(page_url, href)
        if is_pdf_url(full_url):
            links.add(full_url)
    return links


def load_seed_urls(seed_file: Path) -> list[str]:
    urls = []
    for line in seed_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        urls.append(line)
    return urls


def main() -> None:
    setup_logging()
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    seed_file = PROJECT_ROOT / "data" / "seed_urls.txt"
    if not seed_file.exists():
        raise FileNotFoundError("data/seed_urls.txt not found")

    seed_urls = load_seed_urls(seed_file)
    if not seed_urls:
        raise ValueError("No seed URLs found in data/seed_urls.txt")

    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (RAG-Assignment; +https://example.com)",
            "Accept": "text/html,application/pdf",
        }
    )

    manifest = []
    for url in seed_urls:
        try:
            if is_pdf_url(url):
                pdf_urls = {url}
            else:
                logger.info("Scanning %s", url)
                pdf_urls = extract_pdf_links(url, session)
        except Exception as exc:
            logger.warning("Failed to scan %s (%s)", url, exc)
            continue

        for pdf_url in sorted(pdf_urls):
            try:
                logger.info("Downloading %s", pdf_url)
                output_path = download_pdf(pdf_url, RAW_DIR, session)
                manifest.append(
                    {
                        "source_url": pdf_url,
                        "filename": output_path.name,
                    }
                )
            except Exception as exc:
                logger.warning("Failed to download %s (%s)", pdf_url, exc)
                continue

    manifest_path = RAW_DIR / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    logger.info("Saved manifest to %s", manifest_path)


if __name__ == "__main__":
    main()
