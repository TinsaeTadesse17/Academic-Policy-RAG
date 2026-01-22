from __future__ import annotations

import json
import math
import time
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


def load_chunks(chunks_path: Path) -> list[dict]:
    chunks: list[dict] = []
    with chunks_path.open("r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            chunks.append(json.loads(line))
    return chunks


def wait_for_qdrant(store: VectorStore, retries: int = 20, delay: float = 3.0) -> None:
    last_error: Exception | None = None
    for _ in range(retries):
        try:
            store.client.get_collections()
            return
        except Exception as exc:
            last_error = exc
            time.sleep(delay)
    if last_error:
        raise last_error


def main() -> None:
    setup_logging()
    settings = load_settings()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = list(RAW_DIR.glob("*.pdf"))
    if not pdf_files:
        raise FileNotFoundError("No PDFs found in data/raw")

    output_path = PROCESSED_DIR / "chunks.jsonl"
    if output_path.exists():
        all_chunks = load_chunks(output_path)
    else:
        all_chunks: list[dict] = []
        for pdf_path in pdf_files:
            all_chunks.extend(build_chunks(pdf_path, settings.chunk_words, settings.chunk_overlap))

        with output_path.open("w", encoding="utf-8") as f:
            for item in all_chunks:
                f.write(json.dumps(item, ensure_ascii=True) + "\n")

    if not all_chunks:
        raise ValueError("No chunks produced from PDFs")

    embedder = EmbeddingModel(settings.embedding_model)
    store = VectorStore(settings.qdrant_url, settings.qdrant_collection)
    wait_for_qdrant(store)

    checkpoint_path = PROCESSED_DIR / "index_checkpoint.json"
    if checkpoint_path.exists():
        checkpoint = json.loads(checkpoint_path.read_text(encoding="utf-8"))
        start_batch = int(checkpoint.get("last_completed_batch", 0))
    else:
        start_batch = 0

    batch_size = 32
    total_batches = math.ceil(len(all_chunks) / batch_size)

    sample_vector = embedder.encode([all_chunks[0]["text"]])[0]
    store.ensure_collection(vector_size=len(sample_vector))

    for batch_idx in tqdm(range(start_batch, total_batches), desc="Indexing batches"):
        start = batch_idx * batch_size
        end = min(start + batch_size, len(all_chunks))
        batch = all_chunks[start:end]

        vectors = embedder.encode([item["text"] for item in batch])
        ids = list(range(start + 1, end + 1))
        for attempt in range(3):
            try:
                store.upsert(ids=ids, vectors=vectors, payloads=batch)
                break
            except Exception:
                if attempt == 2:
                    raise
                time.sleep(2)

        checkpoint_path.write_text(
            json.dumps(
                {
                    "last_completed_batch": batch_idx + 1,
                    "total_batches": total_batches,
                },
                indent=2,
            ),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
