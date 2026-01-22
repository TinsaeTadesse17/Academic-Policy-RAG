from __future__ import annotations

import json
from pathlib import Path

from tqdm import tqdm

from src.utils.config import RAW_DIR, PROCESSED_DIR, load_settings
from src.utils.logging import setup_logging
from src.ingestion.pdf_loader import extract_pdf_pages
from src.ingestion.cleaner import normalize_text
from src.ingestion.chunker import chunk_text
from src.retrieval.embeddings import EmbeddingModel
from src.retrieval.vector_store import VectorStore


def build_chunks(pdf_path: Path, chunk_words: int, overlap: int) -> list[dict]:
    pages = extract_pdf_pages(pdf_path)
    chunks = []
    for page in pages:
        text = normalize_text(page["text"])
        for chunk_idx, chunk in enumerate(chunk_text(text, chunk_words, overlap)):
            chunks.append(
                {
                    "text": chunk,
                    "source_pdf": pdf_path.name,
                    "page_number": page["page_number"],
                    "chunk_id": f"{pdf_path.stem}_p{page['page_number']}_c{chunk_idx}",
                }
            )
    return chunks


def main() -> None:
    setup_logging()
    settings = load_settings()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = list(RAW_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError("No PDFs found in data/raw")

    all_chunks: list[dict] = []
    for pdf_path in pdf_files:
        all_chunks.extend(build_chunks(pdf_path, settings.chunk_words, settings.chunk_overlap))

    output_path = PROCESSED_DIR / "chunks.jsonl"
    with output_path.open("w", encoding="utf-8") as f:
        for item in all_chunks:
            f.write(json.dumps(item, ensure_ascii=True) + "\n")

    embedder = EmbeddingModel(settings.embedding_model)
    vectors = embedder.encode([item["text"] for item in tqdm(all_chunks, desc="Embedding")])

    store = VectorStore(settings.qdrant_url, settings.qdrant_collection)
    store.ensure_collection(vector_size=len(vectors[0]))

    ids = list(range(1, len(all_chunks) + 1))
    store.upsert(ids=ids, vectors=vectors, payloads=all_chunks)


if __name__ == "__main__":
    main()
