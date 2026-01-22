from __future__ import annotations


def chunk_text(
    text: str,
    chunk_words: int,
    overlap: int,
) -> list[str]:
    words = text.split()
    if not words:
        return []

    chunks: list[str] = []
    start = 0
    step = max(chunk_words - overlap, 1)
    while start < len(words):
        end = min(start + chunk_words, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start += step

    return chunks
